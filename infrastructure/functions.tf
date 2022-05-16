# Function: Execute Insta Downloads
#
data "local_file" "insta_downloader" {
  filename = "functions/insta_downloader.zip"
}

resource "google_storage_bucket_object" "insta_downloader" {
  name   = format("insta_downloader.zip#%s", md5(data.local_file.insta_downloader.content))
  bucket = google_storage_bucket.deployer.name
  source = data.local_file.insta_downloader.filename
}

resource "google_cloudfunctions_function" "insta_downloader" {
  name                = "insta_downloader"
  runtime             = "python38"
  entry_point         = "insta_downloader"
  available_memory_mb = 512
  timeout             = 300
  region              = local.gcs_region

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = google_pubsub_topic.insta_download_jobs.name
  }

  source_archive_bucket = google_storage_bucket.deployer.name
  source_archive_object = google_storage_bucket_object.insta_downloader.name
  service_account_email = google_service_account.cloud_function_invoker_account.email

  environment_variables = {
    BUCKET_NAME  = google_storage_bucket.raw_media.name
    SLACK_URL    = var.slack_insta_url
    PROJECT_ID   = local.project_name
    DATALAMA_KEY = var.datalama_key
    CF_ACCOUNT   = var.cf_account
    CF_TOKEN     = var.cf_token
    TOPIC_ID     = google_pubsub_topic.transcoder_jobs.name
    SHEET_ID     = var.experience_update_sheet_id
  }

  depends_on = [google_storage_bucket.raw_media, google_service_account.cloud_function_invoker_account]
}

# Function: Push task to PubSub
#
data "local_file" "pusher" {
  filename = "functions/pusher.zip"
}

resource "google_storage_bucket_object" "pusher" {
  name   = format("pusher.zip#%s", md5(data.local_file.pusher.content))
  bucket = google_storage_bucket.deployer.name
  source = data.local_file.pusher.filename
}

resource "google_cloudfunctions_function" "pusher" {
  name                = "pusher"
  runtime             = "python38"
  entry_point         = "pusher"
  trigger_http        = true
  ingress_settings    = "ALLOW_ALL"
  available_memory_mb = 128
  region              = local.gcs_region

  source_archive_bucket = google_storage_bucket.deployer.name
  source_archive_object = google_storage_bucket_object.pusher.name
  service_account_email = google_service_account.cloud_function_invoker_account.email

  environment_variables = {
    SLACK_SECRET      = var.slack_secret
    PROJECT_ID        = local.project_name
    INSTA_TOPIC_ID    = google_pubsub_topic.insta_download_jobs.name
    TIKTOK_TOPIC_ID   = google_pubsub_topic.tiktok_download_jobs.name
    UPDATE_TOPIC_ID   = google_pubsub_topic.experience_update_jobs.name
    MEDIA_TX_TOPIC_ID = google_pubsub_topic.media_transfer_jobs.name
  }
  depends_on = [google_service_account.cloud_function_invoker_account, google_pubsub_topic.insta_download_jobs, google_pubsub_topic.tiktok_download_jobs, google_pubsub_topic.experience_update_jobs, google_pubsub_topic.media_transfer_jobs]
}

# Function: Create transcode Jobs
#
data "local_file" "transcoder" {
  filename = "functions/transcoder.zip"
}

resource "google_storage_bucket_object" "transcoder" {
  name   = format("transcoder.zip#%s", md5(data.local_file.transcoder.content))
  bucket = google_storage_bucket.deployer.name
  source = data.local_file.transcoder.filename
}
resource "google_cloudfunctions_function" "transcoder" {
  name                = "transcoder"
  runtime             = "python38"
  entry_point         = "transcoder"
  available_memory_mb = 256
  region              = local.gcs_region

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = google_pubsub_topic.transcoder_jobs.name
  }

  source_archive_bucket = google_storage_bucket.deployer.name
  source_archive_object = google_storage_bucket_object.transcoder.name
  service_account_email = google_service_account.cloud_function_invoker_account.email

  environment_variables = {
    ENVIRONMENT        = var.workspace
    PROJECT_ID         = local.project_name
    LOCATION           = local.gcs_region
    INPUT_BUCKET_NAME  = google_storage_bucket.raw_media.name
    OUTPUT_BUCKET_NAME = google_storage_bucket.transcoded_media.name
    TOPIC_ID           = google_pubsub_topic.transcoder_done.name
  }
  depends_on = [google_storage_bucket.raw_media, google_storage_bucket.transcoded_media, google_service_account.cloud_function_invoker_account]
}

