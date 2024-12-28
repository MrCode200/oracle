from abc import ABC, abstractmethod, abstractproperty
from enum import Enum
from typing import Optional

from src.utils.registry import plugin_registry


class PluginJob(Enum):
    BEFORE_EVALUATION = 1
    AFTER_EVALUATION = 2
    CREATE_ORDER = 3


# REMAKE: Check how to make the arguments passed only when needed so that not every functions needs to take Strategy as a Argument
class BasePlugin(ABC):
    def __new__(cls, name, bases, dct):
        if 'job' not in dct:
            raise TypeError("Plugin must have a job property")

        if not isinstance(dct['job'], PluginJob):
            raise TypeError("Plugin job must be of type PluginJob")

        return super().__new__(cls, name, bases, dct)


    def __init_subclass__(cls, **kwargs):
        plugin_registry.register(keys=cls.__name__, value=cls)

    @abstractmethod
    def run(
        self,
        profile: "Profile",
        indicator_confidences: Optional[dict[str, dict[int, float]]] = None,
    ): ...