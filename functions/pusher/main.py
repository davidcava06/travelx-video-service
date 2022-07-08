import os
from enum import Enum

import structlog
from flask import jsonify
from google.cloud import pubsub_v1
from slack_sdk.signature import SignatureVerifier

PROJECT_ID = os.environ["PROJECT_ID"]
INSTA_TOPIC_ID = os.environ["INSTA_TOPIC_ID"]
TIKTOK_TOPIC_ID = os.environ["TIKTOK_TOPIC_ID"]
UPDATE_TOPIC_ID = os.environ["UPDATE_TOPIC_ID"]
MEDIA_TX_TOPIC_ID = os.environ["MEDIA_TX_TOPIC_ID"]
GUIDE_C_TOPIC_ID = os.environ["GUIDE_C_TOPIC_ID"]
SLACK_SECRET = os.environ["SLACK_SECRET"]
TOPICS = {
    "/ig": INSTA_TOPIC_ID,
    "/tik": TIKTOK_TOPIC_ID,
    "/update": UPDATE_TOPIC_ID,
    "/tx": MEDIA_TX_TOPIC_ID,
    "/guidec": GUIDE_C_TOPIC_ID,
}
COMMANDS = [key for key in TOPICS.keys()]

logger = structlog.get_logger()


class Status(Enum):
    success = "SUCCESS"
    failed = "FAILED"


def verify_signature(request):
    request.get_data()  # Decodes received requests into request.data

    verifier = SignatureVerifier(SLACK_SECRET)

    if not verifier.is_valid_request(request.data, request.headers):
        raise ValueError("Invalid request/credentials.")


def format_slack_message(
    msg: str, status: Status, response_type: str = "in_channel"
) -> str:
    message = {
        "response_type": response_type,
        "text": msg,
        "attachments": [],
    }

    attachment = {}
    if status == Status.failed:
        attachment["color"] = "#EA4435"
    message["attachments"].append(attachment)
    return message


def pusher(request):
    if request.method != "POST":
        return "😒 Only POST requests are accepted", 405
    verify_signature(request)
    command = request.form["command"]
    text = request.form["text"]
    response_url = request.form["response_url"]

    if command not in COMMANDS:
        msg = "🥺 Command not supported."
        status = Status.failed
    else:
        TOPIC_ID = TOPICS[command]
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)
        publisher.publish(
            topic_path,
            text.encode("utf-8"),
            command=command,
            response_url=response_url,  # NOQA
        )
        msg = f"🤓 {command} {text} job has begun..."
        status = Status.success

    # Notify Slack
    pusher_response = format_slack_message(msg, status, "in_channel")
    return jsonify(pusher_response)
