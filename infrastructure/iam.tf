resource "google_cloudfunctions_function_iam_binding" "pusher_invoker_binding" {
  project        = google_cloudfunctions_function.pusher.project
  region         = google_cloudfunctions_function.pusher.region
  cloud_function = google_cloudfunctions_function.pusher.name
  role           = "roles/cloudfunctions.invoker"
  members = [
    "allUsers",
  ]
}

resource "google_cloudfunctions_function_iam_member" "insta_downloader_invoker_member" {
  project        = google_cloudfunctions_function.insta_downloader.project
  region         = google_cloudfunctions_function.insta_downloader.region
  cloud_function = google_cloudfunctions_function.insta_downloader.name
  role           = "roles/cloudfunctions.invoker"
  member         = "serviceAccount:${google_service_account.cloud_function_invoker_account.email}"
}

resource "google_cloud_run_service_iam_member" "generate_invoker" {
  project  = google_cloud_run_service.api.project
  location = google_cloud_run_service.api.location
  service  = google_cloud_run_service.api.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.cloudrun_invoker_account.email}"
}

resource "google_project_iam_member" "transcoder_storage" {
  project = local.project_name
  role    = "roles/storage.object.admin"
  member  = "serviceAccount:service-395975539014@gcp-sa-transcoder.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "api_datastore" {
  project = local.project_name
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.tiktok_api.email}"
}
