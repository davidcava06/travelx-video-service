resource "google_artifact_registry_repository" "app_registry" {
  provider = google-beta

  project       = local.project_name
  location      = local.gcs_region
  repository_id = "${var.workspace}-app-repository"
  format        = "DOCKER"
}
