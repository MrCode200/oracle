from typing import Optional

from src.api import fetch_ticker_price
from src.constants import Status

from logging import getLogger
logger = getLogger("oracle.app")

class TradeAgent:
    def __init__(self, profile):
        self.profile: 'Profile' = profile

    def trade(self, orders: dict[str, float], bt_wallet: Optional[dict[str, float]] = None, bt_balance: Optional[float] = None):
        """
        Runs the trade agent function based on the profile status
        :param orders: The orders in the format of {ticker: percentage_change}
        :param bt_wallet: The backtest wallet
        :param bt_balance: The backtest balance
        :return: (If status == BACKTESTING) The updated backtest wallet and balance
        """
        if self.profile.status == Status.ACTIVE:
            self._live_trade_agent(orders)
        elif self.profile.status == Status.PAPER_TRADING:
            self._paper_trade_agent(orders)
        elif self.profile.status == Status.BACKTESTING:
            return self._backtest_trade_agent(orders, bt_wallet, bt_balance)


    def _paper_trade_agent(self, orders: dict[str, float]):
        # Fallback in case of db doesn't update
        fallback_wallet: dict[str, float] = self.profile.paper_wallet.copy()
        fallback_balance: float = self.profile.paper_balance

        for ticker, percentage_change in orders.items():
            if percentage_change == 0:
                continue

            ticker_current_price: float = fetch_ticker_price(ticker)

            if percentage_change < 0 < self.profile.paper_wallet[ticker]:
                num_of_assets: float = self.profile.paper_wallet[ticker]
                num_of_assets_to_sell: float = num_of_assets * percentage_change

                self.profile.paper_balance += num_of_assets_to_sell * ticker_current_price
                self.profile.paper_wallet[ticker] = num_of_assets - num_of_assets_to_sell

                logger.info(
                    f"Profile with id {self.profile.id} Sold {num_of_assets_to_sell} of {ticker} at {ticker_current_price}",
                    extra={"profile_id": self.profile.id, "ticker": ticker})

            elif percentage_change > 0 < self.profile.paper_balance:
                dedicated_balance: float = self.profile.paper_balance * percentage_change
                num_of_assets_to_buy: float = dedicated_balance / ticker_current_price

                self.profile.paper_wallet[ticker] += num_of_assets_to_buy
                self.profile.paper_balance -= dedicated_balance

                logger.info(
                    f"Profile with id {self.profile.id} Bought {num_of_assets_to_buy} of {ticker} at {ticker_current_price}",
                    extra={"profile_id": self.profile.id, "ticker": ticker})


        if fallback_balance == self.profile.paper_balance and fallback_wallet == self.profile.paper_wallet:
            return

        if not self.profile.update(paper_balance=self.profile.paper_balance, paper_wallet=self.profile.paper_wallet):
            self.profile.paper_wallet = fallback_wallet
            self.profile.paper_balance = fallback_balance
            logger.error(
                f"Failed to update Profile with id: {self.profile.id}; and name: {self.profile.name}; Used Fallback!",
                extra={"profile_id": self.profile.id},
            )

    # TODO: Add backtesting trade agent
    @staticmethod
    def _backtest_trade_agent(orders: dict[str, float], wallet: dict[str, float], balance: float) -> tuple[dict[str, float], float]:
        return wallet, balance

    def _live_trade_agent(self, orders: dict[str, float]):
        ...