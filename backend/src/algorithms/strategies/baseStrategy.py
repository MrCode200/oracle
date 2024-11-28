from pandas import DataFrame

from .plugins import BasePlugin, PluginPriority
from backend.src.api import fetch_historical_data
from backend.src.utils.registry import indicator_registry, plugin_registry
from backend.src.database import get_indicator, get_plugin, delete_plugin, create_plugin, Plugin


class BaseStrategy:
    def __init__(self, profile: 'ProfileModel'):
        """
        Initialize the strategy.

        :param profile: Profile model associated with the strategy
        """
        self.profile: 'ProfileModel' = profile
        self.indicators: dict[str, dict[str, any]] = self.load_indicators()
        self.plugins: dict[int, BasePlugin] = self.load_plugins()

    @staticmethod
    def load_indicators(profile_id, profile_wallet) -> dict[str, dict[str, any]]:
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
                    "indicator": indicator_registry.get(indicator.indicator_name)(
                        **indicator.indicator_settings)
                }

        return indicators

    @staticmethod
    def load_plugins(profile_id) -> dict[int, BasePlugin]:
        """
        Load plugins for a given profile.

        :param profile_id: ID of the profile
        :return: Dictionary of plugins, keyed by plugin ID
        """
        plugins: dict[int, BasePlugin] = {}

        for plugin in get_plugin(profile_id=profile_id):
            plugins[plugin.plugin_id] = plugin_registry.get(plugin.plugin_name)(**plugin.plugin_settings)

        return plugins

    def evaluate(self) -> dict[str, float]:
        """
        Evaluate the strategy.

        This method evaluates the strategy by running the plugins and indicators,
        and returns a dictionary of ticker confidences.

        :return: Dictionary of ticker confidences
        """
        for plugin in self.plugins.values():
            if plugin.priority == PluginPriority.BEFORE_EVALUATION:
                plugin.run(self)

        indicator_confidences: dict[str, dict[int, float]] = self._eval_indicators()
        # TODO:Just looping through all plugins and giving them the result that was edited, could become problematic in the future depending on the feature of the plugin
        for plugin in self.plugins.values():
            if plugin.priority == PluginPriority.AFTER_EVALUATION:
                indicator_confidences = plugin.run(self, indicator_confidences)

        ticker_averaged_confidences: dict[str, float] = {}
        for ticker, confidences in indicator_confidences.items():
            ticker_averaged_confidences[ticker] = sum(confidences.values()) / len(confidences)

        normalized_confidences: dict[str, float] = {}
        sum_of_confidences: float = sum(ticker_averaged_confidences.values())
        for ticker, confidence in ticker_averaged_confidences.items():
            normalized_confidences[ticker] = confidence / sum_of_confidences

        return normalized_confidences

    def _eval_indicators(self) -> dict[str, dict[int, float]]:
        """
        Evaluate the indicators.

        This method evaluates the indicators for each ticker, and returns a
        dictionary of ticker confidences.

        :return: Dictionary of ticker confidences
        """
        model_confidences: dict[str, dict[int, float]] = {}
        for ticker, indicators in self.indicators.keys():
            ticker_confidences: dict[int, float] = {}

            for indicator_model, indicator in self.indicators[ticker].values():
                data: DataFrame = fetch_historical_data(ticker, **indicator_model.fetch_settings)

                confidence: float = indicator.evaluate(df=data) * indicator_model.weight
                ticker_confidences[indicator_model.indicator_id] = confidence

            model_confidences[ticker] = ticker_confidences

        return model_confidences

    def backtest(self, profile):
        pass

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
