from logging import getLogger

from backend.src.services.entities import ProfileModel, Status

logger = getLogger("oracle.app")


def init_service():
    from backend.src.database import get_profile

    profiles = get_profile()
    logger.info("Initializing Service, Loading Profiles...")

    for profile in profiles:
        ProfileModel(profile)

    logger.info("Initialized Service Successfully, all profiles loaded!")
