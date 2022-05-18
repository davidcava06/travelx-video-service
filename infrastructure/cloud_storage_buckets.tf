resource "google_storage_bucket" "deployer" {
  name     = "${var.workspace}-deployer"
  location = "EU"
}

resource "google_storage_bucket" "raw_media" {
  name          = "${var.workspace}-raw-media"
  location      = var.location
  force_destroy = false
  storage_class = "STANDARD"
  project       = local.project_name
  versioning {
    enabled = false
  }
}

resource "google_storage_bucket" "transcoded_media" {
  name          = "${var.workspace}-transcoded-media"
  location      = var.location
  force_destroy = false
  storage_class = "STANDARD"
  project       = local.project_name
  versioning {
    enabled = false
  }
}

resource "google_storage_bucket" "guides_media" {
  name          = "${var.workspace}-guides-media"
  location      = var.location
  force_destroy = false
  storage_class = "STANDARD"
  project       = local.project_name
  versioning {
    enabled = false
  }
}
