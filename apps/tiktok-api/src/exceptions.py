from starlette.exceptions import HTTPException

from src import logging

log = logging.get_logger(__name__)


class Unauthorized(HTTPException):
    def __init__(self, detail="Unauthorized"):
        super().__init__(401, detail=detail)


class Forbidden(HTTPException):
    def __init__(self, detail="Forbidden"):
        super().__init__(403, detail=detail)


class MethodNotAllowed(HTTPException):
    def __init__(self, detail="Method Not Allowed"):
        super().__init__(405, detail=detail)


class NotFound(HTTPException):
    def __init__(self, detail="Not Found"):
        super().__init__(404, detail=detail)


class BadRequest(HTTPException):
    def __init__(self, detail="Bad Request"):
        super().__init__(400, detail=detail)


class BadData(HTTPException):
    def __init__(self, detail="Bad Data"):
        super().__init__(400, detail=detail)
