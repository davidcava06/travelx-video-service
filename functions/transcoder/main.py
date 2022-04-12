import base64
import os
from enum import Enum
from typing import Any, Optional

import structlog
from config import create_standard_job_config
from flask import jsonify
from google.cloud import storage
from google.cloud.video import transcoder_v1
from google.cloud.video.transcoder_v1.services.transcoder_service import (
    TranscoderServiceClient,
)
from slack_sdk.webhook import WebhookClient

PROJECT_ID = os.environ["PROJECT_ID"]
LOCATION = os.environ["LOCATION"]
BUCKET_NAME = os.environ["BUCKET_NAME"]

logger = structlog.get_logger(__name__)
root = os.path.dirname(os.path.abspath(__file__))
storage_client = storage.Client()
transcoder_client = TranscoderServiceClient()
parent = f"projects/{PROJECT_ID}/locations/{LOCATION}"


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
    bucket = storage_client.get_bucket(BUCKET_NAME)
    if not bucket.exists():
        logger.error("🤷 Failed upload: Bucket does not exist.")
        return None
    blob = bucket.get_blob(path)
    if blob is None:
        logger.error("🤷 Failed upload: Blob does not exist.")
        return None
    return "gs://{}/{}".format(BUCKET_NAME, path)


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
    if config:
        logger.info("Creating job with custom config.")
        job.config = config
    else:
        logger.info(f"Creating job with preset {preset}.")
        job.template_id = preset

    response = transcoder_client.create_job(parent=parent, job=job)
    logger.info(f"Created job {response.name}.")
    breakpoint()
    return response


def transcoder(event, context):
    # Initialise Slack Message
    title = None
    title_link = None
    thumb_url = None
    text = None

    # Parse event content
    media_data = event["data"]
    if os.environ["ENVIRONMENT"] != "local":
        if "data" in event:
            media_data = base64.b64decode(event["data"]).decode("utf-8")
    if "attributes" in event:
        response_url = event["attributes"]["response_url"]
        logger.info(f"Responding at {response_url}...")
    video_path = media_data.get("video_path")
    thumbnail_path = media_data.get("thumbnail_path")
    output_uri = media_data.get("output_uri")
    logger.info(f"Processing {video_path}...")

    # Validate input
    video_uri = check_blob_exists(video_path)
    thumbnail_uri = check_blob_exists(thumbnail_path)
    if not video_uri or not thumbnail_uri or not output_uri:
        msg = "🤷 Failed upload: No video, thumbnail input or output URI."
        status = Status.failed
        logger.error(msg)
        # response = notify_slack(
        #     msg,
        #     status,
        #     response_url,
        #     title=title,
        #     title_link=title_link,
        #     thumb_url=thumb_url,
        #     text=text,
        # )
        # return jsonify(response)
        return jsonify({"status": msg})

    # Transcode video
    logger.info("Transcoding video...")
    job = create_job(
        video_uri, output_uri  #, config=create_standard_job_config(thumbnail_uri)
    )
    logger.info(job)

    status = Status.success
    msg = f"🎉 Successfully started transcoding video {video_path}"
    breakpoint()
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

event = {
    "attributes": {"response_url": "https://hooks.slack.com/actions/T12345/12345/12345"},
    "data": {
        "video_path": "tiktok/6977073002311650566/video.mp4",
        "thumbnail_path": "tiktok/6977073002311650566/thumbnail.jpg",
        "output_uri": f"gs://{BUCKET_NAME}/",
    }
}
# transcoder(event, {})