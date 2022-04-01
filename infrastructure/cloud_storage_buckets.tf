resource "google_storage_bucket" "deployer" {
  name     = "${var.workspace}-deployer"
  location = "EU"
}

resource "google_storage_bucket" "raw_videos" {
  name          = "${var.workspace}-raw-videos"
  location      = var.location
  force_destroy = false
  storage_class = "STANDARD"
  project       = local.project_name
  versioning {
    enabled = false
  }
}
