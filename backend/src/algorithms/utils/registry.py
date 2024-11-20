from logging import getLogger
from typing import Type

logger = getLogger("oracle.app")

_MODEL_REGISTRY: dict[str, Type] = {}


def register_model(cls: Type) -> Type:
    """Register an item (indicator, pattern, or strategy) with a category."""

    name: str = cls.__name__
    if name not in _MODEL_REGISTRY:
        _MODEL_REGISTRY.update({name: cls})
    else:
        logger.error(f"Model {name} already registered.", exc_info=True)

    logger.debug(f"Registered `{name}` to registry")
    return cls


def get_model(name: str) -> Type:
    """
    Retrieves the model by its name.

    :param name: The name of the model
    :return: The model
    """
    if name not in _MODEL_REGISTRY:
        logger.error(f"Model {name} not registered.\nREGISTER: {_MODEL_REGISTRY}", exc_info=True)
    logger.debug(f"Looking up MODEL_REGISTRY for name: {name}")
    return _MODEL_REGISTRY[name]
