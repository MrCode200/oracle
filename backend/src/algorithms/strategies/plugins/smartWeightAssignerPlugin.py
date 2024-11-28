from backend.src.algorithms.strategies import BaseStrategy
from backend.src.algorithms.strategies.plugins import BasePlugin, PluginPriority
from backend.src.api import fetch_historical_data


class SmartWeightAssignerPlugin(BasePlugin):
    def __init__(self):
        super().__init__(PluginPriority.BEFORE_EVALUATION)

    def run(self, strategy: BaseStrategy, indicator_confidences: dict[str, dict[str, float]] = None):
        all_results: dict[str, dict[str, float]] = {}
        for ticker, ticker_settings in strategy.profile.algorithms_settings.items():
            results: dict[str, float] = {}

            for indicator_name, indicator_settings in ticker_settings.items():
                data = fetch_historical_data(ticker, **indicator_settings["fetch_settings"])

                perf_history: list[float] = indicator_settings["indicator"].backtest(df=data, partition_amount=10) * indicator_settings["weight"]
                average_perf: float = sum(perf_history)/len(perf_history)
                results[indicator_name] = average_perf

            all_results[ticker] = results

        for ticker, perfs in all_results.items():
            sum_of_confidences: float = sum(perfs.values())
            for indicator_name, confidence in perfs.items():
                strategy.profile.algorithms_settings[ticker][indicator_name]["weight"] = confidence/sum_of_confidences