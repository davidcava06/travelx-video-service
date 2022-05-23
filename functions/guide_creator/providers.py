import json
import os
from enum import Enum

import requests
import structlog
from data import GuideRow, Image
from firebase_admin import firestore

logger = structlog.get_logger(__name__)
root = os.path.dirname(os.path.abspath(__file__))

SHEET_ID = os.environ["SHEET_ID"]
CREATE_RANGE_NAME = "CreateGuides!A2:F50"
ARRAY_COLUMNS = [5]
BOOL_COLUMNS = [2, 3]
CF_ACCOUNT = os.environ["CF_ACCOUNT"]
CF_TOKEN = os.environ["CF_TOKEN"]


class Status(Enum):
    success = "SUCCESS"
    failed = "FAILED"


class SheetClient:
    def __init__(self, sheet_client):
        self.sheet_client = sheet_client

    def read_spreadsheet(
        self, spreadsheet_id: str = SHEET_ID, range: str = CREATE_RANGE_NAME
    ):
        logger.info(f"Reading data from {spreadsheet_id}...")
        sheet = self.sheet_client.spreadsheets()
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range).execute()
        values = result.get("values", [])
        if not values:
            logger.info("No data found...")
            return None

        arrays = []
        elements = []
        for row in values:
            element = {}
            for idx, x in enumerate(row):
                if idx in ARRAY_COLUMNS:
                    x_list = x.split(",")
                    clean_list = [
                        element.strip().lower() for element in x_list if element != ""
                    ]
                    x = (
                        firestore.ArrayUnion(clean_list)
                        if len(clean_list) > 0
                        else None
                    )
                    arrays.append({str(GuideRow(idx)): clean_list})
                if type(x) is str:
                    x = x.strip().lower()
                    x = x if x != "" else None
                if idx in BOOL_COLUMNS:
                    x = bool(int(x))
                element[str(GuideRow(idx))] = x
            elements.append(element)
        return elements, arrays


class StorageClient:
    def __init__(self, document_db):
        self.document_db = document_db

    def upload_document_to_firestore(
        self, object: dict, id: str, collection: str = "instaposts"
    ):
        logger.info(f"Uploading {id} to {collection}...")
        doc_ref = self.document_db.collection(collection).document(id)
        doc_ref.set(object)

    def update_document_to_firestore(self, object: dict, id: str, collection: str):
        doc_ref = self.document_db.collection(collection).document(id)
        doc_ref.update(object)

    def find_document_in_firestore(self, key: str, id: str, collection: str):
        return self.document_db.collection(collection).where(key, "==", id).get()


class CFClient:
    def __init__(self, cf_account: str = CF_ACCOUNT, cf_token: str = CF_TOKEN):
        self.base_url = "https://api.cloudflare.com/client/v4/accounts"
        self.account = cf_account
        self.token = cf_token

    def upload_image_from_url(self, image_origin_url: str, guide_name: str) -> dict:
        """Upload a file to CloudFlare Images"""
        logger.info(f"Uploading to {self.base_url}...")

        headers = {
            "Authorization": f"Bearer {self.token}",
        }
        data = {
            "url": image_origin_url,
            "requireSignedURLs": json.dumps("false"),
            "metadata": json.dumps({"type": "guide", "name": guide_name}),
        }
        response = requests.post(
            f"{self.base_url}/{self.account}/images/v1",
            files=data,
            headers=headers,
        )
        results = response.json()
        image_variants = results["result"]["variants"]
        image_list = []
        for image_variant in image_variants:
            # Guides are always squares
            height = (
                600
                if "guidebig" in image_variant
                else (300 if "guidemedium" in image_variant else 64)
            )
            width = height
            image = Image(url=image_variant, height=height, width=width)
            image_list.append(image)
        return image_list
