import base64
import fnmatch
import json
import lzma
import os
import re
from enum import Enum
from typing import Optional, Tuple

import firebase_admin
import instaloader
import structlog
from firebase_admin import credentials, firestore
from flask import jsonify
from google.cloud import storage
from slack_sdk.webhook import WebhookClient

PROJECT_ID = os.environ["PROJECT_ID"]
BUCKET_NAME = os.environ["BUCKET_NAME"]

logger = structlog.get_logger()
root = os.path.dirname(os.path.abspath(__file__))
insta_loader = instaloader.Instaloader(quiet=True)
storage_client = storage.Client()

cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(
    cred,
    {
        "projectId": PROJECT_ID,
    },
)
db = firestore.client()


class Status(Enum):
    success = "SUCCESS"
    failed = "FAILED"


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


def download_post(insta_id: str) -> Optional[Tuple[str, Status]]:
    target_directory = f"/tmp/{insta_id}"
    post = instaloader.Post.from_shortcode(insta_loader.context, insta_id)
    download_ind = insta_loader.download_post(post, target_directory)
    if not download_ind:
        return "🤷 Error downloading {} from instagram.", Status.failed
    return target_directory, Status.success


def parse_insta_object(file_name) -> dict:
    """Takes a tarfile json and outputs a python object"""
    file_path = os.path.join(root, file_name)
    bytes_value = lzma.open(file_path).read()
    insta_json = bytes_value.decode("utf8")
    return json.loads(insta_json)


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


def insta_downloader(event, context):
    # Parse event content
    if "data" in event:
        insta_url = base64.b64decode(event["data"]).decode("utf-8")
    if "attributes" in event:
        response_url = event["attributes"]["response_url"]
    insta_id, status = parse_insta_url(insta_url)

    # Download payload from Instagram post
    logger.info(insta_id)
    target_directory, status = download_post(insta_id)

    # Store payload
    try:
        thumbnail_paths = find("*.jpg", target_directory)
        if len(thumbnail_paths) > 0:
            upload_file_to_cloudstorage(
                insta_id, thumbnail_paths[0], "thumbnail.jpg"
            )  # MVP

        video_paths = find("*.mp4", target_directory)
        if len(video_paths) > 0:
            upload_file_to_cloudstorage(insta_id, video_paths[0], "video.mp4")

        insta_object_paths = find("*.json.xz", target_directory)
        if len(insta_object_paths) > 0:
            insta_object = parse_insta_object(insta_object_paths[0])  # MVP
            upload_document_to_firestore(insta_object, insta_id)
        msg = f"🔫 {insta_id}: Ready pa fusilarlo"
        status = Status.success
    except Exception as e:
        msg = f"🤷 Storage error: {e}"
        status = Status.failed
        logger.error(msg)

    # Notify Slack
    webhook = WebhookClient(response_url)
    response = format_slack_message(msg, status)
    webhook.send(**response)
    return jsonify(response)
