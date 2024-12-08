from logging import getLogger
from typing import Type

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from src.database import OrderModel, OrderDTO, engine

logger = getLogger("oracle.app")

Session = sessionmaker(bind=engine)


def convert_to_dto(order: OrderModel) -> OrderDTO | None:
    """
    Helper function to convert an IndicatorModel to an IndicatorDTO.
    """
    if not order:
        return None
    return OrderDTO(
        id=order.id,
        profile_id=order.profile_id,
        type=order.type,
        ticker=order.ticker,
        quantity=order.quantity,
        price=order.price,
        timestamp=order.timestamp,
    )


def create_order(
        profile_id: int, order_type: str, ticker: str, quantity: int, price: float
) -> OrderDTO:
    """
    Creates a new order for the profile in the database.

    :param profile_id: The ID of the profile.
    :param order_type: The type of the order (e.g., "buy", "sell").
    :param ticker: The ticker of the asset being traded.
    :param quantity: The quantity of the asset being traded.
    :param price: The price at which the asset is being traded.

    :return: The newly created Order object.
    """
    session = Session()

    try:
        new_order = OrderModel(
            profile_id=profile_id,
            type=order_type,
            ticker=ticker,
            quantity=quantity,
            price=price,
        )
        session.add(new_order)
        session.commit()

        logger.info(
            f"Order {order_type=}; {ticker=}; {quantity=}; {price=}; created successfully for {profile_id=}."
        )
        return convert_to_dto(new_order)

    except IntegrityError as e:
        logger.error(f"Error creating order {order_type=}; {ticker=}; {quantity=}; {price=}; for {profile_id=}: {e}", exc_info=True)
        session.rollback()

    finally:
        session.close()


def get_order(
        id: int | None = None,
        profile_id: int | None = None,
        ticker: str | None = None,
        order_type: str | None = None,
) -> OrderDTO | list[OrderDTO] | None:
    """
    Retrieves an order from the database by ID, profile ID, or ticker.

    :param id: The ID of the order.
    :param profile_id: The ID of the profile.
    :param ticker: The ticker of the asset.
    :param order_type: The type of the order.

    :return: The Order object or None if not found.
    """
    session = Session()

    try:
        if id is not None:
            logger.info(f"Order with ID {id} retrieved.")
            return convert_to_dto(session.get(OrderModel, id))
        elif profile_id is not None:
            order_dtos: list[OrderDTO] = [convert_to_dto(order) for order in session.query(OrderModel).filter_by(profile_id=profile_id).all()]
        elif ticker is not None:
            order_dtos: list[OrderDTO] = [convert_to_dto(order) for order in session.query(OrderModel).filter_by(ticker=ticker).all()]
        elif order_type is not None:
            order_dtos: list[OrderDTO] = [convert_to_dto(order) for order in session.query(OrderModel).filter_by(type=order_type).all()]
        else:
            order_dtos: list[OrderDTO] = [convert_to_dto(order) for order in session.query(OrderModel).all()]

        logger.info(f"{len(order_dtos)} orders where {profile_id=}; {ticker=}; {order_type=}; retrieved.")

    except Exception as e:
        logger.error(f"Error retrieving order(s) where {profile_id=}; {ticker=}; {order_type=}: {e}", exc_info=True)
        return None

    finally:
        session.close()
