import pytest

from src.database import (ProfileDTO, create_profile, delete_profile,
                          get_profile, update_profile)

PROFILE_NAME_1 = "test_profile_beta"
UPDATED_PROFILE_NAME_1 = "updated_test_profile_beta"
BALANCE_1 = 1000
STRATEGY_SETTINGS_1 = {"sell_limit": 0.5, "buy_limit": 0.5, "stop_loss": 0.5, "limit": 0.5}
WALLET_1 = {"BTC": 100}

PROFILE_NAME_2 = "test_profile_delta"
BALANCE_2 = 9000
STRATEGY_SETTINGS_2 = {"sell_limit": 0.3, "buy_limit": 0.5, "stop_loss": 0.5, "limit": 0.5}
WALLET_2 = {"BTC": 100}

@pytest.fixture
def cleanup():
    if get_profile(name=PROFILE_NAME_1) is not None:
        raise Exception(f"Profile already exists, with the test name ``{PROFILE_NAME_1}``")

    if get_profile(name=UPDATED_PROFILE_NAME_1) is not None:
        raise Exception(f"Profile already exists, with the test name ``{UPDATED_PROFILE_NAME_1}``")

    if get_profile(name=PROFILE_NAME_2) is not None:
        raise Exception(f"Profile already exists, with the test name ``{PROFILE_NAME_2}``")

    yield

    delete_profile(name=PROFILE_NAME_1)
    delete_profile(name=UPDATED_PROFILE_NAME_1)
    delete_profile(name=PROFILE_NAME_2)



def test_crud_operations_profile(cleanup):
    new_profile_dto_1: ProfileDTO = create_profile(
        name=PROFILE_NAME_1,
        balance=BALANCE_1,
        wallet=WALLET_1,
        strategy_settings=STRATEGY_SETTINGS_1
    )

    assert isinstance(new_profile_dto_1, ProfileDTO)
    assert new_profile_dto_1.name == PROFILE_NAME_1
    assert new_profile_dto_1.wallet == WALLET_1
    assert new_profile_dto_1.strategy_settings == STRATEGY_SETTINGS_1

    assert get_profile(name=PROFILE_NAME_1) == new_profile_dto_1


    assert update_profile(id=new_profile_dto_1.id, name=UPDATED_PROFILE_NAME_1)
    assert get_profile(name=UPDATED_PROFILE_NAME_1).name == UPDATED_PROFILE_NAME_1
    assert get_profile(id=new_profile_dto_1.id).name == UPDATED_PROFILE_NAME_1

    new_profile_dto_2: ProfileDTO = create_profile(
        name=PROFILE_NAME_2,
        balance=BALANCE_2,
        wallet=WALLET_2,
        strategy_settings=STRATEGY_SETTINGS_2
    )

    profiles: list[ProfileDTO] = get_profile()
    assert len(profiles) >= 2
    for profile in profiles:
        assert isinstance(profile, ProfileDTO)

    assert delete_profile(name=UPDATED_PROFILE_NAME_1)
    assert get_profile(name=UPDATED_PROFILE_NAME_1) is None
    assert delete_profile(id=new_profile_dto_2.id)
    assert get_profile(id=new_profile_dto_2.id) is None