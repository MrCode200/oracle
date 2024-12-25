from logging import getLogger
from threading import Lock
from typing import Optional

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.schedulers.background import BackgroundScheduler

from src.database import get_plugin

from src.api import fetch_historical_data
from src.api import fetch_info_data
from backend.src.database import (IndicatorDTO, PluginDTO, ProfileDTO, get_indicator,
                                  update_profile, delete_plugin, update_indicator,
                                  create_plugin, create_indicator, update_plugin, delete_indicator)
from src.services.indicators import BaseIndicator
from src.utils.registry import profile_registry
from src.services.constants import Status

from src.services.plugin import PluginJob

# getenv
BROKER_API: str = ""

logger = getLogger("oracle.app")


class Profile:
    def __init__(self, profile: ProfileDTO):
        self.id: int = profile.id
        self.name: str = profile.name
        self.status: Status = Status(profile.status)
        self.balance: float = profile.balance
        self.wallet: dict[str, float] = profile.wallet
        self.paper_balance: float = profile.paper_balance
        self.paper_wallet: dict[str, float] = profile.paper_wallet

        # REMAKE: dict[id, indicatorDTO] and also for plugin
        self.indicators: list[IndicatorDTO] = get_indicator(profile_id=profile.id)
        self.plugins: list[PluginDTO] = get_plugin(profile_id=profile.id)
        self.buy_limit: float = profile.buy_limit
        self.sell_limit: float = profile.sell_limit

        profile_registry.register([self.id], self)

        self._lock = Lock()

        self.scheduler = BackgroundScheduler()
        self._setup_schedular()

        logger.debug(
            f"Initialized Profile with ID {self.id} and name: {self.name}",
            extra={"profile_id": self.id},
        )

    def change_status(self, status: Status, run_on_start: bool = False):
        if status == Status.INACTIVE or status.value >= Status.UNKNOWN_ERROR.value:
            if self.scheduler.running:
                self.scheduler.shutdown(wait=True)

        else:
            if not self._check_status_valid():
                return

            if run_on_start:
                self.evaluate()

            if not self.scheduler.running:
                self.scheduler.start()

        self.status = status

        if update_profile(self.id, status=self.status.value):
            logger.info(
                f"Changed Status for Profile with ID {self.id} and name: {self.name} to {self.status}",
                extra={"profile_id": self.id},
            )

            return True
        else:
            logger.error(
                f"Failed to change Status for Profile with ID {self.id} and name: {self.name} to {self.status}, deactivating profile",
                extra={"profile_id": self.id},
            )

            # Deactivate profile only if scheduler is running so that it doesn't get stuck in a loop
            if self.scheduler.running:
                self.change_status(Status.INACTIVE)

            return False

    def evaluate(self):
        if not self._check_status_valid():
            return

        if not self._check_has_create_order_plugin():
            return

        confidences: dict[str, dict[int, float]] = {}
        for ticker in self.wallet.keys():
            confidences[ticker] = {}

        with self._lock:
            for plugin in self.plugins:
                if plugin.instance.job == PluginJob.BEFORE_EVALUATION:
                    plugin.instance.evaluate(self)

            for indicator in self.indicators:
                if not BROKER_API:
                    df = fetch_historical_data(ticker=indicator.ticker, period="5d", interval=indicator.interval)

                confidence = indicator.instance.evaluate(df=df)
                confidences[indicator.ticker][indicator.id] = confidence

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
        fallback_wallet: dict[str, float] = self.paper_wallet.copy()
        fallback_balance: float = self.paper_balance

        for ticker, money_allocation in orders.items():
            ticker_current_price = fetch_info_data(ticker)["currentPrice"]

            if money_allocation < 0:
                num_of_assets: float = self.paper_wallet[ticker]

                self.paper_balance += num_of_assets * ticker_current_price
                self.paper_wallet[ticker] = 0

                logger.info(f"Profile with id {self.id} Sold {num_of_assets} of {ticker} at {ticker_current_price}",
                            extra={"profile_id": self.id, "ticker": ticker})

            elif money_allocation > 0:
                num_of_shares: float = (self.paper_balance * abs(money_allocation)) / ticker_current_price

                self.paper_wallet[ticker] += num_of_shares
                self.paper_balance -= (self.paper_balance * money_allocation)

                logger.info(
                    f"Profile with id {self.id} Bought {num_of_shares} of {ticker} at {ticker_current_price}",
                    extra={"profile_id": self.id, "ticker": ticker})

        if not update_profile(self.id, paper_balance=self.paper_balance, paper_wallet=self.paper_wallet):
            self.paper_wallet = fallback_wallet
            self.paper_balance = fallback_balance
            logger.error(
                f"Failed to update Profile with id: {self.id}; and name: {self.name}; Used Fallback!",
                extra={"profile_id": self.id},
            )

    def update_profile(
            self,
            name: Optional[str] = None,
            balance: Optional[float] = None,
            paper_balance: Optional[float] = None,
            buy_limit: Optional[float] = None,
            sell_limit: Optional[float] = None
    ):
        with self._lock:
            if update_profile(self.id, name=name, balance=balance, paper_balance=paper_balance, buy_limit=buy_limit,
                              sell_limit=sell_limit):
                self.name = name if name is not None else None
                self.balance = balance if balance is not None else None
                self.paper_balance = paper_balance if paper_balance is not None else None
                self.buy_limit = buy_limit if buy_limit is not None else None
                self.sell_limit = sell_limit if sell_limit is not None else None
                logger.info(f"Updated Profile with id: {self.id} to "
                            f"{f"name: {name}" if name is not None else self.name}; "
                            f"{f"balance: {balance}" if balance is not None else self.balance}; "
                            f"{f"paper_balance: {paper_balance}" if paper_balance is not None else self.paper_balance}; "
                            f"{f"buy_limit: {buy_limit}" if buy_limit is not None else self.buy_limit}; "
                            f"{f"sell_limit: {sell_limit}" if sell_limit is not None else self.sell_limit}")
                return True
            else:
                logger.error(f"Failed to update Profile with id: {self.id}; and name: {self.name}")
                return False

    def update_wallet(self, wallet: dict[str, float], is_paper_wallet: bool = False):
        with self._lock:
            if is_paper_wallet:
                execution_status = update_profile(self.id, paper_wallet=wallet)
            else:
                execution_status = update_profile(self.id, wallet=wallet)

            if execution_status:
                if is_paper_wallet:
                    self.paper_wallet = wallet
                else:
                    self.wallet = wallet

                logger.info(
                    f"Updated {"Wallet" if not is_paper_wallet else "Paper Wallet"} for Profile with id: {self.id}; and name: {self.name} to wallet: {self.wallet}"
                )
                return True
            else:
                logger.error(
                    f"Failed to update {"Wallet" if not is_paper_wallet else "Paper Wallet"} for Profile with id: {self.id}; and name: {self.name} to wallet: {self.wallet}",
                )
                return False

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

    def update_indicator(self, id: int, name: str, weight: float, ticker: str, interval: str, settings: dict[str, any]):
        with self._lock:
            if update_indicator(id=id, weight=weight, ticker=ticker, interval=interval, settings=settings):
                self.indicators = [indicator for indicator in self.indicators if indicator.id != id]
                self.indicators.append(
                    IndicatorDTO(
                        id=id,
                        profile_id=self.id,
                        name=name,
                        weight=weight,
                        ticker=ticker,
                        interval=interval,
                        settings=settings
                    )
                )
                logger.info(f"Updated indicator with ID {id} in profile with ID {self.id}.",
                            extra={"profile_id": self.id})
                return True

        logger.error(f"Failed to update indicator with ID {id} in profile with ID {self.id}.",
                     extra={"profile_id": self.id})
        return False

    def remove_indicator(self, indicator_id: int):
        with self._lock:
            if delete_indicator(id=indicator_id):
                self.indicators = [indicator for indicator in self.indicators if indicator.id != indicator_id]

                logger.info(f"Removed indicator with ID {indicator_id} from profile with ID {self.id}.",
                            extra={"profile_id": self.id})
                return True

        logger.error(
            f"Failed to remove indicator with ID {indicator_id} from profile with ID {self.id}.",
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

            self.plugins.append(new_plugin)

            logger.info(f"Added plugin with ID {new_plugin.id} to profile with ID {self.id}.",
                        extra={"profile_id": self.id})
            return True

    def update_plugin(self, id: int, name: str, settings: dict[str, any]):
        with self._lock:
            if update_plugin(id=id, settings=settings):
                self.plugins = [plugin for plugin in self.plugins if plugin.id != id]
                self.plugins.append(PluginDTO(id=id, profile_id=self.id, name=name, settings=settings))
                logger.info(f"Updated plugin with ID {id} in profile with ID {self.id}.",
                            extra={"profile_id": self.id})
                return True

        logger.error(f"Failed to update plugin with ID {id} in profile with ID {self.id}.",
                     extra={"profile_id": self.id})
        return False

    def remove_plugin(self, plugin_id: int):
        with self._lock:
            if delete_plugin(id=plugin_id):
                self.plugins = [plugin for plugin in self.plugins if plugin.id != plugin_id]

                logger.info(f"Removed plugin with ID {plugin_id} from profile with ID {self.id}.",
                            extra={"profile_id": self.id})
                return True

        logger.error(f"Failed to remove plugin with ID {plugin_id} from profile with ID {self.id}.",
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
        indicators: list[IndicatorDTO] | None = self.indicators
        if not indicators:
            logger.info(f"No indicators found for Profile with id: {self.id}", extra={"profile_id": self.id})
            return

        def interval_to_minutes(interval: str) -> int:
            step: int = 1
            match interval[-1]:
                case "m":
                    step = 1
                case "h":
                    step = 60
                case "d":
                    step = 1440
                case "k":
                    step = 10080
                case "o":
                    step = 43200
                case "y":
                    step = 525600

            return int(interval[:-1]) * step

        all_intervals: list[int] = [
            interval_to_minutes(indicator.interval)
            for indicator in indicators
        ]

        smallest_interval: int = min(all_intervals)

        if hasattr(self, 'job') and self.job:
            self.job.remove()

        # TODO: Intervall need start time (example: for 60min/1h round to one hour when starting interval or not?)

        self.job = self.scheduler.add_job(self.evaluate, "interval", minutes=smallest_interval)

        logger.info(
            f"Updated Scheduler to run every {smallest_interval} minutes for Profile with ID {self.id} and name: {self.name}",
            extra={"profile_id": self.id},
        )

    def _check_has_create_order_plugin(self):
        for plugin in self.plugins:
            if plugin.instance.job == PluginJob.CREATE_ORDER:
                return True

        logger.error(
            f"Profile with id {self.id} does not have a create order plugin. Deactivating Profile",
            extra={"profile_id": self.id}, )

        self.change_status(Status.INACTIVE)

        return False

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
