from logging import getLogger
from typing import Type

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from backend.src.database import ProfileModel, ProfileDTO, engine

logger = getLogger("oracle.app")

Session = sessionmaker(bind=engine)


def convert_to_dto(profile: ProfileModel) -> ProfileDTO | None:
    """
    Helper function to convert an IndicatorModel to an IndicatorDTO.
    Or return None if the profile is not found.
    """
    if not profile:
        return None
    return ProfileDTO(
        id=profile.id,
        name=profile.name,
        status=profile.status,
        balance=profile.balance,
        wallet=profile.wallet,
        strategy_settings=profile.strategy_settings
    )


def create_profile(
        name: str, balance: float, wallet: dict, strategy_settings: dict
) -> ProfileDTO | None:
    """
    Creates a new profile in the database.

    :param name: The name of the profile.
    :param balance: The balance of the profile.
    :param wallet: The wallet information for the profile.
    :param strategy_settings: The strategy settings for the profile.

    :return: The newly created profile object.
    """
    session = Session()

    try:
        # Create and add the new profile
        new_profile = ProfileModel(
            name=name,
            balance=balance,
            wallet=wallet,
            strategy_settings=strategy_settings,
        )

        session.add(new_profile)
        session.commit()

        logger.info(f"Profile {name} created successfully.")
        return convert_to_dto(new_profile)

    except IntegrityError as e:
        logger.error(f"Error creating profile {name}: {e}", exc_info=True)
        session.rollback()
        return None

    finally:
        session.close()


def get_profile(
        id: int = None, name: str = None
) -> ProfileDTO | list[ProfileDTO] | None:
    """
    Retrieves a profile from the database based on profile ID or profile name.
    Returns the first matching profile or all profiles if no arguments are passed.

    :param id: The ID of the profile to retrieve. Optional.
    :param name: The name of the profile to retrieve. Optional.

    :return: A Profile object, a list of all Profile objects or None if not found.
    """
    session = Session()

    try:
        if id is not None:
            profile: Type[ProfileModel] | None = session.get(ProfileModel, id)
            return convert_to_dto(profile)

        elif name is not None:
            profile: Type[ProfileModel] | None = session.query(ProfileModel).filter_by(name=name).first()
            return convert_to_dto(profile)
        else:
            profiles: list[Type[ProfileModel]] = session.query(ProfileModel).all()
            return [convert_to_dto(profile) for profile in profiles]

    except Exception as e:
        logger.error(f"Error retrieving Profile: {e}", exc_info=True)
        return None

    finally:
        session.close()


def update_profile(
        id: int,
        name: str | None = None,
        status: str | None = None,
        wallet: dict | None = None,
        strategy_settings: dict | None = None,
) -> bool:
    """
    Updates a profile in the database.

    :param id: The ID of the profile to update.
    :param name: The new profile name (optional).
    :param status: The new status of the profile (optional).
    :param wallet: The new wallet information for the profile (optional).
    :param strategy_settings: The new strategy settings for the profile (optional).

    :return: True if the profile was updated successfully, False otherwise.
    """
    session = Session()

    try:
        # Retrieve the profile to update
        profile = session.get(ProfileModel, id)
        if not profile:
            logger.warning(f"Profile with ID {id} not found.")
            return False

        # Update values if provided
        if name:
            profile.name = name
        if status is not None:
            profile.status = status
        if wallet:
            profile.wallet = wallet
        if strategy_settings:
            profile.strategy_settings = strategy_settings

        session.commit()
        logger.info(f"Profile {id} updated successfully.")
        return True

    except Exception as e:
        logger.error(f"Error updating profile with ID {id}: {e}", exc_info=True)
        session.rollback()
        return False

    finally:
        session.close()


def delete_profile(
        id: int | None = None, name: str | None = None
) -> bool:
    """
    Deletes a profile from the database.

    :param id: The ID of the profile to delete. Optional.
    :param name: The name of the profile to delete. Optional.

    :return: True if the profile was deleted, False if not found or on error.
    """
    session = Session()

    try:
        profile = None
        if id is not None:
            profile = session.get(ProfileModel, id)
        elif name is not None:
            profile = (
                session.query(ProfileModel).filter_by(name=name).first()
            )

        if profile:
            session.delete(profile)
            session.commit()
            logger.info(
                f"Profile {id if id else name} deleted successfully."
            )
            return True
        else:
            logger.warning(
                f"Profile with ID {id} or name {name} not found."
            )
            return False

    except Exception as e:
        logger.error(f"Error deleting profile with ID {id}: {e}", exc_info=True)
        session.rollback()
        return False

    finally:
        session.close()
