from logging import getLogger
from typing import Type

logger = getLogger("oracle.app")

_PROFILE_REGISTRY: dict[int, 'Profile'] = {}


def register_profile(profile: 'Profile'):
    if profile.profile_id in _PROFILE_REGISTRY:
        logger.error(f"Profile with id {profile.profile_id} already exists", exc_info=True)
        return
    logger.debug(f"Added Profile with id: {profile.profile_id}; to registry")
    _PROFILE_REGISTRY[profile.profile_id] = profile


def remove_profile(profile_id: int):
    if profile_id not in _PROFILE_REGISTRY:
        logger.error(f"Profile with id {profile_id} does not exist", exc_info=True)
        return
    logger.debug(f"Removed Profile with id: {profile_id}; from PROFILE_REGISTRY")
    del _PROFILE_REGISTRY[profile_id]


def get_profile(profile_id: int) -> Type | None:
    """
    Retrieves profile by id.

    :param profile_id: The id for the profile to retrieve
    :return: The Profile Type or None if profile_id was not registered.
    """
    if profile_id not in _PROFILE_REGISTRY:
        logger.error(f"Profile with id {profile_id} does not exist", exc_info=True)
        return
    logger.debug(f"Retrieved Profile with id: {profile_id}; from PROFILE_REGISTRY")
    return _PROFILE_REGISTRY[profile_id]


def yield_profiles():
    for profile in _PROFILE_REGISTRY.values():
        logger.debug(f"Yielded Profile with id: {profile.profile_id}; from PROFILE_REGISTRY")
        yield profile