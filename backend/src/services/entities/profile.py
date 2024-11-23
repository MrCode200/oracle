from typing import Type
from logging import getLogger
from dataclasses import dataclass, field
from enum import Enum

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from backend.src.algorithms.strategies.baseStrategy import BaseStrategy

logger = getLogger("oracle.app")

unit_to_minutes = {
    '1m': 1,
    '2m': 2,
    '5m': 5,
    '15m': 15,
    '30m': 30,
    '60m': 60,
    '1h': 60,
    '90m': 90,
    '1d': 1440,
    '5d': 7200,
    '1wk': 10080,
    '1mo': 43200,
    '3mo': 129600,
    '6mo': 259200,
    '1y': 525600,
    '2y': 1051200,
    '5y': 2628000,
    '10y': 5256000,
    'ytd': "notImplemented",  # Example where not available
    'max': "notImplemented"  # Example where not available
}


class Status(Enum):
    INACTIVE = 0
    ACTIVE = 1
    PAPER_TRADING = 2
    GRADIANT_EXIT = 3
    UNKNOWN_ERROR = 100


@dataclass
class Profile:
    profile_id: int
    profile_name: str
    status: Status
    wallet: dict[str, float]
    profile_settings: dict[str, any] # May be subjected to change
    strategy_plugins: dict[str, any] = field(default_factory=dict)
    algorithms_settings: dict[str, dict[str, any]] = field(default_factory=dict)

    def __post_init__(self):
        self.strategy: Type = BaseStrategy(profile=self)

        self.scheduler = BackgroundScheduler()
        self.scheduler.add_listener(self._on_job_execution, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        self.scheduler.add_job(self._evaluate, 'interval', minutes=unit_to_minutes[self.profile_settings['interval']])
        logger.debug(f"Initialized Profile with id: {self.profile_id}; and name: {self.profile_name}",
                     extra={"profile_id": self.profile_id})

    def activate(self, run_on_start: bool = False):
        if not self._check_status_valid():
            return
        self.status = Status.ACTIVE

        if run_on_start:
            self._evaluate()

        self.scheduler.start()
        logger.info(f"Activated Profile with id: {self.profile_id}; and name: {self.profile_name}",
                    extra={"profile_id": self.profile_id})

    def deactivate(self):
        self.scheduler.shutdown(wait=True)
        self.status = Status.INACTIVE
        logger.info(f"Deactivated Profile with id: {self.profile_id}; and name: {self.profile_name}",
                    extra={"profile_id": self.profile_id})

    def _evaluate(self):
        if not self._check_status_valid():
            return

        ...

        logger.debug(f"Evaluation Finished for Profile with id: {self.profile_id}; and name: {self.profile_name}",
                     extra={"profile_id": self.profile_id})

    def backtest(self):
        if not self._check_status_valid():
            return

        ...

    def _check_status_valid(self):
        if self.status.value <= Status.UNKNOWN_ERROR.value:
            logger.error(f"Profile with id {self.profile_id} is in error state: {self.status}\nDeactivating Profile",
                         extra={"profile_id": self.profile_id})
            self.deactivate()
            return False

        return True

    def _on_job_execution(self, event):
        if event.exception:
            logger.error(
                f"Job {event.job_id} for profile {self.profile_name} with id {self.profile_id} failed to execute.",
                exc_info=True, extra={"profile_id": self.profile_id})
        else:
            logger.info(
                f"Job {event.job_id} for profile {self.profile_name} with id {self.profile_id} executed successfully.",
                extra={"profile_id": self.profile_id})
