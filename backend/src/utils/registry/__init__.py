from logging import getLogger

from .registry import Registry  # type: ignore

logger = getLogger("oracle.app")

tc_registry: Registry = Registry(
    registry_name="tc_registry", raise_exception=False, log=True, logger=logger
)
profile_registry: Registry = Registry(
    registry_name="profile_registry", raise_exception=False, log=True, logger=logger
)
plugin_registry: Registry = Registry(
    registry_name="plugin_registry", raise_exception=False, log=True, logger=logger
)
command_registry: Registry = Registry(
    registry_name="command_registry", raise_exception=False, log=True, logger=logger
)
