terraform {
  backend "remote" {
    hostname     = "app.terraform.io"
    organization = "fiebel"

    workspaces {
      prefix = "video-"
    }
  }

  required_providers {
    google      = {}
    google-beta = {}
  }

}

provider "google" {
  project = local.project_name
  region  = local.gcs_region
  zone    = "${local.gcs_region}-${var.gcs_zone}"
}

provider "google-beta" {
  project = local.project_name
  region  = local.gcs_region
  zone    = "${local.gcs_region}-${var.gcs_zone}"
}

resource "google_project_service" "service" {
  for_each = toset([
    "appengine.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "cloudbuild.googleapis.com",
    "cloudkms.googleapis.com",
    "firestore.googleapis.com",
    "iam.googleapis.com",
    "transcoder.googleapis.com",
    "cloudfunctions.googleapis.com",
    "containerregistry.googleapis.com",
    "pubsub.googleapis.com",
    "run.googleapis.com",
  ])

  service = each.key

  disable_on_destroy = false
}
