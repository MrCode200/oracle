from logging import getLogger

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from src.database import IndicatorDTO, IndicatorModel, engine

logger = getLogger("oracle.app")
Session = sessionmaker(bind=engine)

def convert_to_dto(indicator: IndicatorModel) -> IndicatorDTO | None:
    """
    Helper function to convert an IndicatorModel to an IndicatorDTO.
    """
    if not indicator:
        return None
    return IndicatorDTO(
        id=indicator.id,
        profile_id=indicator.profile_id,
        name=indicator.name,
        weight=indicator.weight,
        ticker=indicator.ticker,
        interval=indicator.interval,
        settings=indicator.settings,
    )


def create_indicator(
        profile_id: int,
        name: str,
        weight: float,
        ticker: str,
        interval: str,
        settings: dict,
) -> IndicatorDTO | None:
    """
    Creates a new indicator for the profile in the database.

    :param profile_id: The ID of the profile.
    :param name: The name of the indicator.
    :param weight: The weight of the indicator.
    :param ticker: The ticker of the indicator.
    :param interval: The interval of the indicator.
    :param settings: The settings of the indicator.

    :return: The newly created Indicator object.
    """
    session = Session()

    try:
        new_indicator = IndicatorModel(
            profile_id=profile_id,
            name=name,
            weight=weight,
            ticker=ticker,
            interval=interval,
            settings=settings,
        )

        session.add(new_indicator)
        session.commit()
        session.refresh(new_indicator)

        logger.info(
            f"Indicator with {profile_id=}; {name=}; {weight=}; {ticker=}; {interval=}; {settings=} created successfully."
        )

        return IndicatorDTO(
            id=new_indicator.id,
            profile_id=new_indicator.profile_id,
            name=new_indicator.name,
            weight=new_indicator.weight,
            ticker=new_indicator.ticker,
            interval=new_indicator.interval,
            settings=new_indicator.settings,
        )

    except IntegrityError as e:
        logger.error(f"Error creating Indicator {name}: {e}", exc_info=True)
        session.rollback()

    finally:
        session.close()


def get_indicator(
        profile_id: int = None, indicator_id: int = None, ticker: str = None
) -> list[IndicatorDTO] | IndicatorDTO | None:
    """
    Retrieves indicators based on profile_id, id, or ticker.
    Returns a single IndicatorDTO or a list of IndicatorDTOs.

    :param profile_id: ID of the profile.
    :param indicator_id: ID of the indicator.
    :param ticker: The ticker of the indicator.
    :return: IndicatorDTO or a list of IndicatorDTOs, or None if no result found.
    """
    session = Session()

    try:
        if ticker and profile_id:
            logger.info(f"Indicators with {profile_id=}; {ticker=} retrieved.")
            return [
                convert_to_dto(indicator) for indicator in session.query(IndicatorModel).filter_by(
                profile_id=profile_id, ticker=ticker
                ).all()
            ]

        if indicator_id:
            indicator: IndicatorModel = session.get(IndicatorModel, indicator_id)
            if indicator:
                logger.info(f"Indicator with ID {indicator_id} retrieved.")
                return convert_to_dto(indicator)
            else:
                logger.error(f"Indicator with ID {indicator_id} not found.")
                return None

        if profile_id:
            logger.info(f"Indicators with {profile_id=} retrieved.")
            return [
                convert_to_dto(indicator) for indicator in session.query(IndicatorModel).filter_by(
                profile_id=profile_id
                ).all()
            ]

        logger.info("All indicators retrieved.")
        return [convert_to_dto(indicator) for indicator in session.query(IndicatorModel).all()]

    except Exception as e:
        logger.error(f"Error retrieving indicator: {e}", exc_info=True)
        return None

    finally:
        session.close()


def update_indicator(
        indicator_id: int,
        weight: float = None,
        ticker: str = None,
        interval: str = None,
        settings: dict = None,
) -> bool:
    """
    Updates an existing indicator in the database.

    :param indicator_id: The ID of the indicator to update.
    :param weight: The weight assigned to the indicator when calculating.
    :param ticker: The ticker of the indicator.
    :param interval: The interval of the indicator when fetching data.
    :param settings: The settings of the indicator.
    :return:
    """
    session = Session()

    try:
        indicator = session.get(IndicatorModel, indicator_id)

        if indicator:
            if weight is not None:
                indicator.weight = weight
            if ticker is not None:
                indicator.ticker = ticker
            if interval is not None:
                indicator.interval = interval
            if settings is not None:
                indicator.settings = settings

            session.add(indicator)
            session.commit()
            logger.info(f"Indicator with ID {indicator_id} updated {weight=}; {ticker=}; {interval=}; {settings=}; successfully.")
            return True
        else:
            logger.warning(f"Indicator with ID {indicator_id} not found.")
            return False

    except Exception as e:
        logger.error(f"Error updating {weight}; {ticker}; {interval}; {settings}; for indicator with ID {indicator_id}: {e}", exc_info=True)
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
        indicator = session.get(IndicatorModel, indicator_id)

        if indicator:
            session.delete(indicator)
            session.commit()
            logger.info(f"Indicator with ID {indicator_id} deleted successfully.")
            return True
        else:
            logger.warning(f"Indicator with ID {indicator_id} not found.")
            return False

    except Exception as e:
        logger.error(f"Error deleting indicator with ID {indicator_id}: {e}", exc_info=True)
        session.rollback()
        return False

    finally:
        session.close()
