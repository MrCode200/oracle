import pytest

from backend.src.algorithms.utils.registry import get_model, register_model


def test_register_model():
    @register_model
    class TestModel:
        pass

    assert get_model("TestModel") == TestModel


def test_registry_model_dublicate_registries():
    @register_model
    class TestModel:
        pass


    with pytest.raises(ValueError):
        @register_model
        class TestModel:
            pass