import requests
import structlog
from requests.structures import CaseInsensitiveDict

logger = structlog.get_logger(__name__)


class CFClient:
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app, *args, **kwargs) -> None:
        self.base_url = "https://api.cloudflare.com/client/v4/accounts"
        self.account = app.config.get("CF_ACCOUNT")
        self.token = app.config.get("CF_TOKEN")

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
