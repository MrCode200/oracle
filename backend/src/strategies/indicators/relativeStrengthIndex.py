import logging

import pandas
from pandas import DataFrame, isna
from pandas_ta import rsi

from .indicatorBase import Indicator

logger: logging.Logger = logging.getLogger("oracle.app")


class RelativeStrengthIndex(Indicator):
    """
    Implements the Relative Strength Index (RSI) trading strategy.

    The RSI is a momentum oscillator that measures the speed and change of price movements.
    It oscillates between 0 and 100 and is typically used to identify overbought or oversold conditions.
    This strategy evaluates whether the market conditions are ripe for buying or selling based on RSI thresholds.

    Methods
    -------
    determine_trade_signal(rsi_value: float, lower_band: int = 30, upper_band: int = 70) -> int | None
        Determines whether the signal is to buy (1), sell (0), or hold (None) based on the RSI value and bands.

    evaluate(data_frame: DataFrame, period: int = 14, lower_band: int = 30, upper_band: int = 70) -> int | None
        Evaluates the RSI for the provided DataFrame and returns a buy, sell, or hold signal.

    backtest(data_frame: DataFrame, period: int = 14, lower_band: int = 30, upper_band: int = 70, partition_frequency: int = 31) -> float
        Backtests the RSI strategy on historical data and calculates the Return on Investment (ROI).
    """
    _EA_RANGE: tuple[int, int] = (0, 100)

    @staticmethod
    def determine_trade_signal(rsi_value: float, lower_band: int = 30, upper_band: int = 70) -> int | None:
        """
        Determines whether the signal is to buy, sell, or hold based on the RSI value.

        This method uses predefined RSI bands to classify market conditions into buy, sell, or hold signals:
        - Buy when RSI is below the lower band (default 30).
        - Sell when RSI is above the upper band (default 70).
        - Hold if RSI is between the lower and upper bands.

        :param rsi_value: The current RSI value to evaluate.
        :param lower_band: The RSI value below which to trigger a buy signal (default is 30).
        :param upper_band: The RSI value above which to trigger a sell signal (default is 70).

        :return: 1 for Buy, 0 for Sell, or None for Hold.
        """
        if rsi_value < lower_band:
            return 1  # Buy signal
        elif rsi_value > upper_band:
            return 0  # Sell signal
        else:
            return None  # Hold signal

    @staticmethod
    def evaluate(data_frame: DataFrame, period: int = 14, lower_band: int = 30, upper_band: int = 70) -> int | None:
        """
        Evaluates the RSI for the provided DataFrame and determines the trade signal.

        This method calculates the RSI based on the closing prices in the DataFrame. It then evaluates
        whether the current RSI is below the lower band (buy), above the upper band (sell), or in between
        (hold). The decision is logged for tracking.

        :param data_frame: The DataFrame containing the market data with a 'Close' column.
        :param period: The period to use for RSI calculation (default is 14).
        :param lower_band: The lower RSI threshold for a buy signal (default is 30).
        :param upper_band: The upper RSI threshold for a sell signal (default is 70).

        :return: The trade signal (1 for Buy, 0 for Sell, or None for Hold).
        """
        rsi_series: pandas.Series = rsi(close=data_frame.Close, length=period)
        signal: int | None = RelativeStrengthIndex.determine_trade_signal(rsi_series.iloc[-1])

        decision: str = "hold" if signal is None else "buy" if signal == 1 else "sell"
        logger.info("RSI evaluation result: {}".format(decision), extra={"strategy": "RSI"})

        return signal

    @staticmethod
    def backtest(data_frame: DataFrame, partition_frequency: int = 31, period: int = 14, lower_band: int = 30, upper_band: int = 70) -> list[float]:
        """
        Backtests the RSI strategy on historical data.

        This method simulates a buy/sell trading strategy based on the RSI indicator over a given period.
        It tracks the balance and number of shares owned and calculates the final Return on Investment (ROI).

        :param data_frame: The DataFrame containing the market data with a 'Close' column.
        :key partition_frequency: The frequency at which to recalculate the Return on Investiment (default is 31).
        :param period: The period to use for RSI calculation (default is 14).
        :param lower_band: The lower RSI threshold for a buy signal (default is 30).
        :param upper_band: The upper RSI threshold for a sell signal (default is 70).

        :return: The Return on Investment (ROI) as a float.
        """
        base_balance: int = 1_000_000
        balance: float = base_balance
        shares: float = 0
        net_worth_history: list[float] = []

        rsi_series: pandas.Series = rsi(close=data_frame.Close, length=period)

        for i in range(period + 1, len(rsi_series)):
            trade_signal: int | None = RelativeStrengthIndex.determine_trade_signal(rsi_series.iloc[i], lower_band, upper_band)

            is_partition_cap_reached = (i - period) % partition_frequency == 0

            base_balance, balance, shares = Indicator.process_trade_signal(
                base_balance, balance, shares,
                data_frame.iloc[i].Close, trade_signal,
                net_worth_history, is_partition_cap_reached,
                "RSI"
            )

        total_net_worth = balance +shares * data_frame.iloc[-1].Close
        net_worth_history.append(total_net_worth / base_balance)

        logger.info(f"Backtest completed with Return on Investment of {[str(roi * 100) for roi in net_worth_history]}",
                    extra={"strategy": "RSI"})

        return net_worth_history
