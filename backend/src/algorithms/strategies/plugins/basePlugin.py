from enum import Enum
from abc import abstractmethod, ABC

from backend.src.utils.registry import plugin_registry

class PluginPriority(Enum):
    BEFORE_EVALUATION = 1
    AFTER_EVALUATION = 2


class BasePlugin(ABC):
    def __init_subclass__(cls, **kwargs):
        plugin_registry.register(keys=cls.__name__, value=cls)

    def __init__(self, priority: PluginPriority):
        self.priority: PluginPriority = priority

    @abstractmethod
    def run(self, strategy: 'BaseStrategy', indicator_confidences: dict[str, dict[int, float]] = None):
        ...