# Function: Formats the output of the transcoder and uploads to CDN
#
data "local_file" "cdn_uploader" {
  filename = "functions/cdn_uploader.zip"
}

resource "google_storage_bucket_object" "cdn_uploader" {
  name   = format("cdn_uploader.zip#%s", md5(data.local_file.cdn_uploader.content))
  bucket = google_storage_bucket.deployer.name
  source = data.local_file.cdn_uploader.filename
}
resource "google_cloudfunctions_function" "cdn_uploader" {
  name                = "cdn_uploader"
  runtime             = "python38"
  entry_point         = "cdn_uploader"
  available_memory_mb = 256
  region              = local.gcs_region

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = google_pubsub_topic.transcoder_done.name
  }

  source_archive_bucket = google_storage_bucket.deployer.name
  source_archive_object = google_storage_bucket_object.cdn_uploader.name
  service_account_email = google_service_account.cloud_function_invoker_account.email

  environment_variables = {
    ENVIRONMENT            = var.workspace
    PROJECT_ID             = local.project_name
    LOCATION               = local.gcs_region
    TRANSCODED_BUCKET_NAME = google_storage_bucket.transcoded_media.name
    INFURA_PROJECT_ID      = var.infura_project_id
    INFURA_PROJECT_SECRET  = var.infura_project_secret
  }
  depends_on = [google_storage_bucket.transcoded_media, google_service_account.cloud_function_invoker_account]
}

# Function: Takes the rows of a Google Sheet and update Experiences and Media Experience Summaries
#
data "local_file" "experience_updater" {
  filename = "functions/experience_updater.zip"
}

resource "google_storage_bucket_object" "experience_updater" {
  name   = format("experience_updater.zip#%s", md5(data.local_file.experience_updater.content))
  bucket = google_storage_bucket.deployer.name
  source = data.local_file.experience_updater.filename
}
resource "google_cloudfunctions_function" "experience_updater" {
  name                = "experience_updater"
  runtime             = "python38"
  entry_point         = "experience_updater"
  available_memory_mb = 256
  region              = local.gcs_region
  timeout             = 300

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = google_pubsub_topic.experience_update_jobs.name
  }

  source_archive_bucket = google_storage_bucket.deployer.name
  source_archive_object = google_storage_bucket_object.experience_updater.name
  service_account_email = google_service_account.cloud_function_invoker_account.email

  environment_variables = {
    ENVIRONMENT = var.workspace
    PROJECT_ID  = local.project_name
    LOCATION    = local.gcs_region
    SHEET_ID    = var.experience_update_sheet_id
  }
  depends_on = [google_service_account.cloud_function_invoker_account, google_pubsub_topic.experience_update_jobs]
}

# Function: Takes the rows of a Google Sheet and transfer media between experiences
#
data "local_file" "media_transfer" {
  filename = "functions/media_transfer.zip"
}

resource "google_storage_bucket_object" "media_transfer" {
  name   = format("media_transfer.zip#%s", md5(data.local_file.media_transfer.content))
  bucket = google_storage_bucket.deployer.name
  source = data.local_file.media_transfer.filename
}
resource "google_cloudfunctions_function" "media_transfer" {
  name                = "media_transfer"
  runtime             = "python38"
  entry_point         = "media_transfer"
  available_memory_mb = 256
  region              = local.gcs_region
  timeout             = 300

  event_trigger {
    event_type = "google.pubsub.topic.publish"
    resource   = google_pubsub_topic.media_transfer_jobs.name
  }

  source_archive_bucket = google_storage_bucket.deployer.name
  source_archive_object = google_storage_bucket_object.media_transfer.name
  service_account_email = google_service_account.cloud_function_invoker_account.email

  environment_variables = {
    ENVIRONMENT = var.workspace
    PROJECT_ID  = local.project_name
    LOCATION    = local.gcs_region
    SHEET_ID    = var.media_transfer_sheet_id
  }
  depends_on = [google_service_account.cloud_function_invoker_account, google_pubsub_topic.media_transfer_jobs]
}
