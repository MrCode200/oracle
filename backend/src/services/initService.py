from logging import getLogger

from backend.src.services.entities import Profile
from backend.src.services.utils import register_profile

logger = getLogger('oracle.app')

def init_service():
    from backend.src.database import select_profile

    profiles = select_profile()
    logger.info("Initializing Service, Loading Profiles...")

    for profile_attrs in profiles:
        profile_kwargs: dict[str, any] = {
            "profile_id": profile_attrs.profile_id,
            "profile_name": profile_attrs.profile_name,
            "balance": profile_attrs.balance,
            "stop_loss": profile_attrs.stop_loss,
            "wallet": profile_attrs.wallet,
            "algorithms_settings": profile_attrs.algorithm_settings,
            "fetch_settings": profile_attrs.fetch_settings
        }
        profile: Profile = Profile(**profile_kwargs)
        register_profile(profile)

    logger.info("Initialized Service Successfully, all profiles loaded!")