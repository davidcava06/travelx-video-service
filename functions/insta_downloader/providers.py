import os
from enum import Enum
from typing import Any, Optional, Tuple

import requests
from instagrapi import Client
from instaloader import Instaloader

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

    # TODO: Finish developing for datalama
    def download_post(self, insta_id: str) -> Tuple[str, Status]:
        target_directory = f"/tmp/{insta_id}"
        if self._client_type == Provider.datalama:
            self.download_metadata(insta_id)
        if self._client_type == Provider.loader:
            post = self.client.Post.from_shortcode(self.client.context, insta_id)
            download_ind = self.client.download_post(post, target_directory)
            if not download_ind:
                return "🤷 Error downloading {} from instagram.", Status.failed
        if self._client_type == Provider.api:
            media_pk = self.client.media_pk_from_code(insta_id)
            media = self.client.media_info_a1(media_pk)
            if not media:
                return "🤷 Error downloading {} from instagram.", Status.failed
            print(media)
        return target_directory, Status.success
