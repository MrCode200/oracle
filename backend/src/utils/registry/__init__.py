from logging import getLogger

from .baseRegistry import BaseRegistry

logger = getLogger("oracle.app")

indicator_registry: BaseRegistry = BaseRegistry(registry_name="indicator_registry", raise_exception=False, log=True,
                                                logger=logger)
profile_registry: BaseRegistry = BaseRegistry(registry_name="profile_registry", raise_exception=False, log=True,
                                              logger=logger)
plugin_registry: BaseRegistry = BaseRegistry(registry_name="plugin_registry", raise_exception=False, log=True,
                                             logger=logger)
command_registry: BaseRegistry = BaseRegistry(registry_name="command_registry", raise_exception=False, log=True,
                                              logger=logger)
