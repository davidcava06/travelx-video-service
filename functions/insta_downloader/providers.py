from enum import Enum
from typing import Any, Optional, Tuple

from instagrapi import Client
from instaloader import Instaloader


class Status(Enum):
    success = "SUCCESS"
    failed = "FAILED"


class Provider(Enum):
    loader = "INSTALOADER"
    api = "INSTAGRAPI"


class InstaClient:
    def __init__(self, client_type: Enum):
        self._client_type = client_type
        self.client = self._get_client()

    def _get_client(self) -> Any:
        if self._client_type == Provider.loader:
            return Instaloader(quiet=True)
        if self._client_type == Provider.api:
            return Client()

    def download_post(self, insta_id: str) -> Optional[Tuple[str, Status]]:
        target_directory = f"/tmp/{insta_id}"
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
