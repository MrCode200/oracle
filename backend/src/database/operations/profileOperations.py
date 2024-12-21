from logging import getLogger
from typing import Type

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from src.database import ProfileDTO, ProfileModel, engine

logger = getLogger("oracle.app")

Session = sessionmaker(bind=engine)


def convert_to_dto(profile: Type[ProfileModel] | ProfileModel | None) -> ProfileDTO | None:
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
        paper_balance=profile.paper_balance,
        paper_wallet=profile.paper_wallet,

        buy_limit=profile.buy_limit,
        sell_limit=profile.sell_limit
    )


def create_profile(
        name: str, balance: float, wallet: dict, paper_balance: float, buy_limit: float, sell_limit: float
) -> ProfileDTO | None:
    """
    Creates a new profile in the database.

    :param name: The name of the profile.
    :param balance: The balance of the profile.
    :param wallet: The wallet information for the profile.
    :param paper_balance: The paper balance of the profile.
    :param buy_limit: The new buy limit of the profile (optional).
    :param sell_limit: The new sell limit of the profile (optional).

    :return: The newly created profile object.
    """
    session = Session()

    try:
        # Create and add the new profile
        new_profile = ProfileModel(
            name=name,
            balance=balance,
            wallet=wallet,
            paper_balance=paper_balance,
            paper_wallet=wallet,
            buy_limit=buy_limit,
            sell_limit=sell_limit
        )

        session.add(new_profile)
        session.commit()

        logger.info(
            f"Profile {new_profile.id=}; {name=}; {balance=}; {wallet=}; {paper_balance=}; {buy_limit=}; {sell_limit=}; created successfully.")
        return convert_to_dto(new_profile)

    except IntegrityError as e:
        logger.error(
            f"Error creating profile {name=}; {balance=}; {wallet=}; {paper_balance=}; {buy_limit=}; {sell_limit=}: {e}",
            exc_info=True)
        session.rollback()
        return None

    finally:
        session.close()


def get_profile(id: int = None, name: str = None) -> ProfileDTO | list[ProfileDTO] | None:
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
            logger.info(f"Profile with ID {id} retrieved.")
            return convert_to_dto(session.get(ProfileModel, id))

        elif name is not None:
            profile: Type[ProfileModel] | None = session.query(ProfileModel).filter_by(name=name).first()
            logger.info(f"Profile where {name=} retrieved.")
            return convert_to_dto(profile)
        else:
            profiles: list[Type[ProfileModel]] = session.query(ProfileModel).all()
            logger.info(f"All Profiles retrieved.")
            return [convert_to_dto(profile) for profile in profiles]

    except Exception as e:
        logger.error(f"Error retrieving Profile: {e}", exc_info=True)
        return None

    finally:
        session.close()


from typing import Optional


def update_profile(
        id: int,
        name: Optional[str] = None,
        status: Optional[str] = None,
        balance: Optional[float] = None,
        wallet: Optional[dict] = None,
        paper_balance: Optional[float] = None,
        paper_wallet: Optional[dict] = None,
        buy_limit: Optional[float] = None,
        sell_limit: Optional[float] = None,
) -> bool:
    """
    Updates a profile in the database.

    :param id: The ID of the profile to update.
    :param name: The new profile name (optional).
    :param status: The new status of the profile (optional).
    :param balance: The new balance of the profile (optional).
    :param wallet: The new wallet information for the profile (optional).
    :param paper_balance: The new paper balance of the profile (optional).
    :param paper_wallet: The new paper wallet information for the profile (optional).
    :param buy_limit: The new buy limit of the profile (optional).
    :param sell_limit: The new sell limit of the profile (optional).

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
        if name is not None:
            profile.name = name
        if status is not None:
            profile.status = status

        if balance is not None:
            profile.balance = balance
        if wallet is not None:
            profile.wallet = wallet

        if paper_balance is not None:
            profile.paper_balance = paper_balance
        if paper_wallet is not None:
            profile.paper_wallet = paper_wallet

        if buy_limit is not None:
            profile.buy_limit = buy_limit
        if sell_limit is not None:
            profile.sell_limit = sell_limit

        session.commit()
        logger.info(
            f"Profile with ID {id} updated {name=}; {status=}; {balance=}; {wallet=}; {paper_balance=}; {paper_wallet=}; {buy_limit=}; {sell_limit=}; successfully.")
        return True

    except Exception as e:
        logger.error(f"Error updating {name=}; {status=}; {balance=}; {wallet=}; {paper_balance=}; {paper_wallet=}; {buy_limit=}; {sell_limit=}; for profile with ID {id}: {e}", exc_info=True)
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
