import os
import time
from typing import Optional, Tuple
from uuid import uuid4

import requests
import structlog
import wget
from TikTokApi import TikTokApi

from src.data import create_data_objects, experience_object_to_row
from src.extensions import cdn as cdn_client
from src.extensions import storage as storage_client

logger = structlog.get_logger(__name__)
NO_WATERMARK_BASE_URL = "https://www.tikwm.com"


def get_video_from_url(api: TikTokApi, url: str) -> dict:
    """Get Video from TikTok"""
    # Get video
    tmp_video_path, video_data = download_video(api, url)
    download_thumbnail(video_data)

    # Store in CDN
    data_object = upload_to_cdn(tmp_video_path, video_data)

    return video_data, data_object


def download_thumbnail(video_data: dict):
    logger.info("Gone into thumbnail...")
    tmp_path_f = None
    if "cover" in video_data.keys():
        video_id = video_data["id"]
        thumb_url = video_data["cover"]
    else:
        video_id = video_data["itemInfo"]["itemStruct"]["id"]
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


def download_video(api: TikTokApi, url: Optional[str] = None) -> Tuple[str, dict]:
    root = os.path.dirname(os.path.abspath(__file__))
    try:
        # No Watermark
        video_data = fetch_video_data(url)
        video_id = video_data["id"]
        hdplay = video_data.get("hdplay")
        video_url = hdplay if hdplay is not None else video_data.get("play")

        temp_file_name = f"/tmp/{video_id}.mp4"
        tmp_path_f = os.path.join(root, temp_file_name)
        wget.download(video_url, tmp_path_f)
    except Exception as e:
        # With Watermark
        logger.error(e)
        video = api.video(url=url)
        video_data = video.info_full()
        video_bytes = video.bytes()

        video_id = video_data["itemInfo"]["itemStruct"]["id"]
        temp_file_name = f"/tmp/{video_id}.mp4"
        tmp_path_f = os.path.join(root, temp_file_name)
        with open(tmp_path_f, "wb") as out_file:
            out_file.write(video_bytes)

    file_name = f"tiktok/{video_id}/video.mp4"
    if storage_client._upload_sync(tmp_path_f, file_name):
        storage_client._upload_document_to_firestore(video_data, video_id)
    return tmp_path_f, video_data


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

    logger.info(f"Creating Experience, Video and Post for {tiktok_id}...")
    (
        experience_instance,
        post_instance,
        video_instance,
    ) = create_data_objects(tiktok_object, video_object)
    experience_uid = experience_instance["uid"]

    storage_client._upload_document_to_firestore(
        video_instance, video_instance["uid"], "media"
    )
    storage_client._upload_document_to_firestore(
        experience_instance, experience_instance["uid"], "experiences"
    )
    storage_client._upload_document_to_firestore(
        post_instance, post_instance["uid"], "posts"
    )
    logger.info(f"Adding Experience {experience_uid} to Sheet...")
    # Create array from experience instance
    experience_row = experience_object_to_row(experience_instance)
    # Update spreadsheet
    storage_client._update_spreadsheet([experience_row])

    return experience_instance


def fetch_video_data(url: str) -> dict:
    params = dict(hd=1, url=url)
    response = requests.get(f"{NO_WATERMARK_BASE_URL}/api", params=params)
    if response.status_code != 200:
        raise Exception(f"Failed request to {NO_WATERMARK_BASE_URL} for {url}")
    response = response.json()
    data = response.get("data")
    return data
