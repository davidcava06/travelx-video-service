import base64
import fnmatch
import os
import re
import time
from typing import Any, List, Optional, Tuple
from uuid import uuid4

import firebase_admin
import google.auth
import structlog
from data import create_data_objects, experience_object_to_row
from firebase_admin import credentials, firestore
from flask import jsonify
from google.cloud import storage  # pubsub_v1,
from googleapiclient.discovery import build
from providers import CFClient, InstaClient, Provider, Status
from slack_sdk.webhook import WebhookClient

PROJECT_ID = os.environ["PROJECT_ID"]
BUCKET_NAME = os.environ["BUCKET_NAME"]
INSTA_PROVIDER = Provider.datalama
TOPIC_ID = os.environ["TOPIC_ID"]
SHEET_ID = os.environ["SHEET_ID"]
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
RANGE_NAME = "Experiences!A3:BD100"

logger = structlog.get_logger(__name__)
root = os.path.dirname(os.path.abspath(__file__))
storage_client = storage.Client()
cdn_client = CFClient()

cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(
    cred,
    {
        "projectId": PROJECT_ID,
    },
)
db = firestore.client()

sheet_creds, _ = google.auth.default(scopes=SCOPES)
sheet_client = build("sheets", "v4", credentials=sheet_creds)


def update_spreadsheet(
    values: List[List[Any]], spreadsheet_id: str = SHEET_ID, range: str = RANGE_NAME
):
    sheet = sheet_client.spreadsheets()
    result = (
        sheet.values()
        .append(
            spreadsheetId=spreadsheet_id,
            range=range,
            body=dict(
                values=values,
                majorDimension="ROWS",
            ),
            valueInputOption="USER_ENTERED",
        )
        .execute()
    )

    updates = result.get("updates", {})
    if updates.get("updatedRows") != len(values):
        raise Exception("Writing to Google Sheets Error")


def validate_insta_url(url: str) -> Optional[str]:
    """Check for valid url"""
    pattern = re.compile(r"\/((p)|(reel)|(tv))\/[a-zA-Z0-9!@#$&()-_]+\/")
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


def upload_file_to_cloudstorage(prefix, temp_file_name, file_name, content_type=None):
    bucket = storage_client.get_bucket(BUCKET_NAME)
    file_path = os.path.join(root, temp_file_name)
    if not bucket.exists():
        logger.error("🤷 Failed upload: Bucket does not exist.")
    blob = bucket.blob(f"{prefix}/{file_name}")
    return blob.upload_from_filename(file_path, content_type=content_type)


def upload_document_to_firestore(object: dict, id: str, collection: str = "instaposts"):
    doc_ref = db.collection(collection).document(id)
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


def insta_downloader(event, context):
    # Initialise Slack Message
    title = None
    title_link = None
    thumb_url = None
    text = None

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
            logger.info(f"Storing raw data for {insta_id}...")
            upload_document_to_firestore(insta_object, insta_id)

            logger.info(f"Downloading media for {insta_id}...")
            (
                tmp_thumbnail_path,
                tmp_video_path,
                status,
            ) = insta_client.download_media_files(insta_object)

            logger.info(f"Storing media for {insta_id}...")
            media_type = insta_object["media_type"]

            if tmp_thumbnail_path is not None:
                upload_file_to_cloudstorage(
                    media_type,
                    tmp_thumbnail_path,
                    f"{insta_id}/thumbnail.jpg",
                    content_type="image/jpeg",
                )
            if tmp_video_path is not None:
                upload_file_to_cloudstorage(
                    media_type,
                    tmp_video_path,
                    f"{insta_id}/video.mp4",
                    content_type="video/mp4",
                )

                # Upload to CloudFlare
                logger.info(f"Uploading to CloudFlare for {insta_id}...")
                response = cdn_client.upload_files(tmp_video_path, insta_id)
                ready_to_stream = response["readyToStream"]
                while ready_to_stream is not True:
                    time.sleep(2)
                    response = cdn_client.get_video_by_name(insta_id)
                    ready_to_stream = response[0]["readyToStream"]
                    logger.info(f"Job status: {ready_to_stream}")

                logger.info(f"Formatting data object for {insta_id}...")
                video_object = response[0]
                video_object["storage"] = "cloudflare"
                video_object["storage_id"] = video_object["uid"]
                video_object["uid"] = str(uuid4())
                experience_instance, post_instance = create_data_objects(
                    insta_object, video_object
                )
                experience_uid = experience_instance["uid"]

                logger.info(f"Storing data object for {insta_id}...")
                upload_document_to_firestore(
                    experience_instance, experience_instance["uid"], "experiences"
                )

                upload_document_to_firestore(
                    post_instance, post_instance["uid"], "posts"
                )

                logger.info(f"Adding Experience {experience_uid} to Sheet...")
                # Create array from experience instance
                experience_row = experience_object_to_row(experience_instance)
                # Update spreadsheet
                update_spreadsheet([experience_row])

                # Not required with CloudFlare Stream
                # Publish Transcoding Job
                # video_path = f"{media_type}/{insta_id}/video.mp4"
                # publisher = pubsub_v1.PublisherClient()
                # topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)
                # publisher.publish(
                #     topic_path,
                #     video_path.encode("utf-8"),
                #     response_url=response_url,  # NOQA
                # )

            # Send message to Slack
            msg = f"🔫 {insta_id}: Ready pa fusilarlo"
            title = "Experience: " + experience_instance["uid"]
            title_link = insta_url
            thumb_url = insta_object["thumbnail_url"]
            text = "Post: " + post_instance["uid"]
            status = Status.success
        except Exception as e:
            msg = f"🤷 Storage error: {e}"
            status = Status.failed
            logger.error(msg)

    # Notify Slack
    logger.info(f"Notifying Slack at {response_url}...")
    webhook = WebhookClient(response_url)
    response = format_slack_message(
        msg, status, title=title, title_link=title_link, thumb_url=thumb_url, text=text
    )
    webhook.send(**response)
    return jsonify(response)
