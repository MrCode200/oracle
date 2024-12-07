from enum import Enum
from logging import getLogger

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.schedulers.background import BackgroundScheduler

from backend.src.database import ProfileModel, create_plugin, get_indicator, IndicatorDTO, ProfileDTO, PluginDTO, \
    update_profile
from .strategy import BaseStrategy
from backend.src.utils.registry import profile_registry
from ..indicators import BaseIndicator
from ...api import fetch_info_data

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


class Profile:
    def __init__(self, profile: ProfileDTO):
        self.id: int = profile.id
        self.profile_name: str = profile.name
        self.status: Status = Status(profile.status)
        self.balance: float = profile.balance
        self.wallet: dict[str, float] = profile.wallet
        self.paper_balance: float = profile.paper_balance
        self.paper_wallet: dict[str, float] = profile.paper_wallet
        self.strategy: BaseStrategy = BaseStrategy(
            profile=self, **profile.strategy_settings
        )

        profile_registry.register(self.id, self)

        self.scheduler = BackgroundScheduler()
        self._setup_schedular()
        logger.debug(
            f"Initialized Profile with id: {self.id}; and name: {self.profile_name}",
            extra={"profile_id": self.id},
        )

    def activate(self, run_on_start: bool = False):
        if not self._check_status_valid():
            return
        self.status = Status.ACTIVE

        if run_on_start:
            self.evaluate()

        if not self.scheduler.running:
            self.scheduler.start()
        logger.info(
            f"Activated Profile with id: {self.id}; and name: {self.profile_name}",
            extra={"profile_id": self.id},
        )

    def deactivate(self):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
        self.status = Status.INACTIVE
        logger.info(
            f"Deactivated Profile with id: {self.id}; and name: {self.profile_name}",
            extra={"profile_id": self.id},
        )

    def evaluate(self):
        if not self._check_status_valid():
            return

        self.strategy.evaluate()

        logger.debug(
            f"Evaluation Finished for Profile with id: {self.id}; and name: {self.profile_name}",
            extra={"profile_id": self.id},
        )

    def backtest(self):
        if not self._check_status_valid():
            return

        return self.strategy.backtest()

    def trade_agent(self, orders: dict[str, float]):
        if not self._check_status_valid():
            return

        if self.status == Status.PAPER_TRADING:
            self._paper_trade_agent(orders)

    def _paper_trade_agent(self, orders: dict[str, float]):
        for ticker, money_allocation in orders.items():
            ticker_current_price = fetch_info_data(ticker)["currentPrice"]

            if money_allocation < 0:
                num_of_assets: float = self.paper_wallet[ticker]

                self.paper_balance += num_of_assets * ticker_current_price
                self.paper_wallet[ticker] = 0

                logger.info(f"Profile with id {self.id} Sold {num_of_assets} of {ticker} at {ticker_current_price}",
                            extra={"profile_id": self.id, "ticker": ticker})

            elif money_allocation > 0:
                num_of_shares: float = (self.paper_balance * money_allocation) / ticker_current_price

                self.paper_wallet[ticker] += num_of_shares
                self.paper_balance -= (self.paper_balance * money_allocation)

                logger.info(
                    f"Profile with id {self.id} Bought {num_of_shares} of {ticker} at {ticker_current_price}",
                    extra={"profile_id": self.id, "ticker": ticker})

        if not update_profile(self.id, paper_balance=self.paper_balance, paper_wallet=self.paper_wallet):
            logger.error(
                f"Failed to update Profile with id: {self.id}; and name: {self.profile_name}",
                extra={"profile_id": self.id},
            )

    def add_indicator(self, indicator: 'BaseIndicator', weight: float, ticker: str, interval: str):
        self.strategy.add_indicator(
            indicator=indicator,
            weight=weight,
            ticker=ticker,
            interval=interval
        )

        self._update_scheduler()

    def remove_indicator(self, indicator_dto: IndicatorDTO):
        self.strategy.remove_indicator(indicator_dto)

    def add_plugin(self, plugin: 'BasePlugin'):
        self.strategy.add_plugin(plugin)

    def remove_plugin(self, plugin_dto: PluginDTO):
        self.strategy.remove_plugin(plugin_dto)

    def _setup_schedular(self):
        self.scheduler.add_listener(
            self._on_job_execution, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR
        )

        self._update_scheduler()

    def _update_scheduler(self):
        indicators: list[IndicatorDTO] | IndicatorDTO | None = get_indicator(profile_id=self.id)
        if not indicators:
            logger.info(f"No indicators found for Profile with id: {self.id}", extra={"profile_id": self.id})
            return

        all_intervals: list[int] = [
            interval_to_minutes[indicator.interval]
            for indicator in indicators
        ]

        smallest_interval: int = min(all_intervals)

        if hasattr(self, 'job') and self.job:
            self.job.remove()

        self.job = self.scheduler.add_job(self.evaluate, "interval", minutes=smallest_interval)

    def _check_status_valid(self):
        if self.status.value <= Status.UNKNOWN_ERROR.value:
            logger.error(
                f"Profile with id {self.id} is in error state: {self.status}\nDeactivating Profile",
                extra={"profile_id": self.id},
            )
            self.deactivate()
            return False

        return True

    def _on_job_execution(self, event):
        if event.exception:
            logger.error(
                f"Job {event.job_id} for profile {self.profile_name} with id {self.id} failed to execute. Status: {self.status}",
                exc_info=True,
                extra={"profile_id": self.id},
            )
        else:
            logger.info(
                f"Job {event.job_id} for profile {self.profile_name} with id {self.id} executed successfully.",
                extra={"profile_id": self.id},
            )
