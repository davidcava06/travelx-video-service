resource "google_cloud_run_service" "api" {
  name     = "${var.workspace}-tiktok-api"
  location = local.gcs_region

  template {
    spec {
      containers {
        image = "europe-west2-docker.pkg.dev/${google_artifact_registry_repository.app_registry.project}/${google_artifact_registry_repository.app_registry.repository_id}/tiktok-api:2022-04-08_49_8f480fd"
        resources {
          limits = {
            "cpu"    = "1000m"  //explicit
            "memory" = "3072Mi" //explicit
          }
        }
        env {
          name  = "GCP_PROJECT"
          value = local.project_name
        }
        env {
          name  = "ENVIRONMENT"
          value = var.workspace
        }
        command = ["/venv/bin/gunicorn"]
        args    = ["-c", "gunicorn.py", "-k", "uvicorn.workers.UvicornWorker", "main"]
      }
      timeout_seconds      = "30"
      service_account_name = google_service_account.tiktok_api.email
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "2"
        "run.googleapis.com/client-name"   = "terraform"
        "run.googleapis.com/launch-stage"  = "BETA"
      }
    }
  }
  autogenerate_revision_name = true

  lifecycle {
    ignore_changes = [
      template[0].spec[0].containers[0].image
    ]
  }
}
