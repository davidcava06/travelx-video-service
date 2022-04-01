# Function: Execute Transcoder Job
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
  name         = "transcoder"
  runtime      = "python38"
  entry_point  = "transcoder"
  trigger_http = true
  timeout      = 540
  region       = local.gcs_region

  source_archive_bucket = google_storage_bucket.deployer.name
  source_archive_object = google_storage_bucket_object.raw_videos.name

  environment_variables = {
    GCP_REGION  = local.gcs_region
    BUCKET_NAME = google_storage_bucket.processed_videos.name
    ENVIRONMENT = var.workspace
  }
  depends_on = [google_storage_bucket_object.raw_videos, google_service_account.cloud_function_invoker_account]
}
