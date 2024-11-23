from enum import Enum
from abc import abstractmethod, ABC

from backend.src.services.entities import Profile


class PluginPriority(Enum):
    BEFORE_EXECUTION = 1
    TAKES_RESULT = 2
    AFTER_EXECUTION = 3


class BasePlugin(ABC):
    def __init__(self, priority: PluginPriority):
        self.priority: PluginPriority = priority

    @abstractmethod
    def run(self, profile: Profile):
        ...
