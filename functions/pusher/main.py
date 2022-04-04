import os
from enum import Enum

import structlog
from flask import jsonify
from google.cloud import pubsub_v1
from slack_sdk.signature import SignatureVerifier

PROJECT_ID = os.environ["PROJECT_ID"]
TOPIC_ID = os.environ["TOPIC_ID"]
SLACK_SECRET = os.environ["SLACK_SECRET"]

logger = structlog.get_logger()
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)


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
    # attachment["title_link"] = url
    # attachment["title"] = name
    # attachment["title_link"] = url
    # attachment["text"] = article
    # attachment["image_url"] = image_url
    message["attachments"].append(attachment)

    return message


def pusher(request):
    if request.method != "POST":
        return "😒 Only POST requests are accepted", 405
    verify_signature(request)
    command = request.form["command"]
    text = request.form["text"]
    response_url = request.form["response_url"]

    if command != "/ig":
        msg = "🥺 Command not supported."
        status = Status.failed
    else:
        # Trigger PubSub topic to download insta url contents as temp files
        logger.info(topic_path)
        publish_future = publisher.publish(
            topic_path,
            text.encode("utf-8"),
            command=command,
            response_url=response_url,  # NOQA
        )
        msg = f"🤓 {command} {text} job has begun..."
        status = Status.success
        print("Publish future sent")
        logger.info(publish_future.result())

    # Notify Slack
    pusher_response = format_slack_message(msg, status, "in_channel")
    return jsonify(pusher_response)
