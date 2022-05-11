from enum import Enum

import structlog

logger = structlog.get_logger(__name__)


class Status(Enum):
    success = "SUCCESS"
    failed = "FAILED"
