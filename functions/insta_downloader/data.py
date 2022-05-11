from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, List, Optional
from uuid import uuid4

DEFAULT_RANGE = 56


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


class ExperienceRow(Enum):
    uid = 0
    at_guest_location_ind = 1
    audience = 2
    category = 3
    title = 4
    description = 5
    duration_hours = 6
    is_free = 7
    is_eco = 8
    eco_features = 9
    status = 10
    parent = 11
    hashtags = 12
    amenities__extra_amenities = 13
    amenities__included_amenities = 14
    amenities__packing_items = 15
    group_size__default_private_max_size = 16
    group_size__default_public_max_size = 17
    languages__primary = 18
    languages__secondary_languages = 19
    pricing__caregiver_free_ind = 20
    pricing__minimum_private_booking_price = 21
    pricing__price_per_infant = 22
    pricing__security_deposit = 23
    pricing__price__currency = 24
    pricing__price__unit = 25
    pricing__price__value = 26
    guest_requirements__activity_level = 27
    guest_requirements__infant_can_attend = 28
    guest_requirements__min_age = 29
    guest_requirements__skill_level = 30
    location__address = 31
    location__category = 32
    location__city = 33
    location__country = 34
    location__description = 35
    location__instructions = 36
    location__lat = 37
    location__lng = 38
    location__name = 39
    location__phone = 40
    location__website = 41
    location__zip = 42
    booking_settings__cancellation_policy = 43
    booking_settings__contact_host_ind = 44
    booking_settings__default_booking_lead_hours = 45
    booking_settings__default_confirmed_booking_lead_hours = 46
    booking_settings__default_private_booking_ind = 47
    booking_settings__max_hours = 48
    booking_settings__restricted_start_days = 49
    booking_settings__check_in__default_time = 50
    booking_settings__check_in__default_max_time = 51
    booking_settings__check_in__default_min_time = 52
    booking_settings__check_in__instructions = 53
    booking_settings__check_out__default_time = 54
    booking_settings__check_out__instructions = 55

    def __str__(self):
        """So we can pass str(EnumInstance)"""
        return self.name.replace("__", ".")


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
    restricted_start_days: Optional[List[int]] = None
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
    duration_hours: Optional[float] = None
    group_size: Optional[GroupSizeMeta] = GroupSizeMeta()
    guest_requirements: Optional[GuestRequirementsMeta] = GuestRequirementsMeta()
    pricing: Optional[PricingMeta] = PricingMeta()
    amenities: Optional[AmenitiesMeta] = AmenitiesMeta()
    booking_settings: Optional[BookingSettingsMeta] = BookingSettingsMeta()


def create_data_objects(
    insta_object: dict, video_object: dict, origin: Optional[str] = "instagram"
) -> dict:
    location_meta = LocationMeta()
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


def experience_object_to_row(experience_object: dict) -> List[Any]:
    final_tuple_list = []
    element_tuples_list = [element for element in experience_object.items()]

    # Accepting 2 level dict objects
    for element in element_tuples_list:
        if type(element[1]) is dict:
            sub_element_tuples_list = [
                sub_element for sub_element in element[1].items()
            ]
            for sub_element in sub_element_tuples_list:
                field_name = element[0] + "__" + sub_element[0]
                # Filtering for elements in the Google Sheet
                if field_name in ExperienceRow.__members__:
                    order = ExperienceRow[field_name].value
                    final_tuple = (field_name, sub_element[1], order)
                    final_tuple_list.append(final_tuple)
        else:
            if element[0] in ExperienceRow.__members__:
                order = ExperienceRow[element[0]].value
                final_tuple = (element[0], element[1], order)
                final_tuple_list.append(final_tuple)

    # Sorting and cleaning the list
    final_tuple_list.sort(key=lambda val: val[2])
    sorted_list = [element[1] for element in final_tuple_list]
    sorted_list = ["" if value is None else value for value in sorted_list]
    sorted_list = [1 if value is True else value for value in sorted_list]
    sorted_list = [0 if value is False else value for value in sorted_list]
    if len(sorted_list) == DEFAULT_RANGE:
        return sorted_list
    else:
        raise Exception(f"Range does not match {DEFAULT_RANGE}")
