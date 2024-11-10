import logging
from abc import ABC, abstractmethod
from math import ceil

from pandas import DataFrame, isna
import pandas_ta as ta

logger = logging.getLogger("oracle.app")

class Indicator(ABC):
    """
    Defines an abstract base class for indicators.

    Methods
        - classmethod EA_RANGE(cls) -> tuple[int, int]: Returns the range of the indicator.
        - evaluate(database: Iterable) -> float: Abstract method to run the strategies on the provided database.
        - backtest(database: Iterable) -> float: Abstract method to test the accuracy of the strategies on the provided database.
        - process_trade_signal(database: Iterable) -> float: Abstract method to buy and sell as well as append for all backtest functions.
    """
    @classmethod
    def __init_subclass__(cls, **kwargs):
        if (
            not hasattr(cls, "_EA_SETTINGS") and
            type(cls._EA_SETTINGS) != type(dict) and
            cls._EA_SETTINGS.keys() != {"start", "end", "step"}
        ):
            raise ValueError(f"Subclass {cls.__name__} must define _EA_SETTINGS as a dictionary with keys 'start', 'end', and 'step'")

    @classmethod
    def _EA_SETTINGS(cls) -> tuple[int, int]:
        return cls._EA_SETTINGS

    @staticmethod
    @abstractmethod
    def determine_trade_signal():
        ...

    @staticmethod
    @abstractmethod
    def evaluate(data_frame: DataFrame) -> float | int | None:
        ...

    @staticmethod
    @abstractmethod
    def backtest(data_frame: DataFrame, parition_amount: int = 1) -> list[float]:
        """

        :param data_frame: The DataFrame containing the market data with a 'Close' column.
        :key parition_amount: The amount of paritions which get returned at which to recalculate the Return on Investiment (default is 12).
        :return: A list of parition_amount times of the Return on Investiment.
        :raises ValueError: If parition_amount is less than or equal to 0
        """
        if parition_amount <= 0:
            raise ValueError("Parition amount must be greater than 0")

        base_balance: float = 1_000_000
        balance: float = base_balance
        shares: float = 0
        net_worth_history: list[float] = []

        nan_padding = ...

        indicator_series = ... # Evaluate the indicator

        parition_amount = ceil((len(indicator_series) - nan_padding) / parition_amount) if parition_amount > 1 else 1

        for i in range(nan_padding, len(indicator_series)):
            if isna(data_frame.iloc[i]['Close']):
                continue
                # !!!
                # should be removed and set to the value where no NaN is present based on the period

            trade_signal: int | None = ...

            is_partition_cap_reached: bool = ((i - nan_padding + 1) % parition_amount == 0) if parition_amount > 1 else False

            base_balance, balance, shares = Indicator.process_trade_signal(
                base_balance, balance, shares,
                data_frame.iloc[i].Close, trade_signal,
                net_worth_history, is_partition_cap_reached,
                "BaseClass"
            )


        if not is_partition_cap_reached:
            total_net_worth = balance + shares * data_frame.iloc[-1].Close
            net_worth_history.append(total_net_worth / base_balance)

        logger.info(f"Backtest completed with Return on Investment of {[str(roi * 100) for roi in net_worth_history]}",
                    extra={"strategy": "BaseClass"})

        return net_worth_history

    @staticmethod
    def process_trade_signal(
            base_balance: float,
            balance: float,
            shares: float,
            latest_price: float,
            trade_signal: int,
            net_worth_history: list[float],
            is_partition_cap_reached: bool,
            strategy_name: str
    ) -> tuple[float, float, float]:
        """
        Applies a trade signal to update the portfolio's cash balance, owned shares, and records the ROI.

        This method processes the buy or sell signal based on the current portfolio state, executing a trade
        if the signal and conditions allow. It updates the cash balance, owned shares, and records the portfolio
        value at regular intervals (as specified by the `should_record_roi` flag).

        :param original_balance: The initial cash balance used for ROI calculations.
        :param balance: The current cash balance available for trading.
        :param owned_shares: The number of shares currently owned in the portfolio.
        :param latest_price: The latest market price of the asset being traded.
        :param trade_signal: The trade signal, where 1 represents a buy signal and 0 represents a sell signal.
        :param portfolio_value_history: A list storing the historical values of the portfolio for ROI tracking.
        :param should_record_roi: A flag indicating whether the ROI should be recorded for the current period.
        :param strategy_name: The name of the strategy used for logging purposes.

        :return: A tuple containing:
            - updated `original_balance` (float): The updated balance after executing the trade.
            - updated `cash_balance` (float): The updated cash balance after the trade.
            - updated `owned_shares` (float): The updated number of owned shares after the trade.

        :note:
            - A buy signal (1) will convert available cash into shares, and the cash balance will become 0.
            - A sell signal (0) will sell all owned shares for cash, and the shares will be reset to 0.
            - If `should_record_roi` is True, the method will record the portfolio's total value at that point,
              updating the `portfolio_value_history` with the current ROI.
        """
        if trade_signal == 1 and balance >= latest_price:
            shares = balance / latest_price
            balance = 0
            logger.debug(
                "Executed Buy of {} shares at date: {}".format(shares, latest_price),
                extra={"strategy": strategy_name})

        elif trade_signal == 0 and shares > 0:  # Sell
            logger.debug(
                "Executed Sell of {} shares at date: {}".format(shares, latest_price),
                extra={"strategy": strategy_name})
            balance += shares * latest_price
            shares = 0

        if is_partition_cap_reached:
            total_net_worth: float = balance + shares * latest_price

            net_worth_history.append(total_net_worth / base_balance)
            base_balance = total_net_worth

            logger.debug(
                f"Appended ROI, Total Net Worth:{total_net_worth}; ROI: {net_worth_history[-1]}",
                extra={"strategy": strategy_name})

        return base_balance, balance, shares

if __name__ == '__main__':
    print(help(ta.Strategy))