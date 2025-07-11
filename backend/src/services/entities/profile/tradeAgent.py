from typing import Optional

from src.api import fetch_ticker_price
from src.constants import Status

from logging import getLogger
logger = getLogger("oracle.app")

class TradeAgent:
    def __init__(self, profile):
        self.profile: 'Profile' = profile

    def trade(self, orders: dict[str, float]):
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


    def process_order(
            self,
            orders: dict[str, float],
            wallet: dict[str, float],
            balance: float,
            prices: Optional[dict[str, float]] = None
    ) -> tuple[dict[str, float], float]:
        """
        Processes the order

        :param orders: The orders in the format of {ticker: percentage_change}
        :param wallet: The wallet to be updated
        :param balance: The available balance to be updated
        :param prices: Custom prices in the format of {ticker: price}

        :return: Updated wallet and balance
        """
        if prices is None:
            prices = {}

        for ticker, percentage_change in orders.items():
            if percentage_change == 0:
                continue

            # Is only used for backtesting
            if ticker in prices.keys():
                ticker_current_price: float = prices[ticker]
            else:
                ticker_current_price: float = fetch_ticker_price(ticker)

            if percentage_change < 0 < wallet[ticker]:
                num_of_assets: float = wallet[ticker]
                num_of_assets_to_sell: float = num_of_assets * abs(percentage_change)

                balance += num_of_assets_to_sell * ticker_current_price
                wallet[ticker] = num_of_assets - num_of_assets_to_sell

                logger.info(
                    f"Profile with id {self.profile.id} Sold {num_of_assets_to_sell} of {ticker} at {ticker_current_price}",
                    extra={"profile_id": self.profile.id, "ticker": ticker})

            elif percentage_change > 0 and 0 < balance:
                dedicated_balance: float = balance * percentage_change
                num_of_assets_to_buy: float = dedicated_balance / ticker_current_price

                wallet[ticker] += num_of_assets_to_buy
                balance -= dedicated_balance

                logger.info(
                    f"Profile with id {self.profile.id} Bought {num_of_assets_to_buy} of {ticker} at {ticker_current_price}",
                    extra={"profile_id": self.profile.id, "ticker": ticker})

        return wallet, balance


    def _paper_trade_agent(self, orders: dict[str, float]):
        # Fallback in case of db doesn't update
        fallback_wallet: dict[str, float] = self.profile.paper_wallet.copy()
        fallback_balance: float = self.profile.paper_balance

        self.profile.paper_wallet, self.profile.paper_balance = self.process_order(
            orders,
            self.profile.paper_wallet,
            self.profile.paper_balance
        )

        if fallback_balance == self.profile.paper_balance and fallback_wallet == self.profile.paper_wallet:
            return

        if not self.profile.update(paper_balance=self.profile.paper_balance, paper_wallet=self.profile.paper_wallet):
            self.profile.paper_wallet = fallback_wallet
            self.profile.paper_balance = fallback_balance
            logger.error(
                f"Failed to update Profile with id: {self.profile.id}; and name: {self.profile.name}; Used Fallback!",
                extra={"profile_id": self.profile.id},
            )


    def _live_trade_agent(self, orders: dict[str, float]):
        ...