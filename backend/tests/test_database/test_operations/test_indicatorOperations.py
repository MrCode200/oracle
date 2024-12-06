import pytest

from backend.src.database import get_indicator, create_indicator, delete_indicator, IndicatorDTO, ProfileDTO
from backend.src.database import create_profile, delete_profile, get_profile

PROFILE_NAME = "test_profile_beta"
UPDATED_PROFILE_NAME = "updated_test_profile_beta"
BALANCE = 1000
STRATEGY_SETTINGS = {"sell_limit": 0.5, "buy_limit": 0.5, "stop_loss": 0.5, "limit": 0.5}
WALLET = {"BTC": 100}

INDICATOR_NAME = "test_indicator"
WEIGHT = 0.5
TICKER = "BTC"
INTERVAL = "1d"
SETTINGS = {}

@pytest.fixture
def cleanup():
    if get_profile(name=PROFILE_NAME) is not None:
        raise Exception(f"Profile already exists, with the test name ``{PROFILE_NAME}``")

    yield

    delete_profile(name=PROFILE_NAME)


def test_crud_operations_indicator(cleanup):
    new_profile_dto: ProfileDTO = create_profile(
        name=PROFILE_NAME,
        balance=BALANCE,
        wallet=WALLET,
        strategy_settings=STRATEGY_SETTINGS
    )

    new_indicator_dto_1: IndicatorDTO = create_indicator(
        profile_id=new_profile_dto.id,
        name=INDICATOR_NAME,
        weight=WEIGHT,
        ticker=TICKER,
        interval=INTERVAL,
        settings=SETTINGS
    )

    assert get_indicator(id=new_indicator_dto_1.id) == new_indicator_dto_1

    new_indicator_dto_2: IndicatorDTO = create_indicator(
        profile_id=new_profile_dto.id,
        name=INDICATOR_NAME,
        weight=WEIGHT,
        ticker=TICKER,
        interval=INTERVAL,
        settings=SETTINGS
    )

    assert get_indicator(id=new_indicator_dto_2.id) == new_indicator_dto_2

    assert len(get_indicator(profile_id=new_profile_dto.id)) == 2

    assert delete_indicator(id=new_indicator_dto_2.id)

    assert get_indicator(id=new_indicator_dto_2.id) is None

    assert delete_profile(name=PROFILE_NAME)

    assert get_indicator(id=new_indicator_dto_1.id) is None