import os
from enum import Enum
from typing import Any, Optional, Tuple

import requests
import structlog
import wget
from instagrapi import Client
from instaloader import Instaloader, Post
from requests.structures import CaseInsensitiveDict

logger = structlog.get_logger(__name__)
DATALAMA_KEY = os.environ["DATALAMA_KEY"]
CF_ACCOUNT = os.environ["CF_ACCOUNT"]
CF_TOKEN = os.environ["CF_TOKEN"]
RAPIDAPI_KEY = os.environ["RAPIDAPI_KEY"]


class Status(Enum):
    success = "SUCCESS"
    failed = "FAILED"


class Provider(Enum):
    loader = "INSTALOADER"
    api = "INSTAGRAPI"
    datalama = "DATALAMA"
    rapidapi = "RAPIDAPI"


class InstaloaderClient:
    def __init__(self):
        self._instance = None

    @property
    def instance(self):
        if self._instance is None:
            self._instance = Instaloader()
            self._instance.login("itscamillelondon", "031060CaPi06")
        return self._instance

    def get_media_data_by_code(
        self, insta_id: str
    ) -> Tuple[Optional[dict], int, Status]:
        try:
            post = Post.from_shortcode(self.instance.context, insta_id)
            return post, 200, Status.success
        except Exception:
            return None, 404, Status.failed


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


class RapidApiClient:
    def __init__(self, access_key):
        self.base_url = "https://instagram-data1.p.rapidapi.com"
        self.access_key = access_key

    def get_media_data_by_code(
        self, insta_id: str
    ) -> Tuple[Optional[dict], int, Status]:
        headers = {
            "X-RapidAPI-Key": self.access_key,
            "X-RapidAPI-Host": "instagram-data1.p.rapidapi.com",
        }
        params = {"post": f"https://www.instagram.com/p/{insta_id}"}
        response = requests.get(
            f"{self.base_url}/post/info", params=params, headers=headers
        )
        if response.status_code == 200:
            return response.json(), response.status_code, Status.success
        return None, response.status_code, Status.failed


class InstagrapiClient:
    def __init__(self):
        self.client = Client()

    def get_media_data_by_code(
        self, insta_id: str
    ) -> Tuple[Optional[dict], int, Status]:
        media_pk = self.client.media_pk_from_code(insta_id)
        response = self.client.media_info(media_pk)
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
            return InstaloaderClient()
        if self._client_type == Provider.api:
            return DataLamaClient()
        if self._client_type == Provider.rapidapi:
            return RapidApiClient(RAPIDAPI_KEY)

    def download_metadata(self, insta_id: str) -> Optional[Tuple[str, Status]]:
        return self.client.get_media_data_by_code(insta_id)

    def download_media_files(
        self, insta_object: dict
    ) -> Tuple[Optional[str], Optional[str], Status]:
        insta_id = (
            insta_object.get("code")
            if insta_object.get("code") is not None
            else insta_object.get("shortcode")
        )
        thumbnail_url = (
            insta_object.get("thumbnail_url")
            if insta_object.get("thumbnail_url") is not None
            else insta_object.get("image_versions2")["candidates"][0]["url"]
        )
        video_url = (
            insta_object.get("video_url")
            if insta_object.get("video_url") is not None
            else insta_object.get("video_versions")[0]["url"]
        )

        tmp_thumbnail_path_f = None
        tmp_video_path_f = None
        root = os.path.dirname(os.path.abspath(__file__))
        try:
            if thumbnail_url is not None:
                tmp_thumbnail_path = "/tmp/" + f"{insta_id}.jpg"
                tmp_thumbnail_path_f = os.path.join(root, tmp_thumbnail_path)
                wget.download(thumbnail_url, tmp_thumbnail_path_f)
            if video_url is not None:
                tmp_video_path = "/tmp/" + f"{insta_id}.mp4"
                tmp_video_path_f = os.path.join(root, tmp_video_path)
                wget.download(video_url, tmp_video_path_f)
        except Exception as e:
            logger.error(f"🤷 Error downloading {insta_id}: {e}.")
            raise e
        return tmp_thumbnail_path_f, tmp_video_path_f, Status.success


class CFClient:
    def __init__(self, cf_account: str = CF_ACCOUNT, cf_token: str = CF_TOKEN):
        self.base_url = "https://api.cloudflare.com/client/v4/accounts"
        self.account = cf_account
        self.token = cf_token

    def upload_files(self, file_path: str, file_name: str) -> dict:
        """Upload a file to CloudFlare Stream"""
        logger.info(f"Uploading to {self.base_url}...")

        headers = {"Authorization": f"Bearer {self.token}"}
        files = [
            ("file", (file_name, open(file_path, "rb"), "application/octet-stream"))
        ]

        response = requests.post(
            f"{self.base_url}/{self.account}/stream",
            files=files,
            headers=headers,
        )
        results = response.json()
        return results["result"]

    def get_video_by_name(self, file_name: str) -> dict:
        """Get Video from CloudFlare Stream"""
        logger.info(f"Fetching from {self.base_url}...")

        headers = CaseInsensitiveDict()
        headers["Authorization"] = f"Bearer {self.token}"
        headers["Content-Type"] = "application/json"

        response = requests.get(
            f"{self.base_url}/{self.account}/stream?search={file_name}",
            headers=headers,
        )
        results = response.json()
        return results["result"]
