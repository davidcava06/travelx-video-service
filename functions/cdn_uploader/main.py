import base64
import os
from enum import Enum
from typing import List

import structlog
from flask import jsonify
from google.cloud import storage
from providers import upload_hls_to_ipfs_from_gcs
from slack_sdk.webhook import WebhookClient

PROJECT_ID = os.environ["PROJECT_ID"]
BUCKET_NAME = os.environ["BUCKET_NAME"]
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


def list_blobs(prefix: str, bucket_name: str) -> List[storage.Blob]:
    """List blobs in bucket."""
    bucket = storage_client.get_bucket(bucket_name)
    if not bucket.exists():
        logger.error("🤷 Failed read: Bucket does not exist.")
    blob_list = storage_client.list_blobs(bucket_name, prefix=prefix)
    return [blob for blob in blob_list]


def get_blobs_by_content_type(
    blobs: List[storage.Blob], content_type: str
) -> List[storage.Blob]:
    return [blob for blob in blobs if blob.content_type == content_type]


def download_blobs(blobs: List[storage.Blob]) -> List[str]:
    """Download blobs from bucket."""
    root = os.path.dirname(os.path.abspath(__file__))
    file_path_list = []
    for blob in blobs:
        file_name = "-".join(blobs[2].name.split("/")[1:])
        tmp_file_name = f"{root}/tmp/{file_name}"
        blob.download_to_filename(tmp_file_name)
        file_path_list.append(tmp_file_name)
    return file_path_list


def cdn_uploader(event, context):
    # Initialise Slack Message
    title = None
    title_link = None
    thumb_url = None
    text = None

    video_path = base64.b64decode(event["data"]).decode("utf-8")
    if "attributes" in event:
        response_url = event["attributes"]["response_url"]
        logger.info(f"Responding at {response_url}...")
    logger.info(f"Processing {video_path}...")
    video_path = video_path.replace("/video.mp4", "")

    try:
        # List blobs
        blobs = list_blobs(video_path, BUCKET_NAME)
        # Get blobs by content type
        ts_blobs = get_blobs_by_content_type(blobs, "video/mp2t")
        m3u8_blobs = get_blobs_by_content_type(blobs, "application/vnd.apple.mpegurl")
        ts_file_paths = download_blobs(ts_blobs)
        m3u8_file_paths = download_blobs(m3u8_blobs)

        # Upload to CDN
        manifest_ipfs_url, cdn_url = upload_hls_to_ipfs_from_gcs(
            ts_file_paths, m3u8_file_paths
        )
        title = f"{video_path} Here"
        title_link = cdn_url
        status = Status.success
        msg = f"🎉 Successfully uploaded video to {manifest_ipfs_url}"
    except Exception as e:
        logger.error(e)
        status = Status.failed
        msg = f"🤷 Failed upload to cdn: {str(e)}"

    # Notify Slack
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
