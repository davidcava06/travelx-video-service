from enum import Enum


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


def from_experience_to_summary(experience: dict) -> dict:
    """Create experience object summary"""
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
