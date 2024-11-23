from typing import Type
from logging import getLogger

from backend.src.exceptions import RegistryError

logger = getLogger("oracle.app")

_PLUGIN_REGISTRY: dict[str, Type] = {}


def register_plugin(cls: Type) -> Type:
    name: str = cls.__name__
    if name not in _PLUGIN_REGISTRY:
        _PLUGIN_REGISTRY.update({name: cls})
    else:
        logger.error(f"Plugin {name} already registered.", exc_info=True)
        return cls

    logger.debug(f"Registered `{name}` to registry")
    return cls


def get_plugin(name: str = None) -> Type | dict[str, Type] | None:
    if name is None:
        return _PLUGIN_REGISTRY
    if name not in _PLUGIN_REGISTRY:
        logger.error(f"Plugin {name} not registered.\nREGISTER: {_PLUGIN_REGISTRY}", exc_info=True)
        return
    logger.debug(f"Looking up PLUGIN_REGISTRY for name: {name}")
    return _PLUGIN_REGISTRY[name]
