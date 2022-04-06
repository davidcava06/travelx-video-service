import logging as std_logging
from logging.config import dictConfig

from src import config

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(asctime)s][%(name)-24s][%(levelname)-8s]: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "level": config.LOG_LEVEL,
            "formatter": "default",
        },
        "stderr": {
            "class": "logging.StreamHandler",
            "level": config.LOG_LEVEL,
            "formatter": "default",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "": {"handlers": ["stdout"], "level": config.LOG_LEVEL, "propagate": True},
        "uvicorn.access": {
            "handlers": ["stdout"],
            "level": config.LOG_LEVEL,
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["stderr"],
            "level": config.LOG_LEVEL,
            "propagate": False,
        },
    },
}


dictConfig(log_config)


get_logger = std_logging.getLogger
