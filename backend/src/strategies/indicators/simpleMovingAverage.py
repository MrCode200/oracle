import logging
from math import ceil

import pandas
from pandas import DataFrame
from pandas_ta import sma

from .BaseIndicator import BaseIndicator  # type: ignore

logger: logging.Logger = logging.getLogger("oracle.app")


class SimpleMovingAverage(BaseIndicator):
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

    evaluate(df: DataFrame, short_period: int = 14, long_period: int = 50) -> int | None
        Evaluates the current SMA crossover and returns a trade signal.

    backtest(df: DataFrame, short_period: int = 14, long_period: int = 50) -> float
        Backtests the strategy using historical data and calculates the Return on Investment (ROI).
    """
    _EA_SETTINGS: dict[str, dict[str, int | float]] = {
        "short_period": {"start": 10, "stop": 100, "step": 1, "type": "int"},
        "long_period": {"start": 50, "stop": 200, "step": 1, "type": "int"},
    }

    @staticmethod
    def determine_trade_signal(short_sma_series: pandas.Series, long_sma_series: pandas.Series, index: int = 0) -> int:
        """
        Determines trade signal based on SMA crossovers.

        The function compares the latest and previous values of the short and long SMAs.
        - If the crossovers haven't occurred, returns 0 (Hold).
        - If the short SMA crosses above the long SMA, returns 1 (Buy).
        - If the short SMA crosses below the long SMA, returns -1 (Sell).

        :param short_sma_series: A series of short a period SMA.
        :param long_sma_series: A series of a long period SMA.
        :key index: The index of the data to evaluate (default is 0).

        :return: 1 if Buy signal, -1 if Sell signal, or 0 if Hold signal.

        :raise ValueError: If the index is greater than the length of the series. Due to it getting index-1 value of the series
        """
        if index == len(short_sma_series) - 1:
            raise ValueError("Index must be smaller than the length of the series.")

        short_sma_latest: float = short_sma_series.iloc[index]
        long_sma_latest: float = long_sma_series.iloc[index]
        short_sma_previous: float = short_sma_series.iloc[index - 1]
        long_sma_previous: float = long_sma_series.iloc[index - 1]

        if (short_sma_latest > long_sma_latest) == (short_sma_previous > long_sma_previous):
            return 0  # Hold
        elif short_sma_latest > long_sma_latest:
            return 1  # Buy
        else:
            return -1  # Sell

    @staticmethod
    def evaluate(df: DataFrame, short_period: int = 14, long_period: int = 50) -> int | None:
        """
        Evaluates the latest SMA cross and logs the decision.

        This method calculates the short and long period SMAs for the provided data.
        It then determines the trade signal based on the crossover of the SMAs and returns the decision.

        :param df: The DataFrame containing the market data with a 'Close' column.
        :param short_period: The period for the short-term SMA (default is 14).
        :param long_period: The period for the long-term SMA (default is 50).

        :return: The trade signal (1 for Buy, -1 for Sell, or 0 for Hold).
        """
        short_sma_series: pandas.Series = sma(close=df.Close, length=short_period)
        long_sma_series: pandas.Series = sma(close=df.Close, length=long_period)

        # Determine trade signal
        signal: int | None = SimpleMovingAverage.determine_trade_signal(
            short_sma_series=short_sma_series,
            long_sma_series=long_sma_series
        )

        decision: str = "hold" if signal is 0 else "buy" if signal == 1 else "sell"
        logger.info(f"SMA evaluation result: {decision}", extra={"strategy": "SMA"})
        return signal

    @staticmethod
    def backtest(df: DataFrame, partition_amount: int = 1, short_period: int = 14, long_period: int = 50) -> \
    list[float]:
        """
        Runs a backtest on the data and returns final profit or loss.

        This method simulates a trading strategy using the SMA crossover approach.
        It buys when the short SMA crosses above the long SMA, and sells when the short SMA crosses below the long SMA.
        The initial balance is assumed to be 100,000, and the strategy is tested over the provided market data.

        :param df: The DataFrame containing the market data with a 'Close' column.
        :key partition_amount: The amount of paritions which get returned at which to recalculate the Return on Investiment (default is 1).
        :key short_period: The period for the short-term SMA (default is 14).
        :key long_period: The period for the long-term SMA (default is 50).

        :return: A list of partition_amount times of the Return on Investment.

        :raises ValueError: If partition_amount is less than or equal to 0
        """
        nan_padding = 1 + long_period

        short_sma_series: pandas.Series = sma(close=df.Close, length=short_period)
        long_sma_series: pandas.Series = sma(close=df.Close, length=long_period)

        signal_func_kwargs = {
            'short_period': short_sma_series,
            'long_period': long_sma_series
        }

        return super().backtest(df=df, invalid_values=nan_padding, func_kwargs=signal_func_kwargs,
                                partition_amount=partition_amount)
