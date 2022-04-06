import os

from starlette.config import Config

BASE_DIR = os.path.dirname(__file__)

config = Config(".env")


ENVIRONMENT: str = config("ENVIRONMENT", cast=str, default="local")
