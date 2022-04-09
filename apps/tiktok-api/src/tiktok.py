import structlog
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

    return video_data


def download_video(video_data: dict, video_bytes: bytes) -> dict:
    video_id = video_data["itemInfo"]["itemStruct"]["id"]
    file_name = f"tiktok/{video_id}/video.mp4"
    temp_file_name = f"/tmp/{video_id}.mp4"
    with open(temp_file_name, "wb") as out_file:
        out_file.write(video_bytes)

    # TODO: Save thumbnail
    if storage_client._upload_sync(temp_file_name, file_name):
        storage_client._upload_document_to_firestore(video_data, video_id)
