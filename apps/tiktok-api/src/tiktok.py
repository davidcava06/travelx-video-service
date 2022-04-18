import os
import time
from uuid import uuid4

import structlog
import wget
from TikTokApi import TikTokApi

from src.data import create_data_object
from src.extensions import cdn as cdn_client
from src.extensions import storage as storage_client

logger = structlog.get_logger(__name__)


def get_video_from_url(api: TikTokApi, url: str) -> dict:
    """Get Video from TikTok"""
    video = api.video(url=url)

    # Get data
    video_data = video.info_full()

    # Get video
    video_bytes = video.bytes()
    tmp_video_path = download_video(video_data, video_bytes)
    download_thumbnail(video_data)

    # Store in CDN
    data_object = upload_to_cdn(tmp_video_path, video_data)

    return video_data, data_object


def download_thumbnail(video_data: dict):
    tmp_path_f = None
    video_id = video_data["itemInfo"]["itemStruct"]["id"]
    logger.info(f"Gone into thumbnail: {video_id}")
    thumb_url = video_data["itemInfo"]["itemStruct"]["video"]["cover"]
    logger.info(f"Downloading {thumb_url}...")
    root = os.path.dirname(os.path.abspath(__file__))
    tmp_path = "/tmp/" + f"{video_id}.jpg"
    tmp_path_f = os.path.join(root, tmp_path)
    try:
        wget.download(thumb_url, tmp_path_f)
        file_name = f"tiktok/{video_id}/thumbnail.jpg"
        storage_client._upload_sync(tmp_path_f, file_name)
    except Exception as e:
        logger.error(e)


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
        return tmp_path_f


def upload_to_cdn(tmp_video_path: str, tiktok_object: dict) -> dict:
    """Upload to CloudFlare"""
    tiktok_id = tiktok_object["itemInfo"]["itemStruct"]["id"]
    logger.info(f"Uploading to CloudFlare for {tiktok_id}...")
    response = cdn_client.upload_files(tmp_video_path, tiktok_id)
    ready_to_stream = response["readyToStream"]
    while ready_to_stream is not True:
        time.sleep(2)
        response = cdn_client.get_video_by_name(tiktok_id)
        ready_to_stream = response[0]["readyToStream"]
        logger.info(f"Job status: {ready_to_stream}")

    logger.info(f"Formatting data object for {tiktok_id}...")
    video_object = response[0]
    video_object["storage"] = "cloudflare"
    video_object["storage_id"] = video_object["uid"]
    video_object["uid"] = str(uuid4())
    data_object = create_data_object(tiktok_object, video_object)

    logger.info(f"Storing data object for {tiktok_id}...")
    storage_client._upload_document_to_firestore(
        data_object, data_object["uid"], "experiences"
    )
    return data_object
