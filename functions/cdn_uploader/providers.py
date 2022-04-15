import json
import os
from typing import List

import requests
import structlog

logger = structlog.get_logger(__name__)

INFURA_ENDPOINT = "https://ipfs.infura.io:5001"
INFURA_PROJECT_ID = os.environ["INFURA_PROJECT_ID"]
INFURA_PROJECT_SECRET = os.environ["INFURA_PROJECT_SECRET"]


def upload_file_to_infura_ipfs(files: dict) -> str:
    """Upload a file to the CDN"""
    logger.info(f"Uploading to {INFURA_ENDPOINT}...")
    response = requests.post(
        INFURA_ENDPOINT + "/api/v0/add",
        files=files,
        auth=(INFURA_PROJECT_ID, INFURA_PROJECT_SECRET),
    )
    breakpoint()
    dec = json.JSONDecoder()
    i = 0
    response_list = []
    while i < len(response.text):
        data, s = dec.raw_decode(response.text[i:])
        i += s + 1
        response_list.append((data["Name"], data["Hash"]))
    return response_list


def upload_hls_to_ipfs_from_gcs(
    ts_file_paths: List[str], ts_m3u8_paths: List[str]
) -> str:
    """Upload HLS to IPFS"""
    logger.info("Uploading HLS to IPFS...")
    # Upload ts files to CDN
    # Get the hashes of the ts file
    ts_files = {}
    for ts_file_path in ts_file_paths:
        ts_files[ts_file_path] = ts_file_path
    ts_hash_list = upload_file_to_infura_ipfs(ts_files)

    # Change the sd and hd playlist files to point to the new hashes
    # Upload the new playlist files to CDN
    # Change the manifest file to point to the new hashes of the playlist files
    # Upload the new manifest file to CDN
    # Return the URL of the manifest file
    manifest_result = None
    cdn_url = f"https://cloudflare-ipfs.com/ipfs/${manifest_result.hash}?filename=manifest.m3u8"  # NOQA
    return manifest_result, cdn_url
