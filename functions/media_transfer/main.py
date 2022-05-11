import os

import firebase_admin
import google.auth
import structlog
from data import MediaTxRow, from_experience_to_summary
from firebase_admin import credentials, firestore
from flask import jsonify
from googleapiclient.discovery import build
from providers import Status
from slack_sdk.webhook import WebhookClient

PROJECT_ID = os.environ["PROJECT_ID"]
SHEET_ID = os.environ["SHEET_ID"]
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
RANGE_NAME = "Media!A3:C100"

logger = structlog.get_logger(__name__)
root = os.path.dirname(os.path.abspath(__file__))

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


def read_spreadsheet(spreadsheet_id: str = SHEET_ID, range: str = RANGE_NAME):
    sheet = sheet_client.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range).execute()
    values = result.get("values", [])
    if not values:
        logger.info("No data found...")
        return None

    elements = []
    for row in values:
        element = {}
        for idx, x in enumerate(row):
            if type(x) is str:
                x = x.strip().lower()
            element[str(MediaTxRow(idx))] = x
        elements.append(element)
    return elements


def update_document_to_firestore(object: dict, id: str, collection: str):
    doc_ref = db.collection(collection).document(id)
    doc_ref.update(object)


def find_document_in_firestore(key: str, id: str, collection: str):
    return db.collection(collection).where(key, "==", id).get()


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


def media_transfer(event, context):
    # Parse event content
    if "attributes" in event:
        response_url = event["attributes"]["response_url"]
        logger.info(f"Responding at {response_url}...")

    # Read data from Google Sheet
    logger.info(f"Reading data from {SHEET_ID}...")
    rows = read_spreadsheet()
    if rows is not None and len(rows) > 0:
        # Update data in Firestore
        try:
            for row in rows:
                experience_from_uid = row["experience_from_uid"]
                experience_to_uid = row["experience_to_uid"]

                logger.info(f"Fetching media from experience: {experience_from_uid}...")
                experiences = find_document_in_firestore(
                    "uid", experience_from_uid, "experiences"
                )
                experience_from_object = experiences[0].to_dict()
                media_from = experience_from_object["media"]

                logger.info(f"Fetching media from experience: {experience_to_uid}...")
                experiences = find_document_in_firestore(
                    "uid", experience_to_uid, "experiences"
                )
                experience_to_object = experiences[0].to_dict()
                media_to = experience_to_object["media"]

                logger.info("Transferring Media...")
                extra_media = [x for x in media_from if x not in media_to]
                if extra_media is not None or len(extra_media) > 0:
                    add_media_object = dict(media=firestore.ArrayUnion(extra_media))
                    update_document_to_firestore(
                        add_media_object, experience_to_uid, "experiences"
                    )
                    logger.info("Updating Experience Summaries...")
                    summary = from_experience_to_summary(experience_to_object)
                    for media in extra_media:
                        update_document_to_firestore(summary, media["uid"], "media")

                logger.info(f"Deleting Experience {experience_from_uid}...")
                update_document_to_firestore(
                    dict(status="deleted"), experience_from_uid, "experiences"
                )

            # Send message to Slack
            msg = "🆕 Media Transferred"
            status = Status.success
        except Exception as e:
            msg = f"🤷 Storage error: {e}"
            status = Status.failed
            logger.error(msg)

    # Notify Slack
    logger.info(f"Notifying Slack at {response_url}...")
    webhook = WebhookClient(response_url)
    response = format_slack_message(msg, status)
    webhook.send(**response)
    return jsonify(response)
