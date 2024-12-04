from enum import Enum
from logging import getLogger

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.schedulers.background import BackgroundScheduler

from backend.src.database import Profile, get_indicator, create_plugin
from backend.src.services.entities import BaseStrategy
from backend.src.utils.registry import profile_registry

logger = getLogger("oracle.app")

interval_to_minutes = {
    "1m": 1,
    "2m": 2,
    "5m": 5,
    "15m": 15,
    "30m": 30,
    "60m": 60,
    "90m": 90,
    "1h": 60,
    "1d": 1440,
    "5d": 7200,
    "1wk": 10080,
    "1mo": 43200,
    "3mo": 129600,
}


class Status(Enum):
    INACTIVE = 0
    ACTIVE = 1
    PAPER_TRADING = 2
    GRADIANT_EXIT = 3
    UNKNOWN_ERROR = 100


class ProfileModel:
    def __init__(self, profile: Profile):
        self.profile_id: int = profile.profile_id
        self.profile_name: str = profile.profile_name
        self.status: Status = profile.status
        self.wallet: dict[str, float] = profile.wallet
        self.strategy: BaseStrategy = BaseStrategy(
            profile=self, **profile.strategy_settings
        )

        profile_registry.register(self.profile_id, self)

        self.scheduler = BackgroundScheduler()
        self._setup_schedular()
        logger.debug(
            f"Initialized Profile with id: {self.profile_id}; and name: {self.profile_name}",
            extra={"profile_id": self.profile_id},
        )

    def activate(self, run_on_start: bool = False):
        if not self._check_status_valid():
            return
        self.status = Status.ACTIVE

        if run_on_start:
            self._evaluate()

        self.scheduler.start()
        logger.info(
            f"Activated Profile with id: {self.profile_id}; and name: {self.profile_name}",
            extra={"profile_id": self.profile_id},
        )

    def deactivate(self):
        self.scheduler.shutdown(wait=True)
        self.status = Status.INACTIVE
        logger.info(
            f"Deactivated Profile with id: {self.profile_id}; and name: {self.profile_name}",
            extra={"profile_id": self.profile_id},
        )

    def _evaluate(self):
        if not self._check_status_valid():
            return

        self.strategy.determine_trade_signals()

        logger.debug(
            f"Evaluation Finished for Profile with id: {self.profile_id}; and name: {self.profile_name}",
            extra={"profile_id": self.profile_id},
        )

    def backtest(self):
        if not self._check_status_valid():
            return

        return self.strategy.backtest(profile=self)

    def add_plugin(self, plugin: 'BasePlugin', **kwargs):
        # TODO: How to add plugin settings
        new_plugin = create_plugin(
            profile_id=self.profile_id,
            plugin_name=plugin.__class__.__name__,
            plugin_settings=kwargs,
        )
        self.strategy.add_plugin(new_plugin)

    def remove_plugin(self, plugin_id: int):
        self.strategy.remove_plugin(plugin_id)

    def _setup_schedular(self):
        self.scheduler.add_listener(
            self._on_job_execution, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR
        )

        all_intervals = [
            indicator.fetch_settings["interval"]
            for indicator in get_indicator(profile_id=self.profile_id)
        ]
        smallest_interval: int = min(all_intervals, key=interval_to_minutes.get)
        self.scheduler.add_job(self._evaluate, "interval", minutes=smallest_interval)

    def _check_status_valid(self):
        if self.status.value <= Status.UNKNOWN_ERROR.value:
            logger.error(
                f"Profile with id {self.profile_id} is in error state: {self.status}\nDeactivating Profile",
                extra={"profile_id": self.profile_id},
            )
            self.deactivate()
            return False

        return True

    def _on_job_execution(self, event):
        if event.exception:
            logger.error(
                f"Job {event.job_id} for profile {self.profile_name} with id {self.profile_id} failed to execute.",
                exc_info=True,
                extra={"profile_id": self.profile_id},
            )
        else:
            logger.info(
                f"Job {event.job_id} for profile {self.profile_name} with id {self.profile_id} executed successfully.",
                extra={"profile_id": self.profile_id},
            )
