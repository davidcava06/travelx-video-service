import os
from enum import Enum
from typing import Any, Optional, Tuple

import requests
import structlog
import wget
from instagrapi import Client
from instaloader import Instaloader

logger = structlog.get_logger(__name__)
DATALAMA_KEY = os.environ["DATALAMA_KEY"]


class Status(Enum):
    success = "SUCCESS"
    failed = "FAILED"


class Provider(Enum):
    loader = "INSTALOADER"
    api = "INSTAGRAPI"
    datalama = "DATALAMA"


class DataLamaClient:
    def __init__(self, access_key):
        self.base_url = "https://api.datalama.io"
        self.access_key = access_key

    def get_media_data_by_code(
        self, insta_id: str
    ) -> Tuple[Optional[dict], int, Status]:
        headers = {
            "accept": "application/json",
            "x-access-key": self.access_key,
        }
        params = {"code": insta_id}
        response = requests.get(
            f"{self.base_url}/v1/media/by/code", params=params, headers=headers
        )
        if response.status_code == 200:
            return response.json(), response.status_code, Status.success
        return None, response.status_code, Status.failed


class InstaClient:
    def __init__(self, client_type: Enum):
        self._client_type = client_type
        self.client = self._get_client()

    def _get_client(self) -> Any:
        if self._client_type == Provider.datalama:
            return DataLamaClient(DATALAMA_KEY)
        if self._client_type == Provider.loader:
            return Instaloader(quiet=True)
        if self._client_type == Provider.api:
            return Client()

    def download_metadata(self, insta_id: str) -> Optional[Tuple[str, Status]]:
        if self._client_type == Provider.datalama:
            return self.client.get_media_data_by_code(insta_id)

    def download_media_files(
        self, insta_object: dict
    ) -> Tuple[Optional[str], Optional[str], Status]:
        insta_id = insta_object["code"]
        thumbnail_url = insta_object["thumbnail_url"]
        video_url = insta_object["video_url"]

        tmp_thumbnail_path = None
        tmp_video_path = None
        try:
            if thumbnail_url is not None:
                tmp_thumbnail_path = wget.download(thumbnail_url, f"tmp/{insta_id}.jpg")
            if video_url is not None:
                tmp_video_path = wget.download(video_url, f"tmp/{insta_id}.mp4")
        except Exception as e:
            logger.error(f"🤷 Error downloading {insta_id}: {e}.")
            return None, None, Status.failed
        return tmp_thumbnail_path, tmp_video_path, Status.success
