import base64
import os
import time
from enum import Enum
from typing import Any, Optional

import structlog
from config import create_standard_job_config
from flask import jsonify
from google.cloud import pubsub_v1, storage
from google.cloud.video import transcoder_v1
from google.cloud.video.transcoder_v1.services.transcoder_service import (
    TranscoderServiceClient,
)
from slack_sdk.webhook import WebhookClient

PROJECT_ID = os.environ["PROJECT_ID"]
LOCATION = os.environ["LOCATION"]
INPUT_BUCKET_NAME = os.environ["INPUT_BUCKET_NAME"]
OUTPUT_BUCKET_NAME = os.environ["OUTPUT_BUCKET_NAME"]
TOPIC_ID = os.environ["TOPIC_ID"]
ENVIRONMENT = os.environ["ENVIRONMENT"]

logger = structlog.get_logger(__name__)
root = os.path.dirname(os.path.abspath(__file__))
storage_client = storage.Client()


class Status(Enum):
    success = "SUCCESS"
    failed = "FAILED"


def format_slack_message(
    msg: str,
    status: Status,
    response_type: str = "in_channel",
    title: str = None,
    title_link: str = None,
    thumb_url: str = None,
    text: str = None,
) -> str:
    message = {
        "response_type": response_type,
        "text": msg,
        "attachments": [],
    }

    attachment = {}
    attachment["author_name"] = "Fiebel"
    attachment["color"] = "#EA4435" if status == Status.failed else "#36A64F"
    attachment["title_link"] = title_link
    attachment["title"] = title
    attachment["text"] = text
    attachment["thumb_url"] = thumb_url

    message["attachments"].append(attachment)
    return message


def notify_slack(
    msg: str,
    status: Status,
    response_url: str,
    title: str = None,
    title_link: str = None,
    thumb_url: str = None,
    text: str = None,
):
    """Notify Slack"""
    logger.info(f"Notifying Slack at {response_url}...")
    webhook = WebhookClient(response_url)
    response = format_slack_message(
        msg, status, title=title, title_link=title_link, thumb_url=thumb_url, text=text
    )
    webhook.send(**response)
    return response


def check_blob_exists(path: Any) -> str:
    bucket = storage_client.get_bucket(INPUT_BUCKET_NAME)
    if not bucket.exists():
        logger.error("🤷 Failed upload: Bucket does not exist.")
        return None
    blob = bucket.get_blob(path)
    if blob is None:
        logger.error("🤷 Failed upload: Blob does not exist.")
        return None
    return "gs://{}/{}".format(INPUT_BUCKET_NAME, path)


def create_job(
    video_uri: str,
    output_uri: str,
    config: Optional[transcoder_v1.types.JobConfig] = None,
    preset: str = "preset/web-hd",
):
    """Creates a job based on an ad-hoc or preset job configuration.

    Args:
        input_uri: Uri of the video in the Cloud Storage bucket.
        output_uri: Uri of the video output folder in the Cloud Storage bucket."""
    job = transcoder_v1.types.Job()
    job.input_uri = video_uri
    job.output_uri = output_uri
    job.ttl_after_completion_days = 1
    if config:
        logger.info("Creating job with custom config.")
        job.config = config
        logger.info(job.config)
    else:
        logger.info(f"Creating job with preset {preset}.")
        job.template_id = preset
    return job


# def transcoder(request):
def transcoder(event, context):
    # Initialise Slack Message
    title = None
    title_link = None
    thumb_url = None
    text = None

    # if request.method != "POST":
    #     return "😒 Only POST requests are accepted", 405
    # event = request.get_json()

    # Parse event content
    # if os.environ["ENVIRONMENT"] != "local":
    # if "data" in event:
    video_path = base64.b64decode(event["data"]).decode("utf-8")
    if "attributes" in event:
        response_url = event["attributes"]["response_url"]
        logger.info(f"Responding at {response_url}...")
    logger.info(f"Processing {video_path}...")

    # Validate input
    video_uri = check_blob_exists(video_path)
    output_directory = video_path.replace("video.mp4", "")
    output_uri = f"gs://{OUTPUT_BUCKET_NAME}/{output_directory}"
    if not video_uri or not output_uri:
        msg = "🤷 Failed upload: No video or output URI."
        status = Status.failed
        logger.error(msg)
        response = notify_slack(
            msg,
            status,
            response_url,
            title=title,
            title_link=title_link,
            thumb_url=thumb_url,
            text=text,
        )
        return jsonify(response)

    # Transcode video
    logger.info("Transcoding video...")
    transcoder_client = TranscoderServiceClient()
    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}"
    job = create_job(
        video_uri,
        output_uri,
        config=create_standard_job_config(),
    )
    logger.info(job)
    job = transcoder_client.create_job(parent=parent, job=job)
    logger.info(f"Created job {job.name}.")

    # Wait for job to finish
    logger.info("Waiting for job to finish...")
    job_name = job.name
    job_state = transcoder_client.get_job(name=job_name).state
    while job_state != transcoder_v1.types.Job.ProcessingState.SUCCEEDED:
        time.sleep(2)
        job_state = transcoder_client.get_job(name=job_name).state
        logger.info(f"Job status: {job_state}")
    logger.info("Job finished.")

    status = Status.success
    msg = f"🎉 Successfully transcoded video to {output_uri}"
    response = notify_slack(
        msg,
        status,
        response_url,
        title="Media Here",
        title_link=output_uri + "manifest.m3u8",
        thumb_url=thumb_url,
        text=text,
    )
    return jsonify(response)


# event = {
#     "attributes": {
#         "response_url": "https://hooks.slack.com/services/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"
#     },
#     "data": {
#         "video_path": "tiktok/7081723363546189061/video.mp4"
#     }
# }
# event = {
#     "attributes": {
#         "response_url": "https://hooks.slack.com/services/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"
#     },
#     "data": "dGlrdG9rLzcwODE3MjMzNjM1NDYxODkwNjEvdmlkZW8ubXA0Cg==",
# }
# transcoder(event, {})
