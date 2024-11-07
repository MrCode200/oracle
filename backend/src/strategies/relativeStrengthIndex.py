import logging

from pandas import DataFrame, isna
from pandas_ta import rsi

from .indicatorBase import Indicator

logger = logging.getLogger("oracle.app")


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

    backtest(data_frame: DataFrame, period: int = 14, lower_band: int = 30, upper_band: int = 70) -> float
        Backtests the RSI strategy on historical data and calculates the Return on Investment (ROI).
    """

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
        rsi_series = rsi(close=data_frame.Close, length=period)
        signal = RelativeStrengthIndex.determine_trade_signal(rsi_series.iloc[-1])

        decision = "hold" if signal is None else "buy" if signal == 1 else "sell"
        logger.info("RSI evaluation result: {}".format(decision), extra={"strategy": "RSI"})

        return signal

    @staticmethod
    def backtest(data_frame: DataFrame, period: int = 14, lower_band: int = 30, upper_band: int = 70) -> float:
        """
        Backtests the RSI strategy on historical data.

        This method simulates a buy/sell trading strategy based on the RSI indicator over a given period.
        It tracks the balance and number of shares owned and calculates the final Return on Investment (ROI).

        :param data_frame: The DataFrame containing the market data with a 'Close' column.
        :param period: The period to use for RSI calculation (default is 14).
        :param lower_band: The lower RSI threshold for a buy signal (default is 30).
        :param upper_band: The upper RSI threshold for a sell signal (default is 70).

        :return: The Return on Investment (ROI) as a float.
        """
        initial_balance = 1_000_000
        balance = initial_balance
        shares = 0

        rsi_series = rsi(close=data_frame.Close, length=period)

        for i in range(len(rsi_series)):
            if isna(rsi_series.iloc[i]):
                continue

            signal = RelativeStrengthIndex.determine_trade_signal(rsi_series.iloc[i], lower_band, upper_band)

            if shares > 0:
                logger.warning("IT WORKED, TELL NAVID IMIDIATLY")
                balance += shares * data_frame.iloc[i].Dividends

            if signal == 1 and balance >= data_frame.iloc[i].Close:
                shares = balance // data_frame.iloc[i].Close
                balance -= shares * data_frame.iloc[i].Close
                logger.debug(
                    "Executed Buy of {} shares in iteration {}; date: {}".format(shares, i, data_frame.index[i]),
                    extra={"strategy": "RSI"})
            elif signal == 0 and shares > 0:
                logger.debug(
                    "Executed Sell of {} shares in iteration {}; date: {}".format(shares, i, data_frame.index[i]),
                    extra={"strategy": "RSI"})
                balance += shares * data_frame.iloc[i].Close
                shares = 0

        balance += shares * data_frame.iloc[-1].Close
        return_on_investment = balance / initial_balance

        logger.info(f"Backtest completed with Return on Investment of {return_on_investment:.2%}",
                    extra={"strategy": "RSI"})

        return return_on_investment
