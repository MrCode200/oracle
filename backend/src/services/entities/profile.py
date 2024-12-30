from logging import getLogger
from threading import Lock
from typing import Optional

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.schedulers.background import BackgroundScheduler

from src.database import get_plugin

from src.api import fetch_historical_data
from src.api import fetch_info_data
from src.database import (TradingComponentDTO, PluginDTO, ProfileDTO, get_trading_component,
                          update_profile, delete_plugin, update_trading_component,
                          create_plugin, create_trading_component, update_plugin, delete_trading_component)

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

        # REMAKE: dict[id, TradingComponentDTO] and also for plugin
        self.trading_components: list[TradingComponentDTO] = get_trading_component(profile_id=profile.id)
        self.plugins: list[PluginDTO] = get_plugin(profile_id=profile.id)
        self.buy_limit: float = profile.buy_limit
        self.sell_limit: float = profile.sell_limit

        profile_registry.register([self.id], self)

        self._lock = Lock()

        self.scheduler = BackgroundScheduler()
        self.scheduler_is_paused: bool = True
        self._setup_schedular()

        logger.debug(
            f"Initialized Profile with ID {self.id} and name: {self.name}",
            extra={"profile_id": self.id},
        )

    def change_status(self, status: Status, run_on_start: bool = False):
        with self._lock:
            if status == Status.INACTIVE or status.value >= Status.UNKNOWN_ERROR.value:
                if not self.scheduler_is_paused:
                    self.scheduler.pause()
                    self.scheduler_is_paused = True

            else:
                if not self._check_status_valid():
                    return

                if run_on_start:
                    self.evaluate()

                if self.scheduler_is_paused:
                    self.scheduler.resume()

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
                    plugin.instance.run(profile=self)

            for trading_component in self.trading_components:
                if trading_component.weight == 0:
                    continue

                if not BROKER_API:
                    # PERIOD is ignored when using api_name
                    df = fetch_historical_data(ticker=trading_component.ticker, period="5d", interval=trading_component.interval, api_name="nobitex")

                confidence = trading_component.instance.evaluate(df=df)
                confidences[trading_component.ticker][trading_component.id] = confidence * trading_component.weight

            for plugin in self.plugins:
                if plugin.instance.job == PluginJob.AFTER_EVALUATION:
                    confidences = plugin.instance.run(profile=self, tc_confidences=confidences)

            for plugin in self.plugins:
                if plugin.instance.job == PluginJob.CREATE_ORDER:
                    order: dict[str, float] = plugin.instance.run(profile=self, tc_confidences=confidences)
                    break

            logger.info(
                f"Evaluation Finished for Profile with ID {self.id} and name: {self.name}; "
                f"Confidence: {confidences}; "
                f"Order: {order}",
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
            self._live_trade_agent(orders)

    def _paper_trade_agent(self, orders: dict[str, float]):
        # Fallback in case of db doesn't update
        fallback_wallet: dict[str, float] = self.paper_wallet.copy()
        fallback_balance: float = self.paper_balance

        for ticker, percentage_change in orders.items():
            if percentage_change == 0:
                continue

            ticker_current_price = fetch_historical_data(ticker, period="1d", interval="1m").iloc[-1]["Close"]

            if percentage_change < 0 < self.paper_wallet[ticker]:
                num_of_assets: float = self.paper_wallet[ticker]
                num_of_assets_to_sell: float = num_of_assets * percentage_change

                self.paper_balance += num_of_assets_to_sell * ticker_current_price
                self.paper_wallet[ticker] = num_of_assets - num_of_assets_to_sell

                logger.info(
                    f"Profile with id {self.id} Sold {num_of_assets_to_sell} of {ticker} at {ticker_current_price}",
                    extra={"profile_id": self.id, "ticker": ticker})

            elif percentage_change > 0 < self.paper_balance:
                dedicated_balance: float = self.paper_balance * percentage_change
                num_of_assets_to_buy: float = dedicated_balance / ticker_current_price

                self.paper_wallet[ticker] += num_of_assets_to_buy
                self.paper_balance -= dedicated_balance

                logger.info(
                    f"Profile with id {self.id} Bought {num_of_assets_to_buy} of {ticker} at {ticker_current_price}",
                    extra={"profile_id": self.id, "ticker": ticker})


        if fallback_balance == self.paper_balance and fallback_wallet == self.paper_wallet:
            return

        if not update_profile(self.id, paper_balance=self.paper_balance, paper_wallet=self.paper_wallet):
            self.paper_wallet = fallback_wallet
            self.paper_balance = fallback_balance
            logger.error(
                f"Failed to update Profile with id: {self.id}; and name: {self.name}; Used Fallback!",
                extra={"profile_id": self.id},
            )

    def _live_trade_agent(self, orders: dict[str, float]):
        pass
        ...  # KIAN HERE

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

    def add_trading_component(self, trading_component: 'Basetrading_component', weight: float, ticker: str, interval: str):
        with self._lock:
            new_trading_component: TradingComponentDTO = create_trading_component(
                profile_id=self.id,
                name=trading_component.__class__.__name__,
                weight=weight,
                ticker=ticker,
                interval=interval,
                settings=trading_component.__dict__,
            )
            if new_trading_component is not None:
                self.trading_components.append(new_trading_component)
                logger.info(f"Added trading_component with ID {new_trading_component.id} to profile with ID {self.id}.",
                            extra={"profile_id": self.id})
                self._update_scheduler()

                return True

        logger.error(f"Failed to add trading_component to profile with ID {self.id}.",
                     extra={"profile_id": self.id})
        return False

    def update_trading_component(self, trading_component_id: int, name: str, weight: float, ticker: str, interval: str, settings: dict[str, any]):
        with self._lock:
            if update_trading_component(trading_component_id=trading_component_id, weight=weight, ticker=ticker, interval=interval, settings=settings):
                self.trading_components = [trading_component for trading_component in self.trading_components if trading_component.id != trading_component_id]
                self.trading_components.append(
                    TradingComponentDTO(
                        id=trading_component_id,
                        profile_id=self.id,
                        name=name,
                        weight=weight,
                        ticker=ticker,
                        interval=interval,
                        settings=settings
                    )
                )
                logger.info(f"Updated trading_component with ID {trading_component_id} in profile with ID {self.id}.",
                            extra={"profile_id": self.id})
                return True

        logger.error(f"Failed to update trading_component with ID {trading_component_id} in profile with ID {self.id}.",
                     extra={"profile_id": self.id})
        return False

    def remove_trading_component(self, trading_component_id: int):
        with self._lock:
            if delete_trading_component(trading_component_id=trading_component_id):
                self.trading_components = [trading_component for trading_component in self.trading_components if trading_component.id != trading_component_id]

                logger.info(f"Removed trading_component with ID {trading_component_id} from profile with ID {self.id}.",
                            extra={"profile_id": self.id})
                return True

        logger.error(
            f"Failed to remove trading_component with ID {trading_component_id} from profile with ID {self.id}.",
            extra={"profile_id": self.id})
        return False

    def add_plugin(self, plugin: 'BasePlugin'):
        with self._lock:
            new_plugin: PluginDTO = create_plugin(
                profile_id=self.id,
                name=plugin.__class__.__name__,
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

        self.scheduler.add_job(self.evaluate, "interval", seconds=20)
        self.scheduler.start()
        self.scheduler.pause()
        self.scheduler_is_paused = True

        logger.info(f"Scheduler initialized for Profile with id: {self.id}", extra={"profile_id": self.id})

    def _update_scheduler(self):
        trading_components: list[TradingComponentDTO] | None = self.trading_components
        if not trading_components:
            logger.info(f"No trading_components found for Profile with id: {self.id}", extra={"profile_id": self.id})
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
            interval_to_minutes(trading_component.interval)
            for trading_component in trading_components
        ]

        smallest_interval: int = min(all_intervals)

        self.scheduler.remove_all_jobs()
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
