from typing import Type
from json import loads
from logging import getLogger

from backend.src.services.entities import Profile
from backend.src.services.utils import register_profile

logger = getLogger('oracle.app')

def init_service():
    from backend.src.database import select_profile

    logger.info("Initializing Service, Loading Profiles...")
    results = select_profile()

    for profile_attrs in results:
        print("""Profile: """, profile_attrs)
        profile_kwargs: dict[str, any] = {
            "profile_id": profile_attrs[0],
            "profile_name": profile_attrs[1],
            "balance": profile_attrs[2],
            "stop_loss": profile_attrs[3],
            "wallet": loads(profile_attrs[4]),
            "algorithms_settings": loads(profile_attrs[5]),
            "fetch_settings": loads(profile_attrs[6])
        }
        profile: Type[Profile] = Profile(**profile_kwargs)
        register_profile(profile)

    logger.info("Initialized Service Successfully, all profiles loaded!")