from src.services.plugin.basePlugin import BasePlugin, PluginJob


class LinearMoneyAllocationPlugin(BasePlugin):
    def __init__(self, strategy: "BaseStrategy"):
        super().__init__(PluginJob.CREATE_ORDER, strategy)

    @staticmethod
    def run(self, strategy: "BaseStrategy", indicator_confidences: dict[str, dict[int, float]] = None):
        order: dict[str, float] = {}

        ticker_confidences: dict[str, float] = {}
        for ticker in indicator_confidences.keys():
            ticker_confidences[ticker] = sum(indicator_confidences[ticker].values())

        confidence_sum: float = sum(ticker_confidences.values())
        for ticker, confidence in ticker_confidences.items():
            order[ticker] = confidence / confidence_sum

        return order