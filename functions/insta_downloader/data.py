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
    insta_object: dict, video_object: dict, origin: Optional[str] = "instagram"
) -> dict:
    location_meta = None
    if insta_object["location"] is not None:
        location_meta = LocationMeta(
            address=insta_object["location"].get("address"),
            category=insta_object["location"].get("category"),
            city=insta_object["location"].get("city"),
            lat=insta_object["location"].get("lat"),
            lng=insta_object["location"].get("lng"),
            name=insta_object["location"].get("name"),
            phone=insta_object["location"].get("phone"),
            website=insta_object["location"].get("website"),
            zip=insta_object["location"].get("zip"),
        )
    author_meta = AuthorMeta(
        username=insta_object["user"].get("username"),
        provider=origin,
    )

    video_meta = VideoMeta(
        storage=video_object["storage"],
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
