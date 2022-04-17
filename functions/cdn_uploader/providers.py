import json
import os
from enum import Enum
from typing import Any, List, Tuple

import requests
import structlog

logger = structlog.get_logger(__name__)

PROJECT_ID = os.environ["PROJECT_ID"]
INFURA_ENDPOINT = "https://ipfs.infura.io:5001"
INFURA_PROJECT_ID = os.environ["INFURA_PROJECT_ID"]
INFURA_PROJECT_SECRET = os.environ["INFURA_PROJECT_SECRET"]


class Provider(Enum):
    drive = "DRIVE"
    infura = "INFURA"


class InfuraClient:
    def __init__(self):
        self.base_url = INFURA_ENDPOINT
        self.infura_project_id = INFURA_PROJECT_ID
        self.infura_project_secret = INFURA_PROJECT_SECRET
        self.base_url = f"https://{PROJECT_ID}.infura-ipfs.io/ipfs/"

    def _upload_file_to_infura_ipfs(self, paths: List[Tuple[str, str]]) -> str:
        """Upload a file to IPFS"""
        logger.info(f"Uploading to {INFURA_ENDPOINT}...")
        files = {file[0]: open(file[1], "rb") for file in paths}
        response = requests.post(
            INFURA_ENDPOINT + "/api/v0/add?pin=true",
            files=files,
            auth=(INFURA_PROJECT_ID, INFURA_PROJECT_SECRET),
        )

        dec = json.JSONDecoder()
        i = 0
        response_list = []
        while i < len(response.text):
            data, s = dec.raw_decode(response.text[i:])
            i += s + 1
            name = "-".join(data["Name"].split("-")[1:])
            response_list.append((name, data["Hash"]))
        return response_list


class CDNClient:
    def __init__(self, client_type: Enum):
        self._client_type = client_type
        self.client = self._get_client()
        self.base_url = self.client.base_url

    def _get_client(self) -> Any:
        if self._client_type == Provider.infura:
            return InfuraClient()

    def upload_files(self, files: List[dict]) -> List[dict]:
        """Upload a file to the CDN"""
        logger.info(f"Uploading to {self._client_type}...")
        if self._client_type == Provider.infura:
            return self.client._upload_file_to_infura_ipfs(files)
        return None
