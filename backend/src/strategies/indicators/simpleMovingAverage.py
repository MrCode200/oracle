import logging
from math import ceil

import pandas
from pandas import DataFrame
from pandas_ta import sma

from .indicatorBase import Indicator  # type: ignore

logger: logging.Logger = logging.getLogger("oracle.app")

class SimpleMovingAverage(Indicator):
    """
    Implements the Simple Moving Average (SMA) trading strategy.

    The Simple Moving Average (SMA) is a trend-following indicator that calculates the average of a
    selected range of prices over a set period of time. In this strategy, the crossover of short-term
    and long-term SMAs is used to generate trade signals:
    - A Buy signal is generated when the short-term SMA crosses above the long-term SMA.
    - A Sell signal is generated when the short-term SMA crosses below the long-term SMA.
    - A Hold signal is returned when there is no crossover.

    The strategy aims to capture price trends by entering long (buy) when upward momentum is detected
    and exiting (sell) when momentum weakens.

    Methods
    -------
    determine_trade_signal(short_sma_latest: float, short_sma_previous: float, long_sma_latest: float, long_sma_previous: float)
        Determines the trade signal based on the crossover of short and long SMAs.

    evaluate(data_frame: DataFrame, short_period: int = 14, long_period: int = 50) -> int | None
        Evaluates the current SMA crossover and returns a trade signal.

    backtest(data_frame: DataFrame, short_period: int = 14, long_period: int = 50) -> float
        Backtests the strategy using historical data and calculates the Return on Investment (ROI).
    """
    _EA_SETTINGS: dict[str, dict[str, int|float]] = {
        "short_period": {"start": 1, "stop": 200, "step": 1},
        "long_period": {"start": 1, "stop": 200, "step": 1},
    }


    @staticmethod
    def determine_trade_signal(
            short_sma_latest: float,
            short_sma_previous: float,
            long_sma_latest: float,
            long_sma_previous: float
    ) -> int | None:
        """
        Determines trade signal based on SMA crossovers.

        The function compares the latest and previous values of the short and long SMAs.
        - If the crossovers haven't occurred, returns None (Hold).
        - If the short SMA crosses above the long SMA, returns 1 (Buy).
        - If the short SMA crosses below the long SMA, returns 0 (Sell).

        :param short_sma_latest: The most recent value of the short period SMA.
        :param short_sma_previous: The previous value of the short period SMA.
        :param long_sma_latest: The most recent value of the long period SMA.
        :param long_sma_previous: The previous value of the long period SMA.

        :return: 1 if Buy signal, 0 if Sell signal, or None if Hold signal.
        """
        if (short_sma_latest > long_sma_latest) == (short_sma_previous > long_sma_previous):
            return None  # Hold
        elif short_sma_latest > long_sma_latest:
            return 1  # Buy
        else:
            return 0  # Sell

    @staticmethod
    def evaluate(data_frame: DataFrame, short_period: int = 14, long_period: int = 50) -> int | None:
        """
        Evaluates the latest SMA cross and logs the decision.

        This method calculates the short and long period SMAs for the provided data.
        It then determines the trade signal based on the crossover of the SMAs and returns the decision.

        :param data_frame: The DataFrame containing the market data with a 'Close' column.
        :param short_period: The period for the short-term SMA (default is 14).
        :param long_period: The period for the long-term SMA (default is 50).

        :return: The trade signal (1 for Buy, 0 for Sell, or None for Hold).
        """
        short_sma_series: pandas.Series = sma(close=data_frame.Close, length=short_period)
        long_sma_series: pandas.Series = sma(close=data_frame.Close, length=long_period)

        short_sma_latest: float = short_sma_series.iloc[-1]
        long_sma_latest: float = long_sma_series.iloc[-1]
        short_sma_previous: float = short_sma_series.iloc[-2]
        long_sma_previous: float = long_sma_series.iloc[-2]

        logger.debug(f"Latest short SMA: {short_sma_latest}, Latest long SMA: {long_sma_latest}",
                     extra={"strategy": "SMA"})
        logger.debug(f"Previous short SMA: {short_sma_previous}, Previous long SMA: {long_sma_previous}",
                     extra={"strategy": "SMA"})

        # Determine trade signal
        signal: int | None = SimpleMovingAverage.determine_trade_signal(short_sma_latest, short_sma_previous, long_sma_latest,
                                                                  long_sma_previous)

        decision: str = "hold" if signal is None else "buy" if signal == 1 else "sell"
        logger.info(f"SMA evaluation result: {decision}", extra={"strategy": "SMA"})
        return signal

    @staticmethod
    def backtest(data_frame: DataFrame, parition_amount: int = 1, short_period: int = 14, long_period: int = 50) -> list[float]:
        """
        Runs a backtest on the data and returns final profit or loss.

        This method simulates a trading strategy using the SMA crossover approach.
        It buys when the short SMA crosses above the long SMA, and sells when the short SMA crosses below the long SMA.
        The initial balance is assumed to be 100,000, and the strategy is tested over the provided market data.

        :param data_frame: The DataFrame containing the market data with a 'Close' column.
        :key parition_amount: The amount of paritions which get returned at which to recalculate the Return on Investiment (default is 1).
        :key short_period: The period for the short-term SMA (default is 14).
        :key long_period: The period for the long-term SMA (default is 50).

        :return: A list of parition_amount times of the Return on Investiment.

        :raises ValueError: If parition_amount is less than or equal to 0
        """
        if parition_amount <= 0:
            raise ValueError("Parition amount must be greater than 0")

        base_balance: float = 1_000_000
        balance: float = base_balance
        shares: float = 0
        net_worth_history: list[float] = []

        nan_padding = 1 + long_period

        short_sma_series: pandas.Series = sma(close=data_frame.Close, length=short_period)
        long_sma_series: pandas.Series = sma(close=data_frame.Close, length=long_period)

        parition_amount = ceil((len(long_sma_series) - nan_padding) / parition_amount) if parition_amount > 1 else 1

        for i in range(nan_padding, len(long_sma_series)):
            short_sma_latest: float = short_sma_series.iloc[i]
            long_sma_latest: float = long_sma_series.iloc[i]
            short_sma_previous: float = short_sma_series.iloc[i - 1]
            long_sma_previous: float = long_sma_series.iloc[i - 1]

            trade_signal: int | None = SimpleMovingAverage.determine_trade_signal(
                short_sma_latest, short_sma_previous, long_sma_latest, long_sma_previous
            )

            is_partition_cap_reached: bool = ((i - nan_padding + 1) % parition_amount == 0) if parition_amount > 1 else False

            base_balance, balance, shares = SimpleMovingAverage.process_trade_signal(
                base_balance, balance, shares,
                data_frame.iloc[i].Close, trade_signal,
                net_worth_history, is_partition_cap_reached,
                "SMA"
            )

        if not is_partition_cap_reached:
            total_net_worth = balance + shares * data_frame.iloc[-1].Close
            net_worth_history.append(total_net_worth / base_balance)

        logger.info(f"Backtest completed with Return on Investment of {[str(roi * 100) for roi in net_worth_history]}",
                    extra={"strategy": "SMA"})

        return net_worth_history


