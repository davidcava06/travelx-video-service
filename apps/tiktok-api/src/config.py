import os

BASE_DIR = os.path.dirname(__file__)
ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "local")


class Config:
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    GCP_PROJECT: str = os.environ.get("GCP_PROJECT", "fiebel-video-nonprod")
    GCP_REGION: str = os.environ.get("GCP_REGION", "europe-west2")
    GCP_BUCKET: str = os.environ.get("GCP_BUCKET", "nonprod-raw-media")


class DevelopmentConfig(Config):
    DEBUG: str = True


class NonProductionConfig(Config):
    DEBUG: str = True
    TOPIC_ID: str = "nonprod-transcoder-jobs"


class ProductionConfig(Config):
    DEBUG: str = False
    TOPIC_ID: str = "prod-transcoder-jobs"


config = {
    "nonprod": NonProductionConfig,
    "prod": ProductionConfig,
    "default": DevelopmentConfig,
    "local": DevelopmentConfig,
}
