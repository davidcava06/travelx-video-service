import os

import structlog
from flask import jsonify
from google.cloud import pubsub_v1
from slack_sdk.signature import SignatureVerifier

PROJECT_ID = os.environ["PROJECT_ID"]
TOPIC_ID = os.environ["TOPIC_ID"]

logger = structlog.get_logger()
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)


def verify_signature(request):
    request.get_data()  # Decodes received requests into request.data

    verifier = SignatureVerifier(os.environ["SLACK_SECRET"])

    if not verifier.is_valid_request(request.data, request.headers):
        raise ValueError("Invalid request/credentials.")


def format_slack_message(msg: str, status: str = None) -> str:
    message = {
        "response_type": "in_channel",
        "text": msg,
        "attachments": [],
    }

    attachment = {}
    if status == "FAILED":
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
        return "Only POST requests are accepted", 405
    verify_signature(request)
    command = request.form["command"]
    text = request.form["text"]
    # Trigger PubSub topic to download insta url contents as temp files
    publish_future = publisher.publish(
        topic_path, text.encode("utf-8"), command=command
    )
    try:
        logger.info(publish_future.result())
        msg = f"{command} {text} job has begun..."
        status = "GOOD"
    except Exception as e:
        msg = f"Publishing {command} {text} errored: {e}"
        status = "FAILED"
        logger.warning(msg)

    # Notify Slack
    pusher_response = format_slack_message(msg, status)
    return jsonify(pusher_response)
