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
  name         = "insta_downloader"
  runtime      = "python38"
  entry_point  = "insta_downloader"
  trigger_http = true
  timeout      = 540
  region       = local.gcs_region

  source_archive_bucket = google_storage_bucket.deployer.name
  source_archive_object = google_storage_bucket_object.insta_downloader.name

  environment_variables = {
    GCP_REGION   = local.gcs_region
    BUCKET_NAME  = google_storage_bucket.raw_videos.name
    SLACK_URL    = var.slack_insta_url
    ENVIRONMENT  = var.workspace
    SLACK_SECRET = var.slack_secret
  }
  depends_on = [google_storage_bucket_object.raw_videos, google_service_account.cloud_function_invoker_account]
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
  name         = "pusher"
  runtime      = "python38"
  entry_point  = "pusher"
  trigger_http = true
  timeout      = 540
  region       = local.gcs_region

  source_archive_bucket = google_storage_bucket.deployer.name
  source_archive_object = google_storage_bucket_object.pusher.name

  environment_variables = {
    GCP_REGION   = local.gcs_region
    SLACK_URL    = var.slack_insta_url
    ENVIRONMENT  = var.workspace
    SLACK_SECRET = var.slack_secret
    PROJECT_ID   = var.project_name
    TOPIC_ID     = google_pubsub_topic.insta_download_jobs.name
  }
  depends_on = [google_service_account.cloud_function_invoker_account, google_pubsub_topic.insta_download_jobs]
}
