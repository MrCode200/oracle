import pytest
from src.exceptions import RegistryError
from src.utils.registry.indicatorRegistry import (get_indicator,
                                                  register_indicator)


def test_register_indicator():
    @register_indicator
    class TestIndicator:
        pass

    assert get_indicator("TestIndicator") == TestIndicator


def test_registry_indicator_dublicate_registries():
    @register_indicator
    class TestIndicator:
        pass


    with pytest.raises(RegistryError):
        @register_indicator
        class TestIndicator:
            pass