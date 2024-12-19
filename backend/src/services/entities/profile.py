from enum import Enum
from logging import getLogger
from threading import Lock

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.schedulers.background import BackgroundScheduler

from src.database import get_plugin

from src.api import fetch_historical_data
from src.database import create_plugin, delete_indicator, create_indicator
from src.api import fetch_info_data
from src.database import (IndicatorDTO, PluginDTO, ProfileDTO, get_indicator,
                          update_profile, delete_plugin)
from src.services.indicators import BaseIndicator
from src.utils.registry import profile_registry

from src.services.plugin import PluginJob

#getenv
BROKER_API: str = ""

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
    INACTIVE: int = 0
    ACTIVE: int = 1
    PAPER_TRADING: int = 2
    GRADIANT_EXIT: int = 3
    UNKNOWN_ERROR = 100


class Profile:
    def __init__(self, profile: ProfileDTO):
        self.id: int = profile.id
        self.name: str = profile.name
        self.status: Status = Status(profile.status)
        self.balance: float = profile.balance
        self.wallet: dict[str, float] = profile.wallet
        self.paper_balance: float = profile.paper_balance
        self.paper_wallet: dict[str, float] = profile.paper_wallet

        self.indicators: list[IndicatorDTO] = get_indicator(profile_id=profile.id)
        self.plugins: list[PluginDTO] = get_plugin(profile_id=profile.id)
        self.buy_limit: float = profile.buy_limit
        self.sell_limit: float = profile.sell_limit

        profile_registry.register([self.id], self)

        self._lock = Lock()

        self.scheduler = BackgroundScheduler()
        self._setup_schedular()

        if self.status == Status.ACTIVE or self.status == Status.PAPER_TRADING:
            self.activate(run_on_start=False)

        logger.debug(
            f"Initialized Profile with ID {self.id} and name: {self.name}",
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

        if update_profile(self.id, status=self.status.value):
            logger.info(
                f"Activated Profile with ID {self.id} and name: {self.name}",
                extra={"profile_id": self.id},
            )

            return True
        else:
            logger.error(
                f"Failed to activate Profile with ID {self.id} and name: {self.name}. Deactivating Profile",
                extra={"profile_id": self.id},
            )
            self.deactivate()

            return False

    def activate_paper_trading(self, run_on_start: bool = False):
        if not self._check_status_valid():
            return

        self.status = Status.PAPER_TRADING

        if run_on_start:
            self.evaluate()

        if not self.scheduler.running:
            self.scheduler.start()

        if update_profile(self.id, status=self.status.value):
            logger.info(
                f"Activated Profile with ID {self.id} and name: {self.name}",
                extra={"profile_id": self.id},
            )

            return True
        else:
            logger.error(
                f"Failed to activate Profile with ID {self.id} and name: {self.name}. Deactivating Profile",
                extra={"profile_id": self.id},
            )
            self.deactivate()

            return False

    def deactivate(self):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)

        self.status = Status.INACTIVE
        logger.info(
            f"Deactivated Profile with ID {self.id} and name: {self.name}",
            extra={"profile_id": self.id},
        )

        if update_profile(self.id, status=self.status.value):
            logger.info(
                f"Deactivated Profile with ID {self.id} and name: {self.name}",
                extra={"profile_id": self.id},
            )
            return True

        else:
            logger.error(
                f"Failed to deactivate Profile with ID {self.id} and name: {self.name}.\n"
                f"Due to Risk Reasons Profile will stay locally deactivated. Pls note that on a restart the Profile will be Active.",
                extra={"profile_id": self.id},
            )
            return False
            # TODO: add status not sync to Status

    def evaluate(self):
        if not self._check_status_valid():
            return

        with self._lock:
            for plugin in self.plugins:
                if plugin.instance.job == PluginJob.BEFORE_EVALUATION:
                    plugin.instance.evaluate(self)

            confidences: dict[str, dict[int, float]] = {}
            for indicator in self.indicators:
                if not BROKER_API:
                    df = fetch_historical_data(ticker=indicator.ticker, period="6mo", interval=indicator.interval)

                confidence = indicator.instance.evaluate(df=df)
                confidence[indicator.ticker][indicator.id] = confidence

            for plugin in self.plugins:
                if plugin.instance.job == PluginJob.AFTER_EVALUATION:
                    confidences = plugin.instance.evaluate(self, confidences=confidences)

            for plugin in self.plugins:
                if plugin.instance.job == PluginJob.CREATE_ORDER:
                    order: dict[str, float] = plugin.instance.evaluate(self, confidences=confidences)
                    break

            logger.info(
                f"Evaluation Finished for Profile with ID {self.id} and name: {self.name}",
                extra={"profile_id": self.id},
            )

        self.trade_agent(order)

    def backtest(self) -> dict[str, float] | None:
        if not self._check_status_valid():
            return

        with self._lock:
            ...

            logger.info(
                f"Backtesting for Profile with ID {self.id} and name: {self.name}",
                extra={"profile_id": self.id}, )

        return ...

    def trade_agent(self, orders: dict[str, float]):
        if not self._check_status_valid():
            return

        if self.status == Status.PAPER_TRADING:
            self._paper_trade_agent(orders)
        elif self.status == Status.ACTIVE:
            # self._live_trade_agent(orders)
            ...

    def _paper_trade_agent(self, orders: dict[str, float]):
        for ticker, money_allocation in orders.items():
            ticker_current_price = fetch_info_data(ticker)["currentPrice"]

            if money_allocation < 0:
                num_of_assets: float = self.paper_wallet[ticker]

                self.paper_balance += num_of_assets * ticker_current_price
                self.paper_wallet[ticker] = 0

                logger.info(f"Profile with id {self.id} Sold {num_of_assets} of {ticker} at {ticker_current_price}",
                            extra={"profile_id": self.id, "ticker": ticker})

        for ticker, money_allocation in orders.items():
            ticker_current_price = fetch_info_data(ticker)["currentPrice"]

            if money_allocation > 0:
                num_of_shares: float = (self.paper_balance * money_allocation) / ticker_current_price

                self.paper_wallet[ticker] += num_of_shares
                self.paper_balance -= (self.paper_balance * money_allocation)

                logger.info(
                    f"Profile with id {self.id} Bought {num_of_shares} of {ticker} at {ticker_current_price}",
                    extra={"profile_id": self.id, "ticker": ticker})

        if not update_profile(self.id, paper_balance=self.paper_balance, paper_wallet=self.paper_wallet):
            logger.error(
                f"Failed to update Profile with id: {self.id}; and name: {self.name}",
                extra={"profile_id": self.id},
            )

    def update_wallet(self, wallet: dict[str, float]):
        with self._lock:
            if not update_profile(self.id, wallet=wallet):
                logger.error(
                    f"Failed to update Profile with id: {self.id}; and name: {self.name}",
                )
                return False
            else:
                self.wallet = wallet
                logger.info(
                    f"Updated Walled of Profile with id: {self.id}; and name: {self.name} to wallet: {self.wallet}"
                )
                return True

    def add_indicator(self, indicator: 'BaseIndicator', weight: float, ticker: str, interval: str):
        with self._lock:
            new_indicator: IndicatorDTO = create_indicator(
                profile_id=self.id,
                name=indicator.__class__.__name__,
                weight=weight,
                ticker=ticker,
                interval=interval,
                settings=indicator.__dict__,
            )
            if new_indicator is not None:
                self.indicators.append(new_indicator)
                logger.info(f"Added indicator with ID {new_indicator.id} to profile with ID {self.id}.",
                            extra={"profile_id": self.id})
                self._update_scheduler()

                return True

        logger.error(f"Failed to add indicator to profile with ID {self.id}.",
                     extra={"profile_id": self.id})
        return False


    def remove_indicator(self, indicator_dto: IndicatorDTO):
        with self._lock:
            if delete_indicator(id=indicator_dto.id):
                self.indicators.remove(indicator_dto)

                logger.info(f"Removed indicator with ID {indicator_dto.id} from profile with ID {self.id}.",
                            extra={"profile_id": self.id})
                return True

        logger.error(
            f"Failed to remove indicator with ID {indicator_dto.id} from profile with ID {self.id}.",
            extra={"profile_id": self.id})
        return False

    def add_plugin(self, plugin: 'BasePlugin'):
        with self._lock:
            new_plugin: PluginDTO = create_plugin(
                profile_id=self.id,
                name=plugin.__name__,
                settings=plugin.__dict__,
            )

            if new_plugin is None:
                logger.error(f"Failed to add plugin to profile with ID {self.id}.",
                             extra={"profile_id": self.id})
                return False

            if new_plugin.instance.job == PluginJob.CREATE_ORDER:
                for plugin in self.plugins:
                    if plugin.instance.job == PluginJob.CREATE_ORDER:
                        logger.info(
                            f"User tried to add multiple create order plugins to profile with ID {self.id}.",
                            extra={"profile_id": self.id})
                        return False

            self.plugins.append(new_plugin)

            logger.info(f"Added plugin with ID {new_plugin.id} to profile with ID {self.id}.",
                        extra={"profile_id": self.id})
            return True

    def remove_plugin(self, plugin_dto: PluginDTO):
        with self._lock:
            if delete_plugin(id=plugin_dto.id):
                self.plugins.remove(plugin_dto)

                logger.info(f"Removed plugin with ID {plugin_dto.id} from profile with ID {self.id}.",
                            extra={"profile_id": self.id})
                return True

        logger.error(f"Failed to remove plugin with ID {plugin_dto.id} from profile with ID {self.id}.",
                     extra={"profile_id": self.id})
        return False

    def _setup_schedular(self):
        self.scheduler.add_listener(
            self._on_job_execution, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR
        )

        logger.info(
            f"Initialized Scheduler for Profile with ID {self.id} and name: {self.name}",
            extra={"profile_id": self.id},
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

        logger.info(
            f"Updated Scheduler minutes for Profile with ID {self.id} and name: {self.name}",
            extra={"profile_id": self.id},
        )

    def _check_status_valid(self):
        if self.status.value >= Status.UNKNOWN_ERROR.value:
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
                f"Job {event.job_id} for profile {self.name} with id {self.id} failed to execute. Status: {self.status}",
                exc_info=True,
                extra={"profile_id": self.id},
            )
        else:
            logger.debug(
                f"Job {event.job_id} for profile {self.name} with id {self.id} executed successfully.",
                extra={"profile_id": self.id},
            )
