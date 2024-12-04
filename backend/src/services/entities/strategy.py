from backend.src.services.plugin import BasePlugin
from backend.src.utils.registry import indicator_registry, plugin_registry
from backend.src.database import get_indicator, get_plugin, delete_plugin, create_plugin, Plugin


class BaseStrategy:
    def __init__(self, profile: 'ProfileModel', buy_limit: float = 0.75, sell_limit: float = -0.75):
        """
        Initialize the strategy.

        :param profile: Profile model associated with the strategy
        """
        self.profile: 'ProfileModel' = profile
        self.indicators: dict[str, dict[str, any]] = self.load_indicators(profile.profile_id, profile.wallet)
        self.plugins: dict[int, BasePlugin] = self.load_plugins(profile.profile_id)
        self.buy_limit: float = buy_limit
        self.sell_limit: float = sell_limit

    @staticmethod
    def load_indicators(profile_id: int, profile_wallet: dict[str, float]) -> dict[str, dict[str, any]]:
        """
        Load indicators for a given profile.

        :param profile_id: ID of the profile
        :param profile_wallet: Wallet associated with the profile
        :return: Dictionary of indicators, keyed by ticker and then by indicator ID
        """
        indicators: dict[str, dict[str, any]] = {}

        for ticker in profile_wallet.keys():
            indicators[ticker] = {}

            for indicator in get_indicator(profile_id=profile_id, ticker=ticker):
                indicators[indicator.ticker][indicator.indicator_id] = {
                    "indicator_model": indicator,
                    "indicator": indicator_registry.get(indicator.indicator_name)(**indicator.indicator_settings)
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

        for plugin in get_plugin(profile_id=profile_id):
            plugins[plugin.plugin_id] = plugin_registry.get(plugin.plugin_name)(**plugin.plugin_settings)

        return plugins


    def evaluate(self):
        ...


    def backtest(self):
        ...

    def add_plugin(self, plugin: BasePlugin) -> bool:
        """
        Adds a plugin from the strategy.

        :param plugin: The plugin to be added.
        :return: True if the plugin was added successfully, False otherwise.
        """
        new_plugin: Plugin = create_plugin(profile_id=self.profile.profile_id, plugin_name=plugin.__name__,
                                           plugin_settings=plugin.__dict__)
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
        if delete_plugin(plugin_id=plugin_id):
            del self.plugins[plugin_id]
            return True
        return False