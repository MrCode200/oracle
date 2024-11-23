from pandas import DataFrame

from .plugins import BasePlugin, PluginPriority
from backend.src.api import fetch_historical_data
from backend.src.algorithms.indicators import BaseIndicator
from backend.src.utils.registry import indicator_registry, plugin_registry

class BaseStrategy:
    def __init__(self, profile: 'Profile'):
        self.profile = profile

        self.plugins: list[BasePlugin] = []
        for plugin_name, plugin_config in profile.plugin_configs.items():
            self.add_plugin(plugin_registry.get(plugin_name)(**plugin_config))

    def evaluate(self) -> dict[str, float]:
        for plugin in self.plugins:
            if plugin.priority == PluginPriority.BEFORE_EXECUTION:
                plugin.run(self)

        all_results: dict[str, dict[str, float]] = self._eval_all()

        for plugin in self.plugins:
            if plugin.priority == PluginPriority.AFTER_EXECUTION:
                plugin.run(self, all_results)

        return {"coinA": 0.01, "coinB": 0.5}

    def _eval_all(self) -> dict[str, dict[str, float]]:
        """
        Evaluate all indicators for all tickers
        :return: All results as dict[ticker: dict[indicators: result]]
        """
        all_results: dict[str, dict[str, float]] = {}
        for ticker in self.profile.indicator_configs.keys():
            results: dict[str, float] = {}

            for indicator_name, indicator_settings in self.profile.indicator_configs[ticker].items():
                data: DataFrame = fetch_historical_data(ticker, **indicator_settings["fetch_settings"])

                indicator: BaseIndicator = indicator_registry.get(indicator_name)(indicator_settings["settings"])

                result: float = indicator.evaluate(df=data) * indicator_settings["weight"]
                results[indicator_name] = result

            all_results[ticker] = results

        return all_results

    def backtest(self, profile):
        pass

    def add_plugin(self, plugin: BasePlugin) -> None:
        self.plugins.append(plugin)

    def remove_plugin(self, plugin) -> None:
        self.plugins.remove(plugin)

    def db_format(self) -> dict[str, dict[str, any]]:
        return {
            plugin.__name__: plugin.__dict__ for plugin in self.plugins
        }


