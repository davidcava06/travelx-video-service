from dataclasses import asdict, dataclass
from enum import Enum
from typing import List, Optional
from uuid import uuid4


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
    luxury = "luxury"
    adults = "adults"
    vegan = "vegan"


class GuideStatus(Enum):
    pending = "PENDING"
    live = "LIVE"
    draft = "DRAFT"
    hidden = "HIDDEN"
    deleted = "DELETED"


class GuideRow(Enum):
    title = 0
    description = 1
    is_collaborative = 2
    is_public = 3
    image_url = 4
    experience_uids = 5

    def __str__(self):
        """So we can pass str(EnumInstance)"""
        return self.name.replace("__", ".")


@dataclass
class Image:
    url: str
    height: Optional[int]
    width: Optional[int]


@dataclass
class AuthorMeta:
    username: Optional[str] = "boon"
    provider: Optional[str] = "boon"
    display_name: Optional[str] = "BOON"
    avatar_url: Optional[str] = None


@dataclass
class Guide:
    guide_uid: str
    snapshot_uid: str
    snapshot_from_uid: Optional[str] = None
    owner: Optional[float] = AuthorMeta()
    title: Optional[str] = None
    description: Optional[str] = None
    external_url: Optional[str] = None
    is_public: Optional[bool] = False
    is_collaborative: Optional[bool] = False
    status: Optional[str] = GuideStatus.pending.name
    images: Optional[Image] = []
    experience_summaries: Optional[Image] = []
    created_at: Optional[float] = None
    updated_at: Optional[str] = None
    deleted_at: Optional[str] = None


def create_guide_object(
    guide_input: dict, images: List[dict], experience_summaries: List[dict]
) -> dict:
    guide = Guide(
        guide_uid=str(uuid4()),
        snapshot_uid=str(uuid4()),
        title=guide_input.get(GuideRow.title.name),
        description=guide_input.get(GuideRow.description.name),
        is_public=guide_input.get(GuideRow.is_public.name),
        is_collaborative=guide_input.get(GuideRow.is_collaborative.name),
        images=images,
        experience_summaries=experience_summaries,
        # TODO: Timestamps
    )
    guide_instance = asdict(guide)
    return guide_instance


def from_experience_to_summary_v2(experience: dict) -> dict:
    """Create experience summary object"""
    all_media = experience.get("media")
    media = [all_media[0]] if len(all_media) > 0 else None  # Just 1 for MVP
    return {
        "experience_summary.uid": experience.get("uid"),
        "experience_summary.title": experience.get("title"),
        "experience_summary.description": experience.get("description"),
        "experience_summary.external_url": experience.get("external_url"),
        "experience_summary.status": experience.get("status"),
        "experience_summary.category": experience.get("category"),
        "experience_summary.audience": experience.get("audience"),
        "experience_summary.location": experience.get("location"),
        "experience_summary.is_free": experience.get("is_free"),
        "experience_summary.is_eco": experience.get("is_eco"),
        "experience_summary.eco_features": experience.get("eco_features"),
        "experience_summary.hashtags": experience.get("hashtags"),
        "experience_summary.media": media,
    }
