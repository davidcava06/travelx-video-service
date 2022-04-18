import asyncio
import base64
import os
from uuid import uuid4

import nest_asyncio
import structlog
from flask import Flask, jsonify, request
from google.cloud import pubsub_v1

from src import errors, logging
from src.config import ENVIRONMENT, config
from src.extensions import storage
from src.slack import SlackMessage
from src.status import Status
from src.tiktok import get_video_from_url
from TikTokApi import TikTokApi

logger = structlog.get_logger()


def init_extensions(app):
    storage.init_app(app)


app = Flask(__name__)
app.config.from_object(config[ENVIRONMENT])
PROJECT_ID = app.config.get("GCP_PROJECT")
TOPIC_ID = app.config.get("TOPIC_ID")
CF_ACCOUNT = app.config.get("CF_ACCOUNT")
CF_TOKEN = app.config.get("CF_TOKEN")

# logging
logging.setup(app)

# extension
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


@app.route("/", methods=["GET"])
def root():
    return jsonify({"status": 200})


@app.route("/", methods=["POST"])
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
    # Initialise Slack Message
    slack_message = SlackMessage()
    msg = None
    tiktok_object = None

    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({"message": "Nothing to do here"}), 200

        pubsub_message = json_data["message"]
        # Parse event content
        if "data" in pubsub_message:
            video_url = base64.b64decode(pubsub_message["data"]).decode("utf-8").strip()
            logger.info(f"Processing {video_url}...")
        if "attributes" in pubsub_message:
            response_url = pubsub_message["attributes"]["response_url"]
            logger.info(f"Responding at {response_url}...")

        logger.info("get_video", video_url=video_url)

        # Initialise TikTokApi
        nest_asyncio.apply()
        asyncio.new_event_loop()
        api = TikTokApi()

        tiktok_object, video_path = get_video_from_url(api, video_url)
        status = Status.success

        # Not required with CloudFlare Stream
        # Publish Transcoder Job
        # if ENVIRONMENT != "local":
        #     publisher = pubsub_v1.PublisherClient()
        #     topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)
        #     publisher.publish(
        #         topic_path,
        #         video_path.encode("utf-8"),
        #         response_url=response_url,
        #     )

    except Exception as e:
        msg = f"🤷 Storage error: {e}"
        status = Status.failed
        logger.error(msg)

    # Notify Slack
    logger.info(f"Notifying Slack at {response_url}...")
    slack_message.get_message_from_video(status, tiktok_object, msg)
    slack_message.webhook_send(response_url)
    return jsonify({"content": tiktok_object, "status": 200})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
