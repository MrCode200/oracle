import logging
from subprocess import check_output
from typing import Iterable

from pandas import DataFrame, Series
from pandas import isna

import pandas_ta as ta

from .indicatorBase import Indicator  # type: ignore

logger = logging.getLogger("oracle.app")

class SimpleMovingAverage(Indicator):
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
        # Calculate SMAs
        short_sma_series = data_frame.ta.sma(close=data_frame['Close'], length=short_period)
        long_sma_series = data_frame.ta.sma(close=data_frame['Close'], length=long_period)

        # Get latest and previous SMA values
        short_sma_latest = short_sma_series.iloc[-1]
        long_sma_latest = long_sma_series.iloc[-1]
        short_sma_previous = short_sma_series.iloc[-2]
        long_sma_previous = long_sma_series.iloc[-2]

        logger.debug(f"Latest short SMA: {short_sma_latest}, Latest long SMA: {long_sma_latest}",
                     extra={"strategy": "SMA"})
        logger.debug(f"Previous short SMA: {short_sma_previous}, Previous long SMA: {long_sma_previous}",
                     extra={"strategy": "SMA"})

        # Determine trade signal
        trade_signal = SimpleMovingAverage.determine_trade_signal(short_sma_latest, short_sma_previous, long_sma_latest,
                                                                  long_sma_previous)

        decision = "hold" if trade_signal is None else "buy" if trade_signal == 1 else "sell"
        logger.info(f"SMA evaluation result: {decision}", extra={"strategy": "SMA"})
        return trade_signal

    @staticmethod
    def backtest(data_frame: DataFrame, short_period: int = 14, long_period: int = 50) -> float:
        """
        Runs a backtest on the data and returns final profit or loss.

        This method simulates a trading strategy using the SMA crossover approach.
        It buys when the short SMA crosses above the long SMA, and sells when the short SMA crosses below the long SMA.
        The initial balance is assumed to be 100,000, and the strategy is tested over the provided market data.

        :param data_frame: The DataFrame containing the market data with a 'Close' column.
        :param short_period: The period for the short-term SMA (default is 14).
        :param long_period: The period for the long-term SMA (default is 50).

        :return: The final return of the strategy as a fraction of the initial balance.
        """
        initial_balance = 100_000
        balance = initial_balance
        shares = 0

        # Calculate SMAs
        short_sma_series = data_frame.ta.sma(close=data_frame['Close'], length=short_period)
        long_sma_series = data_frame.ta.sma(close=data_frame['Close'], length=long_period)

        for i in range(1, len(short_sma_series)):  # Start from 1 to access the previous value without error
            # Skip if either the current or previous value is NaN in either SMA series
            if isna(short_sma_series.iloc[i]) or isna(long_sma_series.iloc[i]) or \
                    isna(short_sma_series.iloc[i - 1]) or isna(long_sma_series.iloc[i - 1]):
                continue

            short_sma_latest = short_sma_series.iloc[i]
            long_sma_latest = long_sma_series.iloc[i]
            short_sma_previous = short_sma_series.iloc[i - 1]
            long_sma_previous = long_sma_series.iloc[i - 1]

            trade_signal = SimpleMovingAverage.determine_trade_signal(
                short_sma_latest, short_sma_previous, long_sma_latest, long_sma_previous
            )

            if trade_signal == 1:  # Buy
                logger.debug("Executed Buy in iteration {}".format(i), extra={"strategy": "SMA"})
                shares = balance // data_frame.iloc[i]['Close']
                balance -= shares * data_frame.iloc[i]['Close']
            elif trade_signal == 0 and shares > 0:  # Sell
                logger.debug("Executed Sell in iteration {}".format(i), extra={"strategy": "SMA"})
                balance += shares * data_frame.iloc[i]['Close']
                shares = 0

        # Log the result of the backtest
        balance += shares * data_frame.iloc[-1]['Close']
        final_return = balance / initial_balance

        logger.info(f"Backtest completed with final return: {final_return:.2%} of the initial balance",
                    extra={"strategy": "SMA"})

        return final_return

