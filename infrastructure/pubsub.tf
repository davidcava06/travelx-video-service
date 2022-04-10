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

resource "google_pubsub_topic" "dead_letter_topic" {
  project = local.project_name
  name    = "${var.workspace}-dead-letter"
}

resource "google_pubsub_topic" "tiktok_download_jobs" {
  project = local.project_name
  name    = "${var.workspace}-tiktok-jobs"
}

resource "google_pubsub_subscription" "tiktok_subscription" {
  name  = "${var.workspace}-tiktok-subscription"
  topic = google_pubsub_topic.tiktok_download_jobs.name

  ack_deadline_seconds = 10
  message_retention_duration = "604800s"
  retain_acked_messages      = true

  push_config {
    push_endpoint = "${google_cloud_run_service.api.url}/video"
  }

  oidc_token {
    audience              = google_cloud_run_service.api.0.status.0.url
    service_account_email = google_service_account.cloudrun_invoker_account.email
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.dead_letter_topic.id
    max_delivery_attempts = 10
  }

  depends_on = [
    google_cloud_run_service_iam_member.generate_invoker,
  ]
}
