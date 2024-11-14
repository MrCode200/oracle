from logging import getLogger

import pandas as pd
from pandas import DataFrame, Series

from indicatorBase import Indicator
from backend.src.api import fetch_historical_data

logger = getLogger("oracle.app")


class MovingAverageConvergenceDivergence(Indicator):
    _EA_SETTINGS = {}

    @staticmethod
    def determine_trade_signal(macd_line: Series, signal_line: Series) -> int:
        """
        Determines the trade signal based on the comparison between the MACD line and the signal line.

        The function returns:
            - 1 for a **buy signal** (when the MACD line is above the signal line),
            - -1 for a **sell signal** (when the MACD line is below the signal line),
            - 0 for a **neutral signal** (when the MACD line and signal line are equal).

        :param macd_line: The series of MACD values.
        :param signal_line: The series of signal line values (EMA of the MACD).

        :return: An integer representing the trade signal (1 for buy, -1 for sell, 0 for neutral).
        """
        macd_line_latest: float = macd_line.iloc[0]
        signal_line_latest: float = signal_line.iloc[0]

        if macd_line_latest > signal_line_latest:
            return 1
        elif macd_line_latest < signal_line_latest:
            return -1
        else:
            return 0

    @staticmethod
    def evaluate(data_frame: DataFrame, long_period: int = 26, short_period: int = 12, signal_line_period: int = 9) -> float | int | None:
        """
       Evaluates the trade signal by calculating the MACD and signal line for the given data frame.

       This method calculates the short-term and long-term EMAs, the MACD line (difference between short-term
       and long-term EMAs), and the signal line (9-period EMA of the MACD). It then calls
       `determine_trade_signal` to generate the buy/sell/neutral signal.

       :param data_frame: The pandas DataFrame containing the market data (at least a 'Close' column).
       :key long_period: The period used for the long-term EMA (default is 26).
       :key short_period: The period used for the short-term EMA (default is 12).
       :key signal_line_period: The period used for the signal line EMA (default is 9).

       :return: The trade signal (1 for buy, -1 for sell, 0 for neutral), or None if the DataFrame is empty or invalid.
       """
        long_term_ema: Series = data_frame['Close'].ewm(span=long_period).mean()
        short_term_ema: Series = data_frame['Close'].ewm(span=short_period).mean()

        signal_line_ema: Series = data_frame['Close'].ewm(span=signal_line_period).mean()
        macd_line = short_term_ema - long_term_ema

        trade_signal = MovingAverageConvergenceDivergence.determine_trade_signal(macd_line, signal_line_ema)

        return trade_signal

    @staticmethod
    def backtest(data_frame: DataFrame, partition_amount: int = 1, long_period: int = 26, short_period: int = 12, signal_line_period: int = 9) -> list[float]:
        """

        :param data_frame: The pandas DataFrame containing the market data (at least a 'Close' column).
        :key partition_amount: The amount of paritions which get returned at which to recalculate the Return on Investiment (default is 12).
        :key long_period: The period used for the long-term EMA (default is 26).
        :key short_period: The period used for the short-term EMA (default is 12).
        :key signal_line_period: The period used for the signal line EMA (default is 9).

        :return: A list of parition_amount times of the Return on Investiment.
        """
        pass

data_frame = fetch_historical_data("ETH-USD", '1mo', "1h")

MovingAverageConvergenceDivergence.evaluate(data_frame, long_period=26, short_period=12, signal_line_period=9)
