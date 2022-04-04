resource "google_pubsub_topic" "dead_letter_topic" {
  project = local.project_name
  name    = "${var.workspace}-dead-letter"
}

resource "google_pubsub_topic" "transcoder_jobs" {
  project = local.project_name
  name    = "${var.workspace}-transcoder-jobs"
}

resource "google_pubsub_topic" "insta_download_jobs" {
  project = local.project_name
  name    = "${var.workspace}-insta-jobs"
}
