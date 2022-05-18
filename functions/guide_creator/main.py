import os

import firebase_admin
import google.auth
import structlog
from data import create_guide_object, from_experience_to_summary_v2
from firebase_admin import credentials, firestore
from flask import jsonify
from googleapiclient.discovery import build
from providers import SheetClient, Status, StorageClient
from slack_sdk.webhook import WebhookClient

PROJECT_ID = os.environ["PROJECT_ID"]
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
UPDATE_RANGE_NAME = "UpdateGuides!A2:F50"

logger = structlog.get_logger(__name__)

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


def guide_creator(event, context):
    # Parse event content
    if "attributes" in event:
        response_url = event["attributes"]["response_url"]
        logger.info(f"Responding at {response_url}...")

    sheets_client = SheetClient(sheet_client=sheet_client)
    storage_client = StorageClient(document_db=db)

    # Read data from Google Sheet
    guide_rows = sheets_client.read_spreadsheet()
    if guide_rows is not None and len(guide_rows) > 0:
        try:
            for guide_row in guide_rows:
                # Find relevant experiences
                logger.info("Finding relevant Experiences...")
                experience_summaries = []
                for experience_uid in guide_row["experience_uids"]:
                    experience = storage_client.find_document_in_firestore(
                        "uid", experience_uid, "experiences"
                    )
                    logger.info("Updating Post Experience Summaries...")
                    experience_object = experience.to_dict()
                    experience_summary = from_experience_to_summary_v2(
                        experience_object
                    )
                    experience_summaries.append(experience_summary)

                # Create Image array
                images = []

                # Create the Guide Object
                guide_object = create_guide_object(
                    guide_row, images, experience_summaries
                )

                # Upload snapshot in Firestore
                storage_client.upload_document_to_firestore(
                    guide_object, guide_object["snapshot_uid"], "snapshots"
                )
                # Upload guide in Firestore
                storage_client.upload_document_to_firestore(
                    guide_object, guide_object["guide_uid"], "guides"
                )

            # Send message to Slack
            msg = "🆕 New Guide Available"
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
