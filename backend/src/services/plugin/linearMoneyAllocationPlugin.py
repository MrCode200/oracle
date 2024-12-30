from typing import Optional

from src.services.plugin.basePlugin import BasePlugin, PluginJob


class LinearMoneyAllocationPlugin(BasePlugin):
    job = PluginJob.CREATE_ORDER

    def run(self, profile: "Profile", tc_confidences: Optional[dict[str, dict[int, float]]] = None) -> dict[str, float]:
        order: dict[str, float] = {}

        # Calculate ticker confidences
        confidence_sum: float = 0
        ticker_confidences: dict[str, float] = {}
        for ticker, confidences in tc_confidences.items():
            ticker_confidences[ticker] = sum(confidences.values())
            if ticker_confidences[ticker] > 0:
                confidence_sum += ticker_confidences[ticker]

        if confidence_sum == 0:
            return order

        # Normalize confidence for each ticker based on total sum
        for ticker, confidence in ticker_confidences.items():
            if confidence == 0:
                continue
            elif confidence > 0:
                order[ticker] = confidence / confidence_sum
            else:
                order[ticker] = confidence

        return order