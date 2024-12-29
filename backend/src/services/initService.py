from logging import getLogger

from src.services.entities import Profile, Status
from src.utils import load_config
from src.utils.registry import profile_registry

logger = getLogger("oracle.app")


def init_service():
    from src.database import get_profile, ProfileDTO

    profiles: list[ProfileDTO] = get_profile()
    logger.info("Initializing Service, Loading Profiles...")

    if profiles is None:
        return

    for profile in profiles:
        Profile(profile)

    logger.info("Initialized Service Successfully, all profiles loaded!")
