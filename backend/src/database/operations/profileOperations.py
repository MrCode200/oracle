from logging import getLogger

from sqlalchemy.orm import sessionmaker

from .. import engine, Profile

logger = getLogger("oracle.app")

Session = sessionmaker(bind=engine)


def add_profile(profile_name: str, profile_settings: dict[str, float], wallet: dict,
                algorithm_settings: dict, fetch_settings: dict) -> Profile:
    """
    Adds a new profile to the database.

    :param profile_name: The name of the profile.
    :param profile_settings: The setting for the profile.
    :param wallet: The wallet information for the profile.
    :param algorithm_settings: The algorithm settings for the profile.
    :param fetch_settings: The fetch settings for the profile.
    :return: The added profile object.
    """
    session = Session()

    try:
        new_profile = Profile(
            profile_name=profile_name,
            stop_loss=profile_settings,
            wallet=wallet,
            algorithm_settings=algorithm_settings,
            fetch_settings=fetch_settings
        )

        session.add(new_profile)
        session.commit()

        return new_profile
    except Exception as e:
        logger.error(f"Error adding profile {profile_name}", exc_info=True)
        session.rollback()

    finally:
        session.close()


def select_profile(profile_id: int = None, profile_name: str = None):
    """
    Loads a profile from the database based on profile ID or profile name.
    If no arguments are passed it will return all profiles.

    :param profile_id: The ID of the profile to load. Optional if profile_name is provided.
    :param profile_name: The name of the profile to load. Optional if profile_id is provided.
    :return: A result set containing the profile data.
    """
    session = Session()

    try:
        if profile_id is not None:
            return session.get(Profile, profile_id)
        elif profile_name is not None:
            return session.query(Profile).filter_by(profile_name=profile_name).first()
        else:
            return session.query(Profile).all()
    finally:
        session.close()


def update_profile(profile_id: int, profile_name: str, profile_settings: dict, wallet: dict,
                   algorithm_settings: dict, fetch_settings: dict) -> None:
    """
    Updates a profile in the database.

    :param profile_id: The ID of the profile to update.
    :param profile_name: The name of the profile.
    :param profile_settings: The setting for the profile.
    :param wallet: The wallet information for the profile.
    :param algorithm_settings: The algorithm settings for the profile.
    :param fetch_settings: The fetch settings for the profile.
    """
    session = Session()

    try:
        session.get(Profile, profile_id).update({
            "profile_name": profile_name,
            "profile_settings": profile_settings,
            "wallet": wallet,
            "algorithm_settings": algorithm_settings,
            "fetch_settings": fetch_settings
        })
        session.commit()
    except Exception:
        logger.error(f"Error updating profile with ID {profile_id}", exc_info=True)
        session.rollback()
    finally:
        session.close()


def delete_profile(profile_id: int = None, profile_name: str = None) -> None:
    """
    Deletes a profile from the database.

    :param profile_id: The ID of the profile to load. Optional if profile_name is provided.
    :param profile_name: The name of the profile to load. Optional if profile_id is provided.
    """
    session = Session()
    profile: Profile | None = None

    try:
        if profile_id is not None:
            profile = session.get(Profile, profile_id)
        elif profile_name is not None:
            profile = session.query(Profile).filter_by(profile_name=profile_name).first()

        if profile is not None:
            session.delete(profile)
            session.commit()
        else:
            logger.warning(f"Profile with {profile_id=}; {profile_name=} does not exist")

    except Exception as e:
        logger.error(f"Error deleting profile with ID {profile_id}", exc_info=True)
        session.rollback()
        raise e
    finally:
        session.close()
