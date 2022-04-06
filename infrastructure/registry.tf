resource "google_container_registry" "registry" {
  project  = local.project_name
  location = "EU"

  depends_on = [google_project_service.service]
}
