from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

from src.utils.registry import plugin_registry
from src.utils import check_annotations_for_init


class PluginJob(Enum):
    BEFORE_EVALUATION = 1
    AFTER_EVALUATION = 2
    CREATE_ORDER = 3


# REMAKE: Check how to make the arguments passed only when needed so that not every functions needs to take Strategy as a Argument
class BasePlugin(ABC):
    job: PluginJob = ...

    def __init_subclass__(cls, **kwargs):
        if 'job' not in cls.__dict__:
            raise TypeError("Plugin must have a job property")

        if not isinstance(cls.job, PluginJob):
            raise TypeError("Plugin job must be of type PluginJob")

        check_annotations_for_init(cls)

        plugin_registry.register(keys=cls.__name__, value=cls)

        super.__init_subclass__(**kwargs)

    @abstractmethod
    def run(
        self,
        profile: "Profile",
        tc_confidences: Optional[dict[str, dict[int, float]]] = None,
    ): ...