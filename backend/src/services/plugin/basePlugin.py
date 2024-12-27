from abc import ABC, abstractmethod
from enum import Enum

from src.utils.registry import plugin_registry


class PluginJob(Enum):
    BEFORE_EVALUATION = 1
    AFTER_EVALUATION = 2
    CREATE_ORDER = 3


# REMAKE: Check how to make the arguments passed only when needed so that not every functions needs to take Strategy as a Argument
class BasePlugin(ABC):
    def __init_subclass__(cls, **kwargs):
        plugin_registry.register(keys=cls.__name__, value=cls)

    def __init__(self, profile: "Profile", job: PluginJob):
        self.profile: "Profile" = profile
        self.job: PluginJob = job

    @abstractmethod
    def run(
        self,
        indicator_confidences: dict[str, dict[int, float]] = None,
    ): ...