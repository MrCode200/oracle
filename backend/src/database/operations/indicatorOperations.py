from logging import getLogger

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from backend.src.database import Indicator, engine

logger = getLogger("oracle.app")
Session = sessionmaker(bind=engine)


def create_indicator(
    profile_id: int, indicator_name: str, indicator_settings: dict
) -> Indicator | None:
    """
    Creates a new indicator for the profile in the database.

    :param profile_id: The ID of the profile.
    :param indicator_name: The name of the indicator.
    :param indicator_settings: The settings of the indicator.

    :return: The newly created Indicator object.
    """
    session = Session()

    try:
        new_indicator = Indicator(
            profile_id=profile_id,
            indicator_name=indicator_name,
            indicator_settings=indicator_settings,
        )

        session.add(new_indicator)
        session.commit()
        session.refresh(new_indicator)

        return new_indicator

    except IntegrityError as e:
        logger.error(f"Error adding Indicator {indicator_name}: {e}", exc_info=True)
        session.rollback()

    finally:
        session.close()


def get_indicator(profile_id: int = None, indicator_id: int = None, ticker: str = None):
    """
    Retrieves an indicator from the database by ID, profile ID, or name.

    :param profile_id: The ID of the profile.
    :param indicator_id: The ID of the indicator.
    :param ticker: Returns all Indicators of a profile by ticker

    :return: The Indicator object or None if not found.
    """
    session = Session()

    try:
        if ticker is not None and profile_id is not None:
            return session.get(Indicator, profile_id).filter_by(ticker=ticker).all()
        elif profile_id is not None:
            return session.get(Indicator, profile_id)
        elif indicator_id is not None:
            return session.get(Indicator, indicator_id)

        else:
            return session.query(Indicator).all()

    except Exception as e:
        logger.error(f"Error getting indicator: {e}", exc_info=True)

    finally:
        session.close()


def update_indicator(
    indicator_id: int,
    indicator_weight: float = None,
    ticker: str = None,
    interval: str = None,
    indicator_settings: dict = None,
) -> bool:
    """
    Updates an existing indicator in the database.

    :param indicator_id: The ID of the indicator to update.
    :param indicator_weight: The weight assigned to the indicator when calculating.
    :param ticker: The ticker of the indicator.
    :param interval: The interval of the indicator when fetching data.
    :param indicator_settings: The settings of the indicator.
    :return:
    """
    session = Session()

    try:
        indicator = session.get(Indicator, indicator_id)

        if indicator:
            if indicator_weight is not None:
                indicator.indicator_weight = indicator_weight
            if ticker is not None:
                indicator.ticker = ticker
            if interval is not None:
                indicator.interval = interval
            if indicator_settings is not None:
                indicator.indicator_settings = indicator_settings

            session.add(indicator)
            session.commit()
            logger.info(f"Indicator {indicator_id} updated successfully.")
            return True
        else:
            logger.warning(f"Indicator with ID {indicator_id} not found.")
            return False

    except Exception as e:
        logger.error(
            f"Error updating indicator with ID {indicator_id}: {e}", exc_info=True
        )
        session.rollback()
        return False

    finally:
        session.close()


def delete_indicator(indicator_id: int) -> bool:
    """
    Deletes an indicator from the database.

    :param indicator_id: The ID of the indicator to delete.
    :return: False if the indicator is not deleted successfully or not found, True if the indicator is deleted successfully.
    """
    session = Session()

    try:
        indicator = session.get(Indicator, indicator_id)

        if indicator:
            session.delete(indicator)
            session.commit()
            logger.info(f"Indicator {indicator_id} deleted successfully.")
            return True
        else:
            logger.warning(f"Indicator with ID {indicator_id} not found.")
            return False

    except Exception as e:
        logger.error(
            f"Error deleting indicator with ID {indicator_id}: {e}", exc_info=True
        )
        session.rollback()
        return False

    finally:
        session.close()
