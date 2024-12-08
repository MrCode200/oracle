# For Kiana Bozghale
from src.services.plugin.basePlugin import BasePlugin, PluginPriority


class LinearMoneyAllocationPlugin(BasePlugin):
    def __init__(self, strategy: "BaseStrategy"):
        super().__init__(PluginPriority.BEFORE_EVALUATION, strategy)

    def run(self, strategy: "BaseStrategy", indicator_confidences: dict[str, dict[int, float]] = None):
        pass