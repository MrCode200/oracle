from typing import Optional

from src.services.plugin.basePlugin import BasePlugin, PluginJob


class LinearMoneyAllocationPlugin(BasePlugin):
    job = PluginJob.CREATE_ORDER

    def run(self, profile: "Profile", tc_confidences: Optional[dict[str, dict[int, float]]] = None):
        order: dict[str, float] = {}

        ticker_confidences: dict[str, float] = {}
        for ticker in tc_confidences.keys():
            ticker_confidences[ticker] = sum(tc_confidences[ticker].values())

        confidence_sum: float = sum(ticker_confidences.values())

        if confidence_sum == 0:
            return order

        for ticker, confidence in ticker_confidences.items():
            order[ticker] = confidence / confidence_sum

        return order