import pytest

from backend.src.database import add_profile, delete_profile, select_profile

PROFILE_NAME = "test_profile_beta"
BALANCE = 1000
PROFILE_SETTINGS = {"sell_limit": 0.5, "buy_limit": 0.5, "stop_loss": 0.5, "limit": 0.5}
WALLET = {"BTC": 100}
ALGORITHM_SETTINGS = {"SimpleMovingAverage": {"crossover_weight_impact": 0.5}}
FETCH_SETTINGS = {"period": "1d", "interval": "1d"}


@pytest.fixture
def cleanup():
    if select_profile(profile_name=PROFILE_NAME) is not None:
        raise Exception("Profile already exists, with the test name ``test_profile_delta``")

    yield

    delete_profile(profile_name=PROFILE_NAME)


def test_crud_operations_profile(cleanup):
    add_profile(
        profile_name=PROFILE_NAME,
        balance=BALANCE,
        profile_settings=PROFILE_SETTINGS,
        wallet=WALLET,
        algorithm_settings=ALGORITHM_SETTINGS,
        fetch_settings=FETCH_SETTINGS,
    )

    profile = select_profile(profile_name=PROFILE_NAME)
    assert profile is not None
    assert profile.profile_name == PROFILE_NAME
    assert profile.balance == BALANCE
    assert profile.profile_settings == PROFILE_SETTINGS
    assert profile.wallet == WALLET
    assert profile.algorithm_settings == ALGORITHM_SETTINGS
    assert profile.fetch_settings == FETCH_SETTINGS

    delete_profile(profile_name=PROFILE_NAME)
    profile = select_profile(profile_name=PROFILE_NAME)
    assert profile is None
