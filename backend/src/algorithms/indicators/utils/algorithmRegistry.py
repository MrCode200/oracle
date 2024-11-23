from logging import getLogger
from typing import Type

from backend.src.exceptions import RegistryError

logger = getLogger("oracle.app")

_INDICATOR_REGISTRY: dict[str, Type] = {}


def register_indicator(cls: Type) -> Type:
    """Register an indicator to the registry"""

    name: str = cls.__name__
    if name not in _INDICATOR_REGISTRY:
        _INDICATOR_REGISTRY.update({name: cls})
    else:
        logger.error(f"Indicator {name} already registered.", exc_info=True)
        return cls
    logger.debug(f"Registered `{name}` to registry")
    return cls


def get_indicator(name: str = None) -> Type | dict[str, Type] | None:
    """
    Retrieves the indicator by its name. If name is None then it returns the entire registry

    :param name: The name of indicator
    :return: The indicator
    """
    if name is None:
        return _INDICATOR_REGISTRY
    if name not in _INDICATOR_REGISTRY:
        logger.error(f"Indicator {name} not registered.\nREGISTER: {_INDICATOR_REGISTRY}", exc_info=True)
        return
    logger.debug(f"Looking up INDICATOR_REGISTRY for name: {name}")
    return _INDICATOR_REGISTRY[name]
