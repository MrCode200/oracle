# For Kiana Bozghale
from src.services.plugin.basePlugin import BasePlugin, PluginJob


class LinearMoneyAllocationPlugin(BasePlugin):
    def __init__(self, strategy: "BaseStrategy"):
        super().__init__(PluginJob.BEFORE_EVALUATION, strategy)

    def run(self, strategy: "BaseStrategy", indicator_confidences: dict[str, dict[int, float]] = None):
        pass