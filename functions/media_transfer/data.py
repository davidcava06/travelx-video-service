from enum import Enum


class MediaTxRow(Enum):
    experience_from_uid = 0
    media_uid = 1
    experience_to_uid = 2


def from_experience_to_summary(experience: dict) -> dict:
    """Create experience summary object"""
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
    }
