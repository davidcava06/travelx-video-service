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

variable "slack_insta_url" {
  type    = string
  default = "https://hooks.slack.com/services/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"
}

variable "slack_secret" {
  type = string
}

variable "datalama_key" {
  type = string
}

variable "cf_account" {
  type        = string
  description = "Cloudflare account"
}

variable "cf_token" {
  type        = string
  description = "Cloudflare API Token for Stream"
}

variable "infura_project_id" {
  type = string
}

variable "infura_project_secret" {
  type = string
}

variable "experience_update_sheet_id" {
  type        = string
  description = "ID for Google Sheet to update experiences"
  default     = "1O36Ha4FjCGpbKr1rxPE7xi6sDztKPyy3CWllR691Fzg"
}

variable "media_transfer_sheet_id" {
  type        = string
  description = "ID for Google Sheet to transfer media"
  default     = "1O36Ha4FjCGpbKr1rxPE7xi6sDztKPyy3CWllR691Fzg"
}

locals {
  project_name = lookup(var.project_names, var.workspace)
  gcs_region   = lookup(var.gcs_regions, var.workspace)
}
