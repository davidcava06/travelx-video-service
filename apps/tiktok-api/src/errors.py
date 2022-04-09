import structlog
from flask import current_app, jsonify, request
from marshmallow.exceptions import ValidationError
from werkzeug.exceptions import BadRequest, HTTPException, UnprocessableEntity

logger = structlog.get_logger(__name__)


def init_app(app):
    app.register_error_handler(HTTPException, handle_werkzeug_exception)
    app.register_error_handler(ValidationError, handle_validation)
    app.register_error_handler(BadRequest, handle_bad_request)
    if not app.debug and not app.testing:
        app.register_error_handler(Exception, handle_generic_exception)


def handle_bad_request(error):
    logger.info("bad_request", messages=error.messages)
    return jsonify(error.messages), 400


def handle_unprocessable(error):
    return handle_werkzeug_exception(
        UnprocessableEntity("Oops! Something is wrong with the data you sent")
    )


def handle_validation(error):
    logger.info("validation_error", messages=error.messages)
    return jsonify(error.messages), 422


def handle_werkzeug_exception(error):
    if error.code == 500:
        logger.exception("exception", exc_info=error)
    if error.code == 409:
        logger.exception("conflict", exc_info=error, contents=request.data)
    return (
        jsonify({"message": error.description, "status_code": error.code}),
        error.code or 500,
    )


def handle_generic_exception(error):
    if current_app.debug and not current_app.testing:
        raise error
    logger.exception("exception", exc_info=error)
    return jsonify({"message": "oops! something went wrong", "status_code": 500}), 500
