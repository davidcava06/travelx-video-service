import base64
import fnmatch
import os
import re
from typing import Optional, Tuple

import firebase_admin
import structlog
from firebase_admin import credentials, firestore
from flask import jsonify
from google.cloud import storage
from providers import InstaClient, Provider, Status
from slack_sdk.webhook import WebhookClient

PROJECT_ID = os.environ["PROJECT_ID"]
BUCKET_NAME = os.environ["BUCKET_NAME"]
INSTA_PROVIDER = Provider.datalama

logger = structlog.get_logger(__name__)
root = os.path.dirname(os.path.abspath(__file__))
storage_client = storage.Client()

cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(
    cred,
    {
        "projectId": PROJECT_ID,
    },
)
db = firestore.client()


def validate_insta_url(url: str) -> Optional[str]:
    """Check for valid url"""
    pattern = re.compile(r"\/((p)|(reel)|(tv))\/[a-zA-Z0-9]+\/")
    object = pattern.search(url)
    if object is None:
        return None
    return object.group()


def parse_insta_url(url: str) -> Optional[Tuple[str, Status]]:
    """Parse and return insta id"""
    raw_insta_id = validate_insta_url(url)
    if raw_insta_id is None:
        return None, Status.failed
    insta_id = raw_insta_id.split("/")[-2]
    pattern = re.compile(r"[a-zA-Z0-9]+")
    if pattern.search(insta_id) is None:
        logger.error(f"🤷 Error parsing: {url}.")
        return None, Status.failed
    return insta_id, Status.success


def upload_file_to_cloudstorage(prefix, temp_file_name, file_name):
    bucket = storage_client.get_bucket(BUCKET_NAME)
    file_path = os.path.join(root, temp_file_name)
    if not bucket.exists():
        logger.error("🤷 Failed upload: Bucket does not exist.")
    blob = bucket.blob(f"{prefix}/{file_name}")
    return blob.upload_from_filename(file_path)


def upload_document_to_firestore(object: dict, insta_id: str):
    doc_ref = db.collection("instaposts").document(insta_id)
    doc_ref.set(object)


def find(pattern, path):
    result = []
    for root, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result


def format_slack_message(
    msg: str,
    status: Status,
    response_type: str = "in_channel",
    title: str = None,
    title_link: str = None,
    thumb_url: str = None,
) -> str:
    message = {
        "response_type": response_type,
        "text": msg,
        "attachments": [],
    }

    attachment = {}
    attachment["color"] = "#EA4435" if status == Status.failed else "#36A64F"
    attachment["title_link"] = title_link
    attachment["title"] = title
    attachment["thumb_url"] = thumb_url

    message["attachments"].append(attachment)
    return message


def insta_downloader(event, context):
    # Initialise Slack Message
    title = None
    title_link = None
    thumb_url = None

    # Parse event content
    if "data" in event:
        insta_url = base64.b64decode(event["data"]).decode("utf-8")
        logger.info(f"Processing {insta_url}...")
    if "attributes" in event:
        response_url = event["attributes"]["response_url"]
        logger.info(f"Responding at {response_url}...")
    insta_id, status = parse_insta_url(insta_url)

    # Download payload from Instagram post
    insta_client = InstaClient(INSTA_PROVIDER)
    logger.info(f"Downloading data for {insta_id}...")
    insta_object, msg, status = insta_client.download_metadata(insta_id)
    if status == Status.success:
        # Store payload
        try:
            logger.info(f"Storing data for {insta_id}...")
            upload_document_to_firestore(insta_object, insta_id)

            logger.info(f"Downloading media for {insta_id}...")
            (
                tmp_thumbnail_path,
                tmp_video_path,
                status,
            ) = insta_client.download_media_files(insta_object)

            logger.info(f"Storing media for {insta_id}...")
            media_type = insta_object["media_type"]
            upload_file_to_cloudstorage(
                media_type, tmp_thumbnail_path, f"{insta_id}/thumbnail.jpg"
            )
            upload_file_to_cloudstorage(
                media_type, tmp_video_path, f"{insta_id}/video.mp4"
            )

            # Send message to Slack
            msg = f"🔫 {insta_id}: Ready pa fusilarlo"
            title = insta_id
            title_link = insta_url
            thumb_url = insta_object["thumbnail_url"]
            status = Status.success
        except Exception as e:
            msg = f"🤷 Storage error: {e}"
            status = Status.failed
            logger.error(msg)

    # Notify Slack
    logger.info(f"Notifying Slack at {response_url}...")
    webhook = WebhookClient(response_url)
    response = format_slack_message(
        msg, status, title=title, title_link=title_link, thumb_url=thumb_url
    )
    webhook.send(**response)
    return jsonify(response)
