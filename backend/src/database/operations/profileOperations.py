from logging import getLogger
from typing import Type

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from backend.src.database import engine, Profile

logger = getLogger("oracle.app")

Session = sessionmaker(bind=engine)


def create_profile(
    profile_name: str, wallet: dict, strategy_settings: dict
) -> Profile | None:
    """
    Creates a new profile in the database.

    :param profile_name: The name of the profile.
    :param wallet: The wallet information for the profile.
    :param strategy_settings: The strategy settings for the profile.

    :return: The newly created profile object.
    """
    session = Session()

    try:
        # Create and add the new profile
        new_profile = Profile(
            profile_name=profile_name,
            wallet=wallet,
            strategy_settings=strategy_settings,
        )
        session.add(new_profile)
        session.commit()

        logger.info(f"Profile {profile_name} created successfully.")
        return new_profile

    except IntegrityError as e:
        logger.error(f"Error creating profile {profile_name}: {e}", exc_info=True)
        session.rollback()
        return None

    finally:
        session.close()


def get_profile(
    profile_id: int = None, profile_name: str = None
) -> Profile | list[Type[Profile]] | None:
    """
    Retrieves a profile from the database based on profile ID or profile name.
    Returns the first matching profile or all profiles if no arguments are passed.

    :param profile_id: The ID of the profile to retrieve. Optional.
    :param profile_name: The name of the profile to retrieve. Optional.

    :return: A Profile object, a list of all Profile objects or None if not found.
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


def update_profile(
    profile_id: int,
    profile_name: str | None = None,
    status: str | None = None,
    wallet: dict | None = None,
    strategy_settings: dict | None = None,
) -> bool:
    """
    Updates a profile in the database.

    :param profile_id: The ID of the profile to update.
    :param profile_name: The new profile name (optional).
    :param status: The new status of the profile (optional).
    :param wallet: The new wallet information for the profile (optional).
    :param strategy_settings: The new strategy settings for the profile (optional).

    :return: True if the profile was updated successfully, False otherwise.
    """
    session = Session()

    try:
        # Retrieve the profile to update
        profile = session.get(Profile, profile_id)
        if not profile:
            logger.warning(f"Profile with ID {profile_id} not found.")
            return False

        # Update values if provided
        if profile_name:
            profile.profile_name = profile_name
        if status is not None:
            profile.status = status
        if wallet:
            profile.wallet = wallet
        if strategy_settings:
            profile.strategy_settings = strategy_settings

        session.commit()
        logger.info(f"Profile {profile_id} updated successfully.")
        return True

    except Exception as e:
        logger.error(f"Error updating profile with ID {profile_id}: {e}", exc_info=True)
        session.rollback()
        return False

    finally:
        session.close()


def delete_profile(
    profile_id: int | None = None, profile_name: str | None = None
) -> bool:
    """
    Deletes a profile from the database.

    :param profile_id: The ID of the profile to delete. Optional.
    :param profile_name: The name of the profile to delete. Optional.

    :return: True if the profile was deleted, False if not found or on error.
    """
    session = Session()

    try:
        # Retrieve the profile to delete
        profile = None
        if profile_id is not None:
            profile = session.get(Profile, profile_id)
        elif profile_name is not None:
            profile = (
                session.query(Profile).filter_by(profile_name=profile_name).first()
            )

        if profile:
            session.delete(profile)
            session.commit()
            logger.info(
                f"Profile {profile_id if profile_id else profile_name} deleted successfully."
            )
            return True
        else:
            logger.warning(
                f"Profile with ID {profile_id} or name {profile_name} not found."
            )
            return False

    except Exception as e:
        logger.error(f"Error deleting profile with ID {profile_id}: {e}", exc_info=True)
        session.rollback()
        return False

    finally:
        session.close()
