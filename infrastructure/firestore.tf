resource "google_app_engine_application" "app_engine" {
  project       = local.project_name
  location_id   = local.gcs_region
  database_type = "CLOUD_FIRESTORE"
}
