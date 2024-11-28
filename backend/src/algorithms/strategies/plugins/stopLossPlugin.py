from backend.src.services.entities import ProfileModel
from . import BasePlugin, PluginPriority

class StopLossPlugin(BasePlugin):
    def __init__(self, stop_loss: dict[str, float]):
        super().__init__(PluginPriority.AFTER_EVALUATION)
        self.stop_loss: dict[str, float] = stop_loss


    def run(self, strategy):
        ...





