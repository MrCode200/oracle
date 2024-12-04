from backend.src.database import engine, Order
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from logging import getLogger
from typing import Type

logger = getLogger("oracle.app")

Session = sessionmaker(bind=engine)


def create_order(
    profile_id: int, type: str, ticker: str, quantity: int, price: float
) -> Order:
    """
    Creates a new order for the profile in the database.

    :param profile_id: The ID of the profile.
    :param type: The type of the order (e.g., "buy", "sell").
    :param ticker: The ticker of the asset being traded.
    :param quantity: The quantity of the asset being traded.
    :param price: The price at which the asset is being traded.

    :return: The newly created Order object.
    """
    session = Session()

    try:
        new_order = Order(
            profile_id=profile_id,
            type=type,
            ticker=ticker,
            quantity=quantity,
            price=price,
        )
        session.add(new_order)
        session.commit()

        logger.info(
            f"Order for {ticker} created successfully for profile {profile_id}."
        )
        return new_order

    except IntegrityError as e:
        logger.error(f"Error creating order for {ticker}: {e}", exc_info=True)
        session.rollback()

    finally:
        session.close()


def get_order(
    order_id: int | None = None,
    profile_id: int | None = None,
    ticker: str | None = None,
) -> Order | list[Type[Order]] | None:
    """
    Retrieves an order from the database by ID, profile ID, or ticker.

    :param order_id: The ID of the order.
    :param profile_id: The ID of the profile.
    :param ticker: The ticker of the asset.

    :return: The Order object or None if not found.
    """
    session = Session()

    try:
        if order_id is not None:
            return session.get(Order, order_id)
        elif profile_id is not None:
            return session.query(Order).filter_by(profile_id=profile_id).all()
        elif ticker is not None:
            return session.query(Order).filter_by(ticker=ticker).all()
        else:
            return session.query(Order).all()

    finally:
        session.close()
