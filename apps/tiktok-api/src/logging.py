import logging
import sys

import structlog
from flask import g
from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        if not log_record.get("timestamp"):
            now = record.created
            log_record["timestamp"] = now
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname
        if "name" not in log_record:
            log_record["name"] = record.name
        if "request_id" not in log_record and hasattr(g, "request_id"):
            log_record["request_id"] = g.request_id


def render_to_logging_kwargs(wrapped_logger, method_name, event_dict):
    msg = event_dict.pop("event") if "event" in event_dict else ""
    exc_info = event_dict.pop("exc_info") if "exc_info" in event_dict else None
    return dict(msg=msg, extra=event_dict, exc_info=exc_info)


def setup(app):
    """Setup standard logging"""
    if not app.testing:
        if app.config.get("ENVIRONMENT") != "local":
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(CustomJsonFormatter())
            logging.basicConfig(level=logging.INFO, handlers=[handler])
        else:
            logging.basicConfig(
                level=logging.INFO, format="%(message)s", stream=sys.stdout
            )

    """ Setup other libraries log level """
    logging.getLogger("werkzeug").setLevel(logging.ERROR)

    """ Setup structured logging """
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]
    if app.config.get("ENVIRONMENT") != "local":
        processors.append(render_to_logging_kwargs)
    else:
        processors.append(structlog.processors.format_exc_info),
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        context_class=structlog.threadlocal.wrap_dict(dict),
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
