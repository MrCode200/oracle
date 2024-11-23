import logging
from abc import ABC, abstractmethod
from math import ceil

from pandas import DataFrame, isna
import pandas_ta as ta

logger = logging.getLogger("oracle.app")


class BaseIndicator(ABC):
    """
    Defines an abstract base class for indicators.

    Methods
        - classmethod EA_RANGE(cls) -> tuple[int, int]: Returns the range of the indicator.
        - evaluate() -> float: Abstract method to run the algorithms on the provided database.
        - backtest() -> float: Abstract method to test the accuracy of the algorithms on the provided database.
        - process_trade_signal() -> float: Abstract method to buy and sell as well as append for all backtest functions.

    :raises Attribute Error: If the subclass does not define _EA_SETTINGS and _EA_SETTINGS does not contain 'start', 'stop', 'step' and 'type'.
    """

    @classmethod
    def __init_subclass__(cls, **kwargs):
        required_keys: set = {"start", "stop", "step", "type"}
        for key, setting in cls._EA_SETTINGS.items():
            if not required_keys <= set(setting.keys()):  # Checks if all required keys are present
                raise AttributeError(
                    f"_EA_SETTINGS: dict must contain dictionaries with the keys 'start', 'stop', and 'step'. Argument missing those keys: {key}")

    @classmethod
    def EA_SETTINGS(cls) -> dict[str, dict[str, int | float]]:
        return cls._EA_SETTINGS

    @abstractmethod
    def evaluate(df: DataFrame) -> float:
        ...

    @abstractmethod
    def backtest(self, df: DataFrame, func_kwargs: dict[str, any], invalid_values: int, partition_amount: int,
                 sell_threshold: float, buy_threshold: float, indicator_name: str) -> list[float]:
        """
        Conducts a backtest on the provided market data to evaluate the performance of a trading strategy.

        NOTE:
            - It may not work if the df is not the length of the indicator series!

        :param df: The DataFrame containing the market data with a 'Close' column.
        :param func_kwargs: A dictionary of keyword arguments to be passed to the `determine_trade_signal` method.
        :param invalid_values: The number of initial rows in the DataFrame to skip, typically used to account for NaN values.
        :param partition_amount: The number of partitions to divide the data into for recalculating the Return on Investment (ROI). Must be greater than 0.
        :param indicator_name: The name of the strategy being tested, only needed for logging.
        :param sell_threshold: The percentage of when to sell, (default is 0.2).
        :param buy_threshold: The percentage of when to buy, (default is 0.8).

        :returns: A list of floats representing the ROI for each partition.

        :raises ValueError: If `partition_amount` is less than or equal to 0.
        """
        if partition_amount <= 0:
            raise ValueError("Partition amount must be greater than 0")

        base_balance: float = 1_000_000
        balance: float = base_balance
        shares: float = 0
        net_worth_history: list[float] = []

        partition_amount: int = ceil((len(df) - invalid_values) / partition_amount) if partition_amount > 1 else 1

        for i in range(invalid_values, len(df)):
            trade_signal: float = self.determine_trade_signal(index=i, **func_kwargs)

            is_partition_cap_reached: bool = (
                    (i - invalid_values + 1) % partition_amount == 0) if partition_amount > 1 else False

            base_balance, balance, shares = BaseIndicator.process_trade_signal(
                base_balance, balance, shares,
                df.iloc[i].Close, df.index[i] ,trade_signal,
                buy_threshold, sell_threshold,
                net_worth_history, is_partition_cap_reached,
                indicator_name
            )

        if not is_partition_cap_reached:
            total_net_worth = balance + shares * df.iloc[-1].Close
            net_worth_history.append(total_net_worth / base_balance)

        logger.info(f"Backtest completed with Return on Investment of {[str(roi * 100) for roi in net_worth_history]}",
                    extra={"indicator": indicator_name})

        return net_worth_history

    @abstractmethod
    def determine_trade_signal(self, df: DataFrame, index: int = 0) -> float:
        ...

    @staticmethod
    def process_trade_signal(
            base_balance: float,
            balance: float,
            shares: float,
            latest_price: float,
            date: str,
            trade_signal: float,
            buy_threshold: float,
            sell_threshold: float,
            net_worth_history: list[float],
            is_partition_cap_reached: bool,
            indicator_name: str
    ) -> tuple[float, float, float]:
        """
        Applies a trade signal to update the portfolio's cash balance, owned shares, and records the ROI.

        This method processes the buy or sell signal based on the current portfolio state, executing a trade
        if the signal and conditions allow. It updates the cash balance, owned shares, and records the portfolio
        value at regular intervals (as specified by the `should_record_roi` flag).

        :param base_balance: The initial cash balance used for ROI calculations.
        :param balance: The current cash balance available for trading.
        :param shares: The number of shares currently owned in the portfolio.
        :param latest_price: The latest market price of the asset being traded.
        :param date: The date of the current market data point.
        :param trade_signal: The trade signal, where 1 represents a buy signal and 0 represents a sell signal.
        :param sell_threshold: The percentage of when to sell, (default is 0.2).
        :param buy_threshold: The percentage of when to buy, (default is 0.8).
        :param net_worth_history: A list storing the historical values of the portfolio for ROI tracking.
        :param is_partition_cap_reached: A flag indicating whether the ROI should be recorded for the current period.
        :param indicator_name: The name of the strategy used for logging purposes.

        :return: A tuple containing:
            - updated `original_balance` (float): The updated balance after executing the trade.
            - updated `cash_balance` (float): The updated cash balance after the trade.
            - updated `owned_shares` (float): The updated number of owned shares after the trade.

        :note:
            - A buy signal (1) will convert available cash into shares, and the cash balance will become 0.
            - A sell signal (-1) will sell all owned shares for cash, and the shares will be reset to 0.
            - If `should_record_roi` is True, the method will record the portfolio's total value at that point,
              updating the `portfolio_value_history` with the current ROI.
        """
        if trade_signal >= buy_threshold and balance != 0:
            shares = balance / latest_price
            balance = 0
            logger.debug(
                "Executed Buy on signal `{}` and shares `{}` with a price of `{}`; date: `{}`".format(trade_signal, shares, latest_price, date),
                extra={"strategy": indicator_name})

        elif trade_signal <= sell_threshold and shares > 0:  # Sell
            logger.debug(
                "Executed Sell on signal `{}` and shares `{}` with a price of `{}`; date: `{}`".format(trade_signal, shares, latest_price, date),
                extra={"strategy": indicator_name})
            balance += shares * latest_price
            shares = 0

        if is_partition_cap_reached:
            total_net_worth: float = balance + shares * latest_price

            net_worth_history.append(total_net_worth / base_balance)
            base_balance = total_net_worth

            logger.debug(
                f"Appended ROI, Total Net Worth:{total_net_worth}; ROI: {net_worth_history[-1]}",
                extra={"strategy": indicator_name})

        return base_balance, balance, shares


if __name__ == '__main__':
    print(help(ta.Strategy))
