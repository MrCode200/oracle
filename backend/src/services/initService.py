from logging import getLogger

from src.services.entities import Profile, Status
from src.utils import load_config
from src.utils.registry import profile_registry

logger = getLogger("oracle.app")


def init_service():
    from src.database import get_profile

    profiles = get_profile()
    logger.info("Initializing Service, Loading Profiles...")

    for profile in profiles:
        Profile(profile)

    PROFILE_CONFIG: dict[str, any] = load_config("PROFILE_CONFIG")
    if PROFILE_CONFIG["continue_status"]:
        for profile in profile_registry.get():
            if profile.status in [Status.ACTIVE, Status.PAPER_TRADING]:
                profile.activate(run_on_start = False)

    logger.info("Initialized Service Successfully, all profiles loaded!")
