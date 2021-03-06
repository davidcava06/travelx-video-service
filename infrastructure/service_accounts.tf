resource "google_service_account" "cloud_function_invoker_account" {
  project      = local.project_name
  account_id   = "${var.workspace}-cf-acc"
  display_name = "Cloud Function Invoker Service Account"
}

resource "google_service_account" "tiktok_api" {
  account_id   = "${var.workspace}-tiktok-api"
  display_name = "TikTok API Service Account"
}

resource "google_service_account" "cloudrun_invoker_account" {
  project      = local.project_name
  account_id   = "${var.workspace}-cri-acc"
  display_name = "CloudRun Invoker"
}
