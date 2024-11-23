from queue import PriorityQueue

from pandas import DataFrame

from .plugins import BasePlugin
from backend.src.algorithms.strategies.utils import get_plugin
from backend.src.services.entities import Profile
from ...api import fetch_historical_data
from backend.src.algorithms.indicators.utils import get_indicator
from backend.src.algorithms.indicators import BaseIndicator


class BaseStrategy:
    def __init__(self, profile):
        strategy_plugins = profile.algorithms_settings["strategy_plugins"]
        self.plugin_queue: PriorityQueue = PriorityQueue()

        for plugin_name, plugin_settings in strategy_plugins.items():
            self.add_plugin(get_plugin(plugin_name)(**plugin_settings))

    def evaluate(self, profile: Profile) -> dict[str, float]:
        all_results: dict[str, dict[str, float]] = {}
        for ticker in profile.algorithms_settings.keys():
            results: dict[str, float] = {}

            for indicator_name, indicator_settings in profile.algorithms_settings[ticker].items():
                data: DataFrame = fetch_historical_data(ticker, **indicator_settings["fetch_settings"])
                indicator: BaseIndicator = get_indicator(indicator_name)(indicator_settings["settings"])
                result: float = indicator.evaluate(df=data) * indicator_settings["weight"]
                results[indicator_name] = result

            all_results[ticker] = results

        """while not self.plugin_queue.empty():
            _, plugin = self.plugin_queue.get()
            plugin.run(profile, all_results)"""

        return {"coinA": 0.01, "coinB": 0.5}

    def add_plugin(self, plugin: BasePlugin):
        self.plugin_queue.put((plugin.priority, plugin))

    def remove_plugin(self, plugin):
        new_queue = PriorityQueue()
        while not self.plugin_queue.empty():
            priority, current_plugin = self.plugin_queue.get()
            if current_plugin != plugin:
                new_queue.put((priority, current_plugin))
        self.plugin_queue = new_queue

    def __repr__(self):
        ...
