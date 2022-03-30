resource "google_storage_bucket" "videos" {
  name          = "raw-videos"
  location      = var.location
  force_destroy = false
  storage_class = "STANDARD"
  project       = var.project
  versioning {
    enabled = false
  }
}
