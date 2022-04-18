from dataclasses import asdict, dataclass
from typing import Optional
from uuid import uuid4


@dataclass
class LocationMeta:
    address: Optional[str] = None
    category: Optional[str] = None
    city: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    zip: Optional[str] = None


@dataclass
class AuthorMeta:
    username: str
    provider: Optional[str] = None


@dataclass
class VideoMeta:
    storage: str
    uid: str
    name: str
    hls: str
    dash: Optional[str] = None
    storage_id: Optional[str] = None
    size: Optional[int] = None
    thumbnail: Optional[str] = None
    created_at: Optional[str] = None
    uploaded_at: Optional[str] = None


@dataclass
class ExperienceMeta:
    uid: str
    video: dict
    location: Optional[LocationMeta] = None
    author: Optional[AuthorMeta] = None


def create_data_object(
    tiktok_object: dict, video_object: dict, origin: Optional[str] = "tiktok"
) -> dict:
    location_meta = None
    tiktok_object = tiktok_object["itemInfo"]["itemStruct"]
    if "location" in tiktok_object:
        location_meta = LocationMeta(
            address=tiktok_object["location"].get("address"),
            category=tiktok_object["location"].get("category"),
            city=tiktok_object["location"].get("city"),
            lat=tiktok_object["location"].get("lat"),
            lng=tiktok_object["location"].get("lng"),
            name=tiktok_object["location"].get("name"),
            phone=tiktok_object["location"].get("phone"),
            website=tiktok_object["location"].get("website"),
            zip=tiktok_object["location"].get("zip"),
        )
    author_meta = AuthorMeta(
        username=tiktok_object["author"].get("nickname"),
        provider=origin,
    )

    video_meta = VideoMeta(
        storage=video_object["storage"],
        storage_id=video_object["uid"],
        uid=video_object["uid"],
        name=video_object["meta"].get("name"),
        hls=video_object["playback"].get("hls"),
        dash=video_object["playback"].get("hls"),
        size=video_object["size"],
        thumbnail=video_object["thumbnail"],
        created_at=video_object["created"],
        uploaded_at=video_object["uploaded"],
    )

    return asdict(
        ExperienceMeta(
            uid=str(uuid4()),
            location=location_meta,
            author=author_meta,
            video=video_meta,
        )
    )
