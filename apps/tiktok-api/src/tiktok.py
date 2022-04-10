import os

import structlog
import wget
from TikTokApi import TikTokApi

from src.extensions import storage as storage_client

logger = structlog.get_logger(__name__)


def get_video_from_url(api: TikTokApi, url: str) -> dict:
    """Get Video from TikTok"""
    video = api.video(url=url)

    # Get data
    video_data = video.info_full()

    # Get video
    video_bytes = video.bytes()
    download_video(video_data, video_bytes)
    download_thumbnail(video_data, video_bytes)

    return video_data


def download_thumbnail(video_data: dict):
    tmp_path_f = None
    video_id = video_data["itemInfo"]["itemStruct"]["id"]
    thumb_url = video_data["itemInfo"]["itemStruct"]["video"]["cover"]

    root = os.path.dirname(os.path.abspath(__file__))
    tmp_path = "/tmp/" + f"{video_id}.jpg"
    tmp_path_f = os.path.join(root, tmp_path)

    wget.download(thumb_url, tmp_path_f)

    file_name = f"tiktok/{video_id}/thumbnail.jpg"
    storage_client._upload_sync(tmp_path_f, file_name)


def download_video(video_data: dict, video_bytes: bytes) -> dict:
    video_id = video_data["itemInfo"]["itemStruct"]["id"]

    root = os.path.dirname(os.path.abspath(__file__))
    temp_file_name = f"/tmp/{video_id}.mp4"
    tmp_path_f = os.path.join(root, temp_file_name)
    with open(tmp_path_f, "wb") as out_file:
        out_file.write(video_bytes)

    file_name = f"tiktok/{video_id}/video.mp4"
    if storage_client._upload_sync(tmp_path_f, file_name):
        storage_client._upload_document_to_firestore(video_data, video_id)
