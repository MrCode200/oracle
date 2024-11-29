import pytest

from backend.src.database import create_order, select_orders, add_profile, delete_profile, select_profile

PROFILE_NAME = "test_profile_delta"
BALANCE = 1000
PROFILE_SETTINGS = {"sell_limit": 0.5, "buy_limit": 0.5, "stop_loss": 0.5, "limit": 0.5}
WALLET = {"BTC": 100}
ALGORITHM_SETTINGS = {"SimpleMovingAverage": {"crossover_weight_impact": 0.5}}
FETCH_SETTINGS = {"period": "1d", "interval": "1d"}

ORDER_TYPE = "BUY"
TICKER = "BTC-USD"
PRICE = 1000
QUANTITY = 1


@pytest.fixture
def cleanup():
    if select_profile(profile_name=PROFILE_NAME) is not None:
        raise Exception("Profile already exists, with the test name ``test_profile_delta``")

    yield

    delete_profile(profile_name=PROFILE_NAME)


def test_crud_operations_order(cleanup):
    add_profile(
        profile_name=PROFILE_NAME,
        balance=BALANCE,
        profile_settings=PROFILE_SETTINGS,
        wallet=WALLET,
        algorithm_settings=ALGORITHM_SETTINGS,
        fetch_settings=FETCH_SETTINGS,
    )

    profile_id = select_profile(profile_name=PROFILE_NAME).profile_id

    create_order(profile_id=profile_id, order_type=ORDER_TYPE, ticker=TICKER, price=PRICE, quantity=QUANTITY)

    orders = select_orders(profile_id=profile_id)

    assert len(orders) == 1
    assert orders[0].profile_id == profile_id
    assert orders[0].type == ORDER_TYPE
    assert orders[0].ticker == TICKER
    assert orders[0].quantity == QUANTITY
    assert orders[0].price == PRICE

    create_order(profile_id=profile_id, order_type=ORDER_TYPE, ticker=TICKER, price=PRICE, quantity=QUANTITY)

    orders = select_orders(profile_id=profile_id)

    assert len(orders) == 2

    delete_profile(profile_name=PROFILE_NAME)

    orders = select_orders(profile_id=profile_id)

    assert len(orders) == 0
