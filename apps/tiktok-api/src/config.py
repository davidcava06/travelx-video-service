import os

BASE_DIR = os.path.dirname(__file__)
ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "local")


class Config:
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    GCP_PROJECT: str = os.environ.get("GCP_PROJECT", "fiebel-video-nonprod")
    GCP_REGION: str = os.environ.get("GCP_REGION", "europe-west2")
    GCP_BUCKET: str = os.environ.get("GCP_BUCKET", "nonprod-raw-media")
    CF_ACCOUNT: str = os.environ.get("CF_ACCOUNT", "")
    CF_TOKEN: str = os.environ.get("CF_TOKEN", "")
    SHEET_ID = os.environ.get(
        "SHEET_ID", "1O36Ha4FjCGpbKr1rxPE7xi6sDztKPyy3CWllR691Fzg"
    )


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
