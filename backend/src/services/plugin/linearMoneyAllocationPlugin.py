# For Kiana Bozghale
from src.services.plugin.basePlugin import BasePlugin, PluginJob


class LinearMoneyAllocationPlugin(BasePlugin):
    def __init__(self, strategy: "BaseStrategy"):
        super().__init__(PluginJob.BEFORE_EVALUATION, strategy)

    def run(self, strategy: "BaseStrategy", indicator_confidences: dict[str, dict[int, float]] = None):
        indicators_avg ={}
        for ticker in indicator_confidences :
            counter = 0
            for i in range(1, len(indicator_confidences[ticker]) + 1):
                counter += indicator_confidences[ticker][i]
            indicators_avg[ticker]=counter/len(indicator_confidences[ticker])
            counter = 0
    
        pass