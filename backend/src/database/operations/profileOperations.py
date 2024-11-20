from logging import getLogger

from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from .utils import validate_profile_name
from .. import engine, Profile

logger = getLogger("oracle.app")

Session = sessionmaker(bind=engine)


def add_profile(profile_name: str, balance: float, stop_loss: float, wallet: dict,
                algorithm_settings: dict, fetch_settings: dict) -> Profile:
    """
    Adds a new profile to the database.

    :param profile_name: The name of the profile.
    :param balance: The balance associated with the profile.
    :param stop_loss: The stop-loss setting for the profile.
    :param wallet: The wallet information for the profile.
    :param algorithm_settings: The algorithm settings for the profile.
    :param fetch_settings: The fetch settings for the profile.
    :return: The added profile object.
    """
    validate_profile_name(profile_name)
    session = Session()

    try:
        new_profile = Profile(
            profile_name=profile_name,
            balance=balance,
            stop_loss=stop_loss,
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


def select_profile(profile_id: int = None):
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
            query = session.query(Profile).get(profile_id)
        else:
            query = select(Profile)

        # Execute the query and fetch the results
        results = session.execute(query).scalars().all()
        return results
    finally:
        session.close()


def delete_profile(profile_id: int) -> None:
    """
    Deletes a profile from the database.

    :param profile_id: The ID of the profile to delete.
    """
    session = Session()

    try:
        profile = session.query(Profile).get(profile_id)

        if profile is not None:
            session.delete(profile)
            session.commit()

    except Exception as e:
        logger.error(f"Error deleting profile with ID {profile_id}", exc_info=True)
        session.rollback()
        raise e
    finally:
        session.close()
