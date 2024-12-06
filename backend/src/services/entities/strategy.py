from backend.src.database import (
    PluginModel,
    create_plugin,
    delete_plugin,
    get_indicator,
    get_plugin, Indicator, create_indicator, delete_indicator,
)
from backend.src.services.indicators import BaseIndicator
from backend.src.services.plugin import BasePlugin
from backend.src.utils.registry import indicator_registry, plugin_registry


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
        self.indicators: dict[str, dict[str, any]] = self.load_indicators(
            profile.id, profile.wallet
        )
        self.plugins: dict[int, BasePlugin] = self.load_plugins(profile.id)
        self.buy_limit: float = buy_limit
        self.sell_limit: float = sell_limit

    @staticmethod
    def load_indicators(
        profile_id: int, profile_wallet: dict[str, float]
    ) -> dict[str, dict[str, any]]:
        """
        Load indicators for a given profile.

        :param profile_id: ID of the profile
        :param profile_wallet: Wallet associated with the profile
        :return: Dictionary of indicators, keyed by ticker and then by indicator ID
        """
        indicators: dict[str, dict[str, any]] = {}

        indicators_data: list[BaseIndicator] | BaseIndicator = get_indicator(
            profile_id=profile_id
        )

        if indicators_data is None:
            return {}

        if not isinstance(indicators_data, list):
            indicators_data = [indicators_data]

        for indicator in indicators_data:
            indicators[indicator.id] = {
                "indicator_data": indicator,
                "indicator_instance": indicator_registry.get(indicator.name)(
                    **indicator.settings
                ),
            }

        return indicators

    @staticmethod
    def load_plugins(profile_id: int) -> dict[int, BasePlugin]:
        """
        Load plugins for a given profile.

        :param profile_id: ID of the profile
        :return: Dictionary of plugins, keyed by plugin ID
        """
        plugins: dict[int, BasePlugin] = {}

        plugins_models: list[PluginModel] | PluginModel = get_plugin(profile_id=profile_id)

        if plugins_models is None:
            return {}

        if not isinstance(plugins_models, list):
            plugins_models = [plugins_models]

        for plugin in plugins_models:
            plugins[plugin.id] = plugin_registry.get(plugin.name)(
                **plugin.settings
            )

        return plugins

    def evaluate(self): ...

    def backtest(self): ...
    def add_indicatorDTO (self,indicator: BaseIndicator) ->bool :

        new_indicator:Indicator = create_indicator()#TODO
        if indicator is not None:
            self.plugins[new_indicator.plugin_id] = indicator
            return True
        return False
    def remove_indicatorDTO(self,id) ->bool :
        if delete_indicator(plugin_id=id):
            del self.plugins[id]
            return True
        return False

    def add_plugin(self, plugin: BasePlugin) -> bool:
        """
        Adds a plugin from the strategy.

        :param plugin: The plugin to be added.
        :return: True if the plugin was added successfully, False otherwise.
        """
        new_plugin: PluginModel = create_plugin(
            profile_id=self.profile.id,
            name=plugin.__name__,
            settings=plugin.__dict__,
        )
        if plugin is not None:
            self.plugins[new_plugin.plugin_id] = plugin
            return True
        return False

    def remove_plugin(self, plugin_id: int) -> bool:
        """
        Removes a plugin from the strategy.

        :param plugin_id: The ID of the plugin to be removed.
        :return: True if the plugin was removed successfully, False otherwise.
        """
        if delete_plugin(id=plugin_id):
            del self.plugins[plugin_id]
            return True
        return False
