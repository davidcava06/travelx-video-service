import os

from flask import jsonify
from slack.signature import SignatureVerifier
from google.cloud import pubsub_v1

PROJECT_ID = os.environ["PROJECT_ID"]
TOPIC_ID = os.environ["TOPIC_ID"]

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)


def verify_signature(request):
    request.get_data()  # Decodes received requests into request.data

    verifier = SignatureVerifier(os.environ["SLACK_SECRET"])

    if not verifier.is_valid_request(request.data, request.headers):
        raise ValueError("Invalid request/credentials.")


def format_slack_message(query: str) -> str:
    message = {
        "response_type": "in_channel",
        "text": "Task: {} has begun...".format(query),
        "attachments": [],
    }

    attachment = {}
    # attachment["color"] = "#3367d6"
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
    # Parse insta url
    # Trigger PubSub topic to download insta url contents as temp files
    # Notify Slack
    pusher_response = format_slack_message(request.form["text"])
    return jsonify(pusher_response)
