resource "google_storage_bucket" "videos" {
  name          = "${var.workspace}-raw-videos"
  location      = var.location
  force_destroy = false
  storage_class = "STANDARD"
  project       = local.project_name
  versioning {
    enabled = false
  }
}
