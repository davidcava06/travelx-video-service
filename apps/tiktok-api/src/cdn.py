import requests
import structlog

from requests.structures import CaseInsensitiveDict

logger = structlog.get_logger(__name__)


class CFClient:
    def __init__(self, cf_account: str, cf_token: str):
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
        return response

    def get_video_by_name(self, file_name: str) -> dict:
        """Get Video from CloudFlare Stream"""
        logger.info(f"Uploading to {self.base_url}...")

        headers = CaseInsensitiveDict()
        headers["Authorization"] = f"Bearer {self.token}"
        headers["Content-Type"] = "application/json"

        response = requests.get(
            f"{self.base_url}/{self.account}/stream?search={file_name}",
            headers=headers,
        )
        return response
