from typing import Optional

from src.services.entities.plugin.basePlugin import BasePlugin, PluginJob


class LinearMoneyAllocationPlugin(BasePlugin):
    job = PluginJob.CREATE_ORDER

    def run(self, profile: "Profile", tc_confidences: Optional[dict[str, dict[int, float]]] = None) -> dict[str, float]:
        order: dict[str, float] = {}

        # Calculate ticker confidences
        buy_confidence_sum: float = 0
        ticker_confidences: dict[str, float] = {}
        for ticker, confidences in tc_confidences.items():
            if confidences == {}:
                continue

            average_ticker_conf: float = sum(confidences.values()) / len(confidences)
            if average_ticker_conf == 0:
                continue

            ticker_confidences[ticker] = average_ticker_conf
            if ticker_confidences[ticker] > 0:
                buy_confidence_sum += ticker_confidences[ticker]

        # Normalize confidence for each ticker based on total sum
        for ticker, confidence in ticker_confidences.items():
            if confidence >= profile.buy_limit:
                order[ticker] = confidence / buy_confidence_sum
            elif confidence <= profile.sell_limit:
                order[ticker] = confidence

        return order