from logging import getLogger

from sqlalchemy.engine import ResultProxy
from sqlalchemy.orm import sessionmaker

from .. import engine, Order

logger = getLogger("oracle.app")

Session = sessionmaker(bind=engine)

def insert_order(profile_id: int, order_type: str, ticker: str, quantity: int, price: float) -> None:
    session = Session()

    try:
        new_order = Order(
            profile_id=profile_id,
            type=order_type,
            ticker=ticker,
            quantity=quantity,
            price=price
        )

        session.add(new_order)
        session.commit()
    except Exception as e:
        logger.error(f"Error inserting order", exc_info=True)
        session.rollback()

    finally:
        session.close()


def select_orders(profile_id: int) -> ResultProxy:
    session = Session()

    try:
        orders = session.query(Order).filter(Order.profile_id == profile_id).all()
        return orders
    finally:
        session.close()
