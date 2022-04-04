variable "workspace" {
  type = string
}

variable "project_names" {
  type = map(any)
  default = {
    nonprod = "fiebel-video-nonprod"
    prod    = "fiebel-video-prod"
  }
}

variable "location" {
  type    = string
  default = "EU"
}

variable "gcs_regions" {
  type = map(any)
  default = {
    nonprod = "europe-west2"
    prod    = "europe-west2"
  }
}

variable "gcs_zone" {
  type    = string
  default = "c"
}

variable "slack_secret" {
  type = string
}

variable "slack_insta_url" {
  type    = string
  default = "https://hooks.slack.com/services/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"
}

locals {
  project_name = lookup(var.project_names, var.workspace)
  gcs_region   = lookup(var.gcs_regions, var.workspace)
}
