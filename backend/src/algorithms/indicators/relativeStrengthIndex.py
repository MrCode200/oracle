import logging

import pandas
from pandas import DataFrame, Series
from pandas_ta import rsi

from backend.src.algorithms.baseModel import BaseModel

logger: logging.Logger = logging.getLogger("oracle.app")


class RelativeStrengthIndex(BaseModel):
    """
    Implements the Relative Strength Index (RSI) trading strategy.

    The RSI is a momentum oscillator that measures the speed and change of price movements.
    It oscillates between 0 and 100 and is typically used to identify overbought or oversold conditions.
    This strategy evaluates whether the market conditions are ripe for buying or selling based on RSI thresholds.

    Methods
    -------
    determine_trade_signal(rsi_value: float, lower_band: int = 30, upper_band: int = 70) -> int | None
        Determines whether the signal is to buy (1), sell (0), or hold (None) based on the RSI value and bands.

    evaluate(df: DataFrame, period: int = 14, lower_band: int = 30, upper_band: int = 70) -> int | None
        Evaluates the RSI for the provided DataFrame and returns a buy, sell, or hold signal.

    backtest(df: DataFrame, period: int = 14, lower_band: int = 30, upper_band: int = 70, partition_frequency: int = 31) -> float
        Backtests the RSI strategy on historical data and calculates the Return on Investment (ROI).
    """
    _EA_SETTINGS: dict[str, dict[str, int | float]] = {
        "period": {"start": 1, "stop": 200, "step": 1, "type": "int"},
        "lower_band": {"start": 1, "stop": 200, "step": 0.1, "type": "float"},
        "upper_band": {"start": 1, "stop": 200, "step": 0.1, "type": "float"}
    }

    def __init__(self, period: int = 14, lower_band: int = 30, upper_band: int = 70):
        """
        Initializes the Relative Strength Index (RSI) trading strategy.

        :key period: The period to use for RSI calculation (default is 14).
        :key lower_band: The lower RSI threshold for a buy signal (default is 30).
        :key upper_band: The upper RSI threshold for a sell signal (default is 70).
        """
        self.period = period
        self.lower_band = lower_band
        self.upper_band = upper_band

    def determine_trade_signal(self, rsi_series: Series, index: int = 0) -> float:
        """
        Determines whether the signal is to buy, sell, or hold based on the RSI value.

        This method uses predefined RSI bands to classify market conditions into buy, sell, or hold signals:
        - Buy when RSI is below the lower band (default 30).
        - Sell when RSI is above the upper band (default 70).
        - Hold if RSI is between the lower and upper bands.

        :param rsi_series: The calculated RSI values.
        :param index: The index of the RSI value in the series which gets evaluated (default is 0).

        :return: 1 for Buy, -1 for Sell, or 0 for Hold.
        """
        rsi_value: float = rsi_series.iloc[index]
        if rsi_value < self.lower_band:
            return 1
        elif rsi_value > self.upper_band:
            return -1
        else:
            return 0

    def evaluate(self, df: DataFrame) -> float:
        """
        Evaluates the RSI for the provided DataFrame and determines the trade signal.

        This method calculates the RSI based on the closing prices in the DataFrame. It then evaluates
        whether the current RSI is below the lower band (buy), above the upper band (sell), or in between
        (hold). The decision is logged for tracking.

        :param df: The DataFrame containing the market data with a 'Close' column.

        :return: The trade signal (1 for Buy, -1 for Sell, or 0 for Hold).
        """
        rsi_series: pandas.Series = rsi(close=df.Close, length=self.period)
        signal: float = self.determine_trade_signal(rsi_series.iloc[-1])

        logger.info("RSI evaluation result: {}".format(signal), extra={"strategy": "RSI"})

        return signal

    def backtest(self, df: DataFrame, partition_amount: int = 1, sell_percent: float = -0.8,
                 buy_percent: float = 0.8) -> list[float]:
        """
        Backtests the RSI strategy on historical data.

        This method simulates a buy/sell trading strategy based on the RSI indicator over a given period.
        It tracks the balance and number of shares owned and calculates the final Return on Investment (ROI).

        :param df: The DataFrame containing the market data with a 'Close' column.
        :key partition_amount: The amount of paritions which get returned at which to recalculate the Return on Investiment (default is 1)..
        :key sell_percent: The percentage of when to sell, (default is 0.2).
        :key buy_percent: The percentage of when to buy, (default is 0.8).

        :return: A list of parition_amount times of the Return on Investiment.

        :raises ValueError: If parition_amount is less than or equal to 0
        """
        rsi_series: pandas.Series = rsi(close=df.Close, length=self.selperiod)
        signal_func_kwargs: dict[str, any] = {
            "rsi_series": rsi_series
        }

        return super(RelativeStrengthIndex, self).backtest(
            df=df,
            invalid_values=self.period + 1,
            sell_percent=sell_percent,
            buy_percent=buy_percent,
            func_kwargs=signal_func_kwargs,
            partition_amount=partition_amount,
            strategy_name="RSI"
        )
