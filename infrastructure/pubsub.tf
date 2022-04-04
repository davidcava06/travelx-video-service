resource "google_pubsub_topic" "dead_letter_topic" {
  project = local.project_name
  name    = "${var.workspace}-dead-letter"
}

resource "google_pubsub_topic" "transcoder_jobs" {
  project = local.project_name
  name    = "${var.workspace}-transcoder-jobs"

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.dead_letter_topic.id
    max_delivery_attempts = 10
  }
}

resource "google_pubsub_topic" "insta_download_jobs" {
  project = local.project_name
  name    = "${var.workspace}-insta-jobs"

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.dead_letter_topic.id
    max_delivery_attempts = 10
  }
}
