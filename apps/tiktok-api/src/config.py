import os

from starlette.config import Config

BASE_DIR = os.path.dirname(__file__)

config = Config(".env")


ENVIRONMENT: str = config("ENVIRONMENT", cast=str, default="local")
LOG_LEVEL: str = config("LOG_LEVEL", cast=str, default="INFO")
DEBUG: bool = config("DEBUG", cast=bool, default=False)
