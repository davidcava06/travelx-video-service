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
    SLACK_SECRET = var.slack_secret
    PROJECT_ID   = local.project_name
    TOPIC_ID     = google_pubsub_topic.insta_download_jobs.name
  }
  depends_on = [google_service_account.cloud_function_invoker_account, google_pubsub_topic.insta_download_jobs]
}
