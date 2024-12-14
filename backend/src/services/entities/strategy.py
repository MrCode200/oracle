import logging

from build.lib.services.plugin import PluginPriority
from src.database import (IndicatorDTO, PluginDTO, PluginModel,
                          create_indicator, create_plugin, delete_indicator,
                          delete_plugin, get_indicator, get_plugin)
from src.services.indicators import BaseIndicator
from src.services.plugin import BasePlugin
from src.utils.registry import indicator_registry, plugin_registry

logger = logging.getLogger("oracle.app")


class BaseStrategy:
    def __init__(
            self,
            profile: "ProfileModel",
            buy_limit: float = 0.75,
            sell_limit: float = -0.75,
    ):
        """
        Initialize the strategy.

        :param profile: Profile model associated with the strategy
        """
        self.profile: "ProfileModel" = profile
        self.indicators: list[IndicatorDTO] = get_indicator(profile_id=profile.id)
        self.plugins: list[PluginDTO] = get_plugin(profile_id=profile.id)
        self.buy_limit: float = buy_limit
        self.sell_limit: float = sell_limit

    def evaluate(self):
        ...

    def backtest(self):
        ...

    def add_indicator(self, indicator: BaseIndicator, weight: float, ticker: str, interval: str) -> bool:
        new_indicator: IndicatorDTO = create_indicator(
            profile_id=self.profile.id,
            name=indicator.__class__.__name__,
            weight=weight,
            ticker=ticker,
            interval=interval,
            settings=indicator.__dict__,
        )
        if new_indicator is not None:
            self.indicators.append(new_indicator)
            logger.info(f"Added indicator with ID {new_indicator.id} to profile with ID {self.profile.id}.",
                        extra={"profile_id": self.profile.id})
            return True
        logger.error(f"Failed to add indicator to profile with ID {self.profile.id}.",
                     extra={"profile_id": self.profile.id})
        return False

    def remove_indicator(self, indicator_dto: IndicatorDTO) -> bool:
        if delete_indicator(id=indicator_dto.id):
            self.indicators.remove(indicator_dto)

            logger.info(f"Removed indicator with ID {indicator_dto.id} from profile with ID {self.profile.id}.",
                        extra={"profile_id": self.profile.id})
            return True

        logger.error(f"Failed to remove indicator with ID {indicator_dto.id} from profile with ID {self.profile.id}.",
                     extra={"profile_id": self.profile.id})
        return False

    def add_plugin(self, plugin: BasePlugin) -> bool:
        """
        Adds a plugin from the strategy.

        :param plugin: The plugin to be added.
        :return: True if the plugin was added successfully, False otherwise.
        """
        new_plugin: PluginDTO = create_plugin(
            profile_id=self.profile.id,
            name=plugin.__name__,
            settings=plugin.__dict__,
        )

        if new_plugin is None:
            logger.error(f"Failed to add plugin to profile with ID {self.profile.id}.",
                         extra={"profile_id": self.profile.id})
            return False

        if new_plugin.instance.job == PluginPriority.CREATE_ORDER:
            for plugin in self.plugins:
                if plugin.instance.job == PluginPriority.CREATE_ORDER:
                    logger.info(
                        f"User tried to add multiple create order plugins to profile with ID {self.profile.id}.",
                        extra={"profile_id": self.profile.id})
                    return False

        self.plugins.append(new_plugin)

        logger.info(f"Added plugin with ID {new_plugin.id} to profile with ID {self.profile.id}.",
                    extra={"profile_id": self.profile.id})
        return True

    def remove_plugin(self, plugin_dto: PluginDTO) -> bool:
        """
        Removes a plugin from the strategy.

        :param plugin_dto: The plugin to be removed.
        :return: True if the plugin was removed successfully, False otherwise.
        """
        if delete_plugin(id=plugin_dto.id):
            self.plugins.remove(plugin_dto)

            logger.info(f"Removed plugin with ID {plugin_dto.id} from profile with ID {self.profile.id}.",
                        extra={"profile_id": self.profile.id})
            return True

        logger.error(f"Failed to remove plugin with ID {plugin_dto.id} from profile with ID {self.profile.id}.",
                     extra={"profile_id": self.profile.id})
        return False
