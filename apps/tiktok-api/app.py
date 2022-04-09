import asyncio
import nest_asyncio
import os
import structlog

from uuid import uuid4
from werkzeug.exceptions import BadRequest
from flask import Flask, jsonify, request

from TikTokApi import TikTokApi

from src import logging, errors
from src.config import ENVIRONMENT, config
from src.extensions import storage
from src.tiktok import get_video_from_url

logger = structlog.get_logger()

def init_extensions(app):
    storage.init_app(app)

app = Flask(__name__)
app.config.from_object(config[ENVIRONMENT])

# logging
logging.setup(app)

# extensions
init_extensions(app)
errors.init_app(app)


@app.before_request
def before_request():
    logger.new(request_id=str(uuid4()))
    if ENVIRONMENT != "local":
        logger.info("start_request")

@app.after_request
def after_request(response):
    if ENVIRONMENT != "local":
        logger.info(
            "end_request",
            addr=request.remote_addr,
            path=request.path,
            request_args=request.args,
            method=request.method,
            response_status=response.status_code,
        )
    return response

@app.route("/")
def root():
    return jsonify({"status": 200})

@app.route("/video", methods=["POST"])
async def video():
    """Get Video from TikTok
    ---
    description: Given a TikTok URL, return the video
    responses:
        200:
            description: Executes request
        400:
            description: Bad Request
        403:
            description: Forbidden
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "Nothing to do here"}), 200

    video_url = json_data.get("video_url")
    if not video_url:
        raise BadRequest("No video url provided")

    logger.info("get_video", video_url=video_url)

    # Initialise TikTokApi
    nest_asyncio.apply()
    asyncio.new_event_loop()
    api = TikTokApi()

    data = get_video_from_url(api, video_url)
    return jsonify({"content": data, "status": 200})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
