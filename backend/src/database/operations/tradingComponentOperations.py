from logging import getLogger

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from src.database import TradingComponentDTO, TradingComponentModel, engine

logger = getLogger("oracle.app")
Session = sessionmaker(bind=engine)

def convert_to_dto(trading_component: TradingComponentModel) -> TradingComponentDTO | None:
    """
    Helper function to convert an IndicatorModel to an IndicatorDTO.
    """
    if not trading_component:
        return None
    return TradingComponentDTO(
        id=trading_component.id,
        profile_id=trading_component.profile_id,
        name=trading_component.name,
        weight=trading_component.weight,
        ticker=trading_component.ticker,
        interval=trading_component.interval,
        settings=trading_component.settings,
    )

def create_trading_component(
        profile_id: int,
        name: str,
        weight: float,
        ticker: str,
        interval: str,
        settings: dict,
) -> TradingComponentDTO | None:
    """
    Creates a new trading_component for the profile in the database.

    :param profile_id: The ID of the profile.
    :param name: The name of the Trading Component.
    :param weight: The weight of the Trading Component.
    :param ticker: The ticker of the Trading Component.
    :param interval: The interval of the Trading Component.
    :param settings: The settings of the Trading Component.

    :return: The newly created trading_component object.
    """
    session = Session()

    try:
        new_trading_component = TradingComponentModel(
            profile_id=profile_id,
            name=name,
            weight=weight,
            ticker=ticker,
            interval=interval,
            settings=settings,
        )

        session.add(new_trading_component)
        session.commit()
        session.refresh(new_trading_component)

        logger.info(
            f"Trading Component with {profile_id=}; {name=}; {weight=}; {ticker=}; {interval=}; {settings=} created successfully."
        )

        return TradingComponentDTO(
            id=new_trading_component.id,
            profile_id=new_trading_component.profile_id,
            name=new_trading_component.name,
            weight=new_trading_component.weight,
            ticker=new_trading_component.ticker,
            interval=new_trading_component.interval,
            settings=new_trading_component.settings,
        )

    except IntegrityError as e:
        logger.error(f"Error creating Trading Component {name}: {e}", exc_info=True)
        session.rollback()

    finally:
        session.close()


def get_trading_component(
        profile_id: int = None, trade_component_id: int = None, ticker: str = None
) -> list[TradingComponentDTO] | TradingComponentDTO | None:
    """
    Retrieves Trading Component based on profile_id, id, or ticker.
    Returns a single TradeComponentDTO or a list of TradeComponentDTO.

    :param profile_id: ID of the profile.
    :param trade_component_id: ID of the Trading Component.
    :param ticker: The ticker of the Trading Component.
    :return: TradeComponentDTO or a list of TradeComponentDTO, or None if no result found.
    """
    session = Session()

    try:
        if ticker and profile_id:
            logger.info(f"Trading Component with {profile_id=}; {ticker=} retrieved.")
            return [
                convert_to_dto(trading_component) for trading_component in session.query(TradingComponentModel).filter_by(
                profile_id=profile_id, ticker=ticker
                ).all()
            ]

        if trade_component_id:
            trading_component: TradingComponentModel = session.get(TradingComponentModel, trade_component_id)
            if trading_component:
                logger.info(f"Trading Component with ID {trade_component_id} retrieved.")
                return convert_to_dto(trading_component)
            else:
                logger.error(f"Trading Component with ID {trade_component_id} not found.")
                return None

        if profile_id:
            logger.info(f"Trading Components with {profile_id=} retrieved.")
            return [
                convert_to_dto(trading_component) for trading_component in session.query(TradingComponentModel).filter_by(
                profile_id=profile_id
                ).all()
            ]

        logger.info("All Trading Components retrieved.")
        return [convert_to_dto(trading_component) for trading_component in session.query(TradingComponentModel).all()]

    except Exception as e:
        logger.error(f"Error retrieving Trading Component: {e}", exc_info=True)
        return None

    finally:
        session.close()


def update_trading_component(
        trading_component_id: int,
        weight: float = None,
        ticker: str = None,
        interval: str = None,
        settings: dict = None,
) -> bool:
    """
    Updates an existing Trading Component in the database.

    :param trading_component_id: The ID of the Trading Component to update.
    :param weight: The weight assigned to the Trading Component when calculating.
    :param ticker: The ticker of the Trading Component.
    :param interval: The interval of the Trading Component when fetching data.
    :param settings: The settings of the Trading Component.
    :return:
    """
    session = Session()

    try:
        trading_component = session.get(TradingComponentModel, trading_component_id)

        if trading_component:
            if weight is not None:
                trading_component.weight = weight
            if ticker is not None:
                trading_component.ticker = ticker
            if interval is not None:
                trading_component.interval = interval
            if settings is not None:
                trading_component.settings = settings

            session.add(trading_component)
            session.commit()
            logger.info(f"Trading Component with ID {trading_component_id} updated {weight=}; {ticker=}; {interval=}; {settings=}; successfully.")
            return True
        else:
            logger.warning(f"Trading Component with ID {trading_component_id} not found.")
            return False

    except Exception as e:
        logger.error(f"Error updating {weight}; {ticker}; {interval}; {settings}; for Trading Component with ID {trading_component_id}: {e}", exc_info=True)
        session.rollback()
        return False

    finally:
        session.close()


def delete_trading_component(trading_component_id: int) -> bool:
    """
    Deletes a Trading Component from the database.

    :param trading_component_id: The ID of the Trading Component to delete.
    :return: False if the Trading Component is not deleted successfully or not found, True if the Trading Component is deleted successfully.
    """
    session = Session()

    try:
        trading_component = session.get(TradingComponentModel, trading_component_id)

        if trading_component:
            session.delete(trading_component)
            session.commit()
            logger.info(f"Trading Component with ID {trading_component_id} deleted successfully.")
            return True
        else:
            logger.warning(f"Trading Component with ID {trading_component_id} not found.")
            return False

    except Exception as e:
        logger.error(f"Error deleting Trading Component with ID {trading_component_id}: {e}", exc_info=True)
        session.rollback()
        return False

    finally:
        session.close()
