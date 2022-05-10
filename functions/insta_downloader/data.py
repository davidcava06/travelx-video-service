from dataclasses import asdict, dataclass
from enum import Enum
from typing import List, Optional
from uuid import uuid4


class ExperienceStatus(Enum):
    pending = "PENDING"
    live = "LIVE"
    draft = "DRAFT"
    hidden = "HIDDEN"
    deleted = "DELETED"


class ExperienceCategory(Enum):
    accommodation = "accommodation"
    activity = "activity"


class ExperienceAudience(Enum):
    volunteering = "volunteering"
    families = "families"
    solo = "solo"
    couples = "couples"
    lgbt = "lgbt"
    corporate = "corporate"
    groups = "groups"
    pets = "pet friendly"
    non_drinkers = "non drinkers"
    seniors = "seniors"
    students = "students"


class ActivityLevel(Enum):
    light = "light"
    moderate = "moderate"
    intense = "intense"
    extreme = "extreme"


class SkillLevel(Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advance = "advance"
    expert = "expert"


class PriceUnit(Enum):
    guest = "guest"
    night = "night"


class DiscountType(Enum):
    min_length = "Length-of-stay discount"
    group_size = "Group size discount"
    early_bird = "Early bird discount"
    custom = "Custom discount"


class CancellationType(Enum):
    forbidden = "No cancellation"
    strict = "7 days or within 24 hours of booking if booking made 48h before the start"
    flexible = "Until 24 hours before the Experience start time for a full refund."


@dataclass
class LocationMeta:
    address: Optional[str] = None
    category: Optional[List[str]] = None
    city: Optional[str] = None
    country: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    zip: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None


@dataclass
class AuthorMeta:
    username: str
    provider: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None


@dataclass
class LanguagesMeta:
    primary: str
    secondary_languages: Optional[str] = None


@dataclass
class GroupSizeMeta:
    default_public_max_size: Optional[int] = None
    default_private_max_size: Optional[int] = None


@dataclass
class AccessibilityMeta:
    environmental_features: Optional[List[str]] = None
    communication_features: Optional[List[str]] = None
    other_features: Optional[List[str]] = None


@dataclass
class GuestRequirementsMeta:
    min_age: Optional[int] = None
    infant_can_attend: Optional[bool] = False
    verified_id_ind: Optional[bool] = False
    other_requirements: Optional[List[str]] = None
    activity_level: Optional[str] = ActivityLevel.light.name
    skill_level: Optional[str] = SkillLevel.beginner.name


@dataclass
class DiscountMeta:
    type: Optional[str] = None
    description: Optional[str] = None
    params: Optional[dict] = None
    percent: Optional[int] = None


@dataclass
class PriceMeta:
    currency: Optional[str] = "GBP"
    value: Optional[int] = 0
    unit: Optional[str] = PriceUnit.guest.name


@dataclass
class AncillaryMeta:
    category: Optional[str] = None
    description: Optional[str] = None
    is_included: Optional[bool] = False
    price: Optional[PriceMeta] = PriceMeta()


@dataclass
class CheckingMeta:
    default_time: Optional[int] = None
    default_min_time: Optional[int] = None
    default_max_time: Optional[int] = None
    window_days: Optional[
        List[str]
    ] = None  # Number of days from now that booking is available
    instructions: Optional[str] = None


@dataclass
class PricingMeta:
    price: Optional[PriceMeta] = PriceMeta()
    price_per_infant: Optional[int] = None
    minimum_private_booking_price: Optional[int] = None
    caregiver_free_ind: Optional[bool] = False
    security_deposit: Optional[int] = None
    discounts: Optional[List[DiscountMeta]] = None


@dataclass
class AmenitiesMeta:
    included_amenities: Optional[List[AncillaryMeta]] = None
    extra_amenities: Optional[List[AncillaryMeta]] = None
    packing_items: Optional[List[str]] = None


@dataclass
class BookingSettingsMeta:
    default_confirmed_booking_lead_hours: Optional[int] = None
    default_booking_lead_hours: Optional[int] = None
    max_hours: Optional[int] = None
    restricted_start_days: Optional[str] = None
    default_private_booking_ind: Optional[bool] = False
    cancellation_policy: Optional[str] = CancellationType.forbidden.name
    rules: Optional[str] = None
    instant_book_ind: Optional[bool] = False
    contact_host_ind: Optional[bool] = True
    check_in: Optional[CheckingMeta] = CheckingMeta()
    check_out: Optional[CheckingMeta] = CheckingMeta()


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
class ExperienceSummary:
    uid: str
    title: Optional[str] = None
    description: Optional[str] = None
    external_url: Optional[str] = None
    status: Optional[str] = ExperienceStatus.pending.name
    category: Optional[str] = ExperienceCategory.activity.name
    audience: Optional[List[str]] = None
    location: Optional[LocationMeta] = LocationMeta()
    is_free: Optional[bool] = True
    is_eco: Optional[bool] = False
    eco_features: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None


@dataclass
class MediaMeta:
    uid: str
    media_type: str = "video"
    media: Optional[VideoMeta] = None
    is_ad: Optional[bool] = False
    ad_url: Optional[str] = None
    external_url: Optional[str] = None
    author: Optional[AuthorMeta] = None
    experience_summary: Optional[ExperienceSummary] = None


@dataclass
class ExperienceMeta:
    uid: str
    parent: Optional[str] = None
    languages: Optional[LanguagesMeta] = LanguagesMeta(primary="English")
    title: Optional[str] = None
    description: Optional[str] = None
    external_url: Optional[str] = None
    status: Optional[str] = ExperienceStatus.pending.name
    category: Optional[str] = ExperienceCategory.activity.name
    audience: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    at_guest_location_ind: Optional[bool] = False
    location: Optional[LocationMeta] = LocationMeta()
    media: Optional[List[VideoMeta]] = None
    author: Optional[AuthorMeta] = None
    is_free: Optional[bool] = True
    is_eco: Optional[bool] = False
    eco_features: Optional[List[str]] = None
    duration_hours: Optional[int] = None
    group_size: Optional[GroupSizeMeta] = GroupSizeMeta()
    guest_requirements: Optional[GuestRequirementsMeta] = GuestRequirementsMeta()
    pricing: Optional[PricingMeta] = PricingMeta()
    amenities: Optional[AmenitiesMeta] = AmenitiesMeta()
    booking_settings: Optional[BookingSettingsMeta] = BookingSettingsMeta()


def create_data_objects(
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
        display_name=insta_object["user"].get("full_name"),
        provider=origin,
    )

    video_meta = VideoMeta(
        storage=video_object["storage"],
        storage_id=video_object["storage_id"],
        uid=video_object["uid"],
        name=video_object["meta"].get("name"),
        hls=video_object["playback"].get("hls"),
        dash=video_object["playback"].get("dash"),
        size=video_object["size"],
        thumbnail=video_object["thumbnail"],
        created_at=video_object["created"],
        uploaded_at=video_object["uploaded"],
    )

    experience_meta = ExperienceMeta(
        uid=str(uuid4()),
        location=location_meta,
        author=author_meta,
        media=[video_meta],
    )
    experience_instance = asdict(experience_meta)

    experience_summary = ExperienceSummary(
        uid=experience_meta.uid,
        title=experience_meta.title,
        description=experience_meta.description,
        location=experience_meta.location,
    )

    media_meta = MediaMeta(
        uid=str(uuid4()),
        media=video_meta,
        author=author_meta,
        experience_summary=experience_summary,
    )
    media_instance = asdict(media_meta)

    return experience_instance, media_instance
