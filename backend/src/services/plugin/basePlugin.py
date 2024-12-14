from abc import ABC, abstractmethod
from enum import Enum

from src.utils.registry import plugin_registry


class PluginJob(Enum):
    BEFORE_EVALUATION = 1
    AFTER_EVALUATION = 2
    CREATE_ORDER = 3


class BasePlugin(ABC):
    def __init_subclass__(cls, **kwargs):
        plugin_registry.register(keys=cls.__name__, value=cls)

    def __init__(self, strategy: "BaseStrategy", job: PluginJob):
        self.strategy: "BaseStrategy" = strategy
        self.job: PluginJob = job

    @abstractmethod
    def run(
        self,
        strategy: "BaseStrategy",  # type: ignore
        indicator_confidences: dict[str, dict[int, float]] = None,
    ): ...