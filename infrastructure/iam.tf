resource "google_pubsub_topic_iam_binding" "insta_jobs_publisher" {
  project = local.project_name
  topic   = google_pubsub_topic.insta_download_jobs.name
  role    = "roles/pubsub.publisher"
  members = [
    "serviceAccount:${google_service_account.cloud_function_invoker_account.email}",
  ]
}

resource "google_cloudfunctions_function_iam_binding" "pusher_invoker_binding" {
  project        = google_cloudfunctions_function.pusher.project
  region         = google_cloudfunctions_function.pusher.region
  cloud_function = google_cloudfunctions_function.pusher.name
  role           = "roles/cloudfunctions.invoker"
  members = [
    "allUsers",
  ]
}

resource "google_cloudfunctions_function_iam_binding" "insta_downloader_invoker_binding" {
  project        = google_cloudfunctions_function.insta_downloader.project
  region         = google_cloudfunctions_function.insta_downloader.region
  cloud_function = google_cloudfunctions_function.insta_downloader.name
  role           = "roles/cloudfunctions.invoker"
  members = [
    "serviceAccount:${google_service_account.cloud_function_invoker_account.email}",
  ]
}
