resource "google_service_account" "cloud_function_invoker_account" {
  project      = local.project_name
  account_id   = "${var.workspace}-cf-acc"
  display_name = "Cloud Function Invoker Service Account"
}
