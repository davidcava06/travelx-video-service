import base64
import os
from enum import Enum
from typing import List, Tuple

import structlog
from flask import jsonify
from google.cloud import storage
from providers import CDNClient, Provider
from slack_sdk.webhook import WebhookClient

PROJECT_ID = os.environ["PROJECT_ID"]
BUCKET_NAME = os.environ["TRANSCODED_BUCKET_NAME"]
ENVIRONMENT = os.environ["ENVIRONMENT"]

logger = structlog.get_logger(__name__)
root = os.path.dirname(os.path.abspath(__file__))
storage_client = storage.Client()
cdn_client = CDNClient(Provider.infura)


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


def download_blobs(blobs: List[storage.Blob]) -> List[Tuple[str, str]]:
    """Download blobs from bucket."""
    files_list = []

    for blob in blobs:
        tmp_file_name = "-".join(blob.name.split("/")[1:])
        file_name = blob.name.split("/")[-1]
        tmp_file_path = f"/tmp/{tmp_file_name}"
        blob.download_to_filename(tmp_file_path)
        files_list.append((file_name, tmp_file_path))
    return files_list


def replace_str_in_file(input_file_path: str, replacement_tuples: List[tuple]):
    lines = []
    with open(input_file_path) as infile:
        for line in infile:
            for pair in replacement_tuples:
                line = line.replace(pair[0], pair[1])
            lines.append(line)
    with open(input_file_path, "w") as outfile:
        for line in lines:
            outfile.write(line)

    return input_file_path


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
        ts_files = download_blobs(ts_blobs)
        m3u8_files = download_blobs(m3u8_blobs)
        m3u8_playlist_files = [
            m3u8_file for m3u8_file in m3u8_files if "manifest.m3u8" not in m3u8_file[1]
        ]
        m3u8_manifest_file = [
            m3u8_file for m3u8_file in m3u8_files if "manifest.m3u8" in m3u8_file[1]
        ][0]

        # Upload ts files to CDN
        ts_pairs = cdn_client.upload_files(ts_files)

        # Update playlists m3u8 files with CDN urls
        m3u8_playlists = [
            (playlist[0], replace_str_in_file(playlist[1], ts_pairs))
            for playlist in m3u8_playlist_files
        ]

        playlist_pairs = cdn_client.upload_files(m3u8_playlists)

        # Update manifest.m3u8 file with playlist CDN urls
        m3u8_manifest = (
            m3u8_manifest_file[0],
            replace_str_in_file(m3u8_manifest_file[1], playlist_pairs),
        )
        manifest_pair = cdn_client.upload_files([m3u8_manifest])

        manifest_cdn_url = (
            cdn_client.base_url + manifest_pair[0][1] + "?filename=manifest.m3u8"
        )

        title = f"{video_path} Here"
        title_link = cdn_client.base_url + manifest_pair[0][1] + "?filename=manifest.m3u8"
        status = Status.success
        msg = f"🎉 Successfully uploaded video to {manifest_cdn_url}"
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
