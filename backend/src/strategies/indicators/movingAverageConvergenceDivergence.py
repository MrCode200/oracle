from logging import getLogger

from pandas import DataFrame, Series

from .baseIndicator import BaseIndicator

logger = getLogger("oracle.app")


class MovingAverageConvergenceDivergence(BaseIndicator):
    _EA_SETTINGS = {}

    @staticmethod
    def determine_trade_signal(df: DataFrame, long_period: int, short_period: int, signal_line_period: int,
                               index: int = -1) -> int:
        """
        Determines the trade signal based on the comparison between the MACD line and the signal line.

        The function returns:
            - 1 for a **buy signal** (when the MACD line is above the signal line),
            - -1 for a **sell signal** (when the MACD line is below the signal line),
            - 0 for a **neutral signal** (when the MACD line and signal line are equal).

        :param df: The pandas DataFrame containing the market data (at least a 'Close' column).
        :param long_period: The period used for the long-term EMA (default is 26).
        :param short_period: The period used for the short-term EMA (default is 12).
        :param signal_line_period: The period used for the signal line EMA (default is 9).
        :param index: The index in the DataFrame up to which the calculation should be done (default is -1, i.e., the entire DataFrame).

        :return: An integer representing the trade signal (1 for buy, -1 for sell, 0 for neutral).
        """
        long_term_ema: Series = df['Close'].iloc[:index].ewm(span=long_period, adjust=False).mean()
        short_term_ema: Series = df['Close'].iloc[:index].ewm(span=short_period, adjust=False).mean()

        macd_line = short_term_ema - long_term_ema
        signal_line_ema: Series = macd_line.ewm(span=signal_line_period, adjust=False).mean()


        signal_line_latest: float = signal_line_ema.iloc[-1]
        macd_line_latest: float = macd_line.iloc[-1]

        if macd_line_latest > signal_line_latest:
            return 1
        elif macd_line_latest < signal_line_latest:
            return -1
        else:
            return 0

    @staticmethod
    def evaluate(df: DataFrame, long_period: int = 26, short_period: int = 12,
                 signal_line_period: int = 9) -> float | int | None:
        """
        Evaluates the trade signal by calculating the MACD and signal line for the given data frame.

        This method calculates the short-term and long-term EMAs, the MACD line (difference between short-term
        and long-term EMAs), and the signal line (9-period EMA of the MACD). It then calls
        `determine_trade_signal` to generate the buy/sell/neutral signal.

        :param df: The pandas DataFrame containing the market data (at least a 'Close' column).
        :param long_period: The period used for the long-term EMA (default is 26).
        :param short_period: The period used for the short-term EMA (default is 12).
        :param signal_line_period: The period used for the signal line EMA (default is 9).

        :return: The trade signal as an integer (1 for buy, -1 for sell, 0 for neutral),
                 or None if the DataFrame is empty or invalid.

        :raises ValueError: If long_period is less than short_period.
        """
        if long_period < short_period:
            raise ValueError("long_period must be greater than short_period")

        return MovingAverageConvergenceDivergence.determine_trade_signal(df, long_period, short_period,
                                                                         signal_line_period)

    @staticmethod
    def backtest(df: DataFrame, partition_amount: int = 1, long_period: int = 26, short_period: int = 12,
                 signal_line_period: int = 9) -> list[float]:
        """
        Backtests the MACD strategy on historical data.

        This method simulates a buy/sell trading strategy based on the MACD indicator over a given period.
        It tracks the balance and number of shares owned and calculates the final Return on Investment (ROI).

        :param df: The pandas DataFrame containing the market data (at least a 'Close' column).
        :param partition_amount: The number of partitions to divide the data into for backtesting,
                                 which determines how often the Return on Investment (ROI) is recalculated.
        :param long_period: The period used for the long-term EMA (default is 26).
        :param short_period: The period used for the short-term EMA (default is 12).
        :param signal_line_period: The period used for the signal line EMA (default is 9).

        :return: A list of ROI values calculated at each partition of the backtest.

        :raises ValueError: If long_period is less than short_period.
        """
        if long_period < short_period:
            raise ValueError("long_period must be greater than short_period")

        signal_func_kwargs: dict[str, any] = {
            "df": df,
            "long_period": long_period,
            "short_period": short_period,
            "signal_line_period": signal_line_period
        }

        return BaseIndicator.backtest(
            df=df,
            indicator_cls=MovingAverageConvergenceDivergence,
            invalid_values=long_period,
            func_kwargs=signal_func_kwargs,
            partition_amount=partition_amount,
            strategy_name="MACD"
        )
