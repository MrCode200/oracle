import logging

logger = logging.getLogger("oracle.app")



from backend.src.api import fetch_historical_data
from backend.src.database import update_indicator
from backend.src.services.plugin import BasePlugin, PluginPriority


class SmartWeightAssignerPlugin(BasePlugin):
    def __init__(self, strategy: 'BaseStrategy', period):
        self.period: str = period
        super().__init__(PluginPriority.BEFORE_EVALUATION, strategy)

    def run(self, indicator_confidences: dict[str, dict[str, float]] = None):
        all_results: dict[str, dict[str, float]] = {}
        for ticker in self.strategy.profile.wallet.keys():
            results: dict[str, float] = {}

            for indicator_instance, indicator_model in self.strategy:
                data = fetch_historical_data(ticker, period=self.period, interval=indicator_model.interval)

                perf_history: list[float] = indicator_instance.backtest(df=data, partition_amount=10) * indicator_model["weight"]
                average_perf: float = sum(perf_history)/len(perf_history)
                results[indicator_model.id] = average_perf

            all_results[ticker] = results

        update_failed_flag: bool = False
        for ticker, perfs in all_results.items():
            sum_of_confidences: float = sum(perfs.values())
            for indicator_id, average_perf in perfs.items():
                if not update_indicator(indicator_id, indicator_weight=average_perf/sum_of_confidences):
                    logger.debug(f"Failed to update the weight of the indicator {indicator_id}")
        if update_failed_flag:
            logger.warning("SmartWeightAssignerPlugin failed to update some indicators")
        else:
            logger.info("SmartWeightAssignerPlugin executed successfully")