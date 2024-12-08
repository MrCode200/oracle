import pytest

from src.database import create_order, get_order, OrderDTO, get_profile, delete_profile, ProfileDTO, \
    create_profile

PROFILE_NAME = "test_profile_beta"
UPDATED_PROFILE_NAME = "updated_test_profile_beta"
BALANCE = 1000
STRATEGY_SETTINGS = {"sell_limit": 0.5, "buy_limit": 0.5, "stop_loss": 0.5, "limit": 0.5}
WALLET = {"BTC": 100}


ORDER_TYPE = "BUY"
TICKER = "BTC-USD"
PRICE = 1000
QUANTITY = 1


@pytest.fixture
def cleanup():
    if get_profile(name=PROFILE_NAME) is not None:
        raise Exception(f"Profile already exists, with the test name ``{PROFILE_NAME}``")

    yield

    delete_profile(name=PROFILE_NAME)


def test_crud_operations_order(cleanup):
    new_profile_dto: ProfileDTO = create_profile(
        name=PROFILE_NAME,
        balance=BALANCE,
        wallet=WALLET,
        strategy_settings=STRATEGY_SETTINGS
    )

    new_order_dto_1: OrderDTO = create_order(
        profile_id=new_profile_dto.id,
        order_type=ORDER_TYPE,
        ticker=TICKER,
        price=PRICE,
        quantity=QUANTITY
    )

    new_order_dto_2: OrderDTO = create_order(
        profile_id=new_profile_dto.id,
        order_type=ORDER_TYPE,
        ticker=TICKER,
        price=PRICE,
        quantity=QUANTITY
    )

    get_order_dto: OrderDTO = get_order(id=new_order_dto_1.id)
    assert get_order_dto == new_order_dto_1
    assert get_order_dto.id == new_order_dto_1.id
    assert get_order_dto.profile_id == new_order_dto_1.profile_id
    assert get_order_dto.type == new_order_dto_1.type
    assert get_order_dto.ticker == new_order_dto_1.ticker
    assert get_order_dto.quantity == new_order_dto_1.quantity
    assert get_order_dto.price == new_order_dto_1.price

    assert len(get_order(profile_id=new_profile_dto.id)) == 2
    for order in get_order(profile_id=new_profile_dto.id):
        assert order.profile_id == new_profile_dto.id

    delete_profile(name=PROFILE_NAME)

    assert get_order(id=new_order_dto_1.id) is None

