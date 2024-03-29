import os

import firebase_admin
import google.auth
import structlog
from data import ExperienceRow, from_experience_to_summary
from firebase_admin import credentials, firestore
from flask import jsonify
from googleapiclient.discovery import build
from providers import Status
from slack_sdk.webhook import WebhookClient

PROJECT_ID = os.environ["PROJECT_ID"]
SHEET_ID = os.environ["SHEET_ID"]
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
RANGE_NAME = "Experiences!A3:BD300"
ARRAY_COLUMNS = [2, 9, 12, 19, 32, 49]
BOOL_COLUMNS = [1, 7, 8, 20, 28, 44]

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
            if idx in ARRAY_COLUMNS:
                x_list = x.split(",")
                clean_list = [
                    element.strip().lower() for element in x_list if element != ""
                ]
                x = firestore.ArrayUnion(clean_list) if len(clean_list) > 0 else None
            if type(x) is str:
                x = x.strip().lower()
                x = x if x != "" else None
            if idx in BOOL_COLUMNS:
                x = bool(int(x))
            element[str(ExperienceRow(idx))] = x
        clean_element = {k: v for k, v in element.items() if v is not None}
        elements.append(clean_element)
    return elements


def update_document_to_firestore(object: dict, id: str, collection: str):
    doc_ref = db.collection(collection).document(id)
    doc_ref.update(object)


def find_document_in_firestore(key: str, id: str, collection: str):
    return db.collection(collection).where(key, "==", id).get()


def add_parent_media(experience: dict) -> dict:
    if experience.get("parent") is not None and experience.get("parent") != "":
        logger.info("Finding relevant parent media...")
        parent_experience = find_document_in_firestore(
            "uid", experience["parent"], "experiences"
        )
        if parent_experience is None or len(parent_experience) == 0:
            return experience

        logger.info("Adding parent media...")
        parent_object = parent_experience[0].to_dict()  # only 1 parent
        parent_media = parent_object.get("media")
        if parent_media is not None:
            extra_media = []
            current_media = experience.get("media")
            if current_media is None:
                current_media = []
            extra_media = [x for x in parent_media if x not in current_media]
            media_update = dict(media=firestore.ArrayUnion(extra_media))
            update_document_to_firestore(media_update, experience["uid"], "experiences")


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


def experience_updater(event, context):
    # Parse event content
    if "attributes" in event:
        response_url = event["attributes"]["response_url"]
        logger.info(f"Responding at {response_url}...")

    # Read data from Google Sheet
    logger.info(f"Reading data from {SHEET_ID}...")
    experiences = read_spreadsheet()
    if experiences is not None and len(experiences) > 0:
        # Update data in Firestore
        try:
            for experience in experiences:
                experience_uid = experience["uid"]
                add_parent_media(experience)

                logger.info(f"Updating Experience: {experience_uid}...")
                update_document_to_firestore(
                    experience, experience["uid"], "experiences"
                )

                # Find relevant media
                logger.info("Finding relevant Media...")
                posts = find_document_in_firestore(
                    "experience_summary.uid", experience["uid"], "posts"
                )
                for post in posts:
                    logger.info("Updating Post Experience Summaries...")
                    post_object = post.to_dict()
                    summary = from_experience_to_summary(experience)
                    update_document_to_firestore(summary, post_object["uid"], "posts")

            # Send message to Slack
            msg = "🆕 Experiences Updated"
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
