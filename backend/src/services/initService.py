from logging import getLogger

from backend.src.services.entities import Profile, Status
from backend.src.utils.registry import profile_registry

logger = getLogger('oracle.app')

def init_service():
    from backend.src.database import select_profile

    profiles = select_profile()
    logger.info("Initializing Service, Loading Profiles...")

    for profile_attrs in profiles:
        profile_kwargs: dict[str, any] = {
            "profile_id": profile_attrs.profile_id,
            "profile_name": profile_attrs.profile_name,
            "status": Status(profile_attrs.status),
            "profile_settings": profile_attrs.profile_settings,
            "wallet": profile_attrs.wallet,
            "algorithms_settings": profile_attrs.algorithm_settings,
            "algorithms_weights": profile_attrs.algorithm_weights,
            "fetch_settings": profile_attrs.fetch_settings
        }
        profile: Profile = Profile(**profile_kwargs)
        profile_registry.register(profile)

    logger.info("Initialized Service Successfully, all profiles loaded!")