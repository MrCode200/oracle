from logging import getLogger

from pandas import DataFrame, Series

from backend.src.services.baseModel import BaseModel
from ..utils import check_crossover, trend_based_pullback

logger = getLogger("oracle.app")


class MovingAverageConvergenceDivergence(BaseModel):
    """
    A class to represent the Moving Average Convergence Divergence (MACD) strategy.

    This strategy uses the MACD and signal line crossovers, momentum, and pullbacks to generate buy and sell signals.
    """

    _EA_SETTINGS = {}

    @staticmethod
    def determine_trade_signal(df: DataFrame, slow_period: int, fast_period: int, signal_line_period: int,
                               max_momentum_lookback: int, momentum_signal_weight: int,
                               zero_line_crossover_weight: int, zero_line_pullback_lookback: int,
                               zero_line_pullback_tolerance_percent: float, zero_line_pullback_weight: float,
                               return_pullback_strength: bool, magnitude_weight: float, rate_of_change_weight: float,
                               weight_impact: float,
                               index: int = -1) -> float:
        """
        Determines the trade signal based on the comparison between the MACD line and the signal line.

        This function computes the MACD line, signal line, and histogram, and returns a buy/sell signal based on
        the MACD line's relationship to the signal line, the momentum strength, and the pullback from the zero line.

        The function returns:
            - 1 for a **buy signal** (when the MACD line is above the signal line),
            - -1 for a **sell signal** (when the MACD line is below the signal line),
            - 0 for a **neutral signal** (when the MACD line and signal line are equal).

        :param df: The pandas DataFrame containing the market data (at least a 'Close' column).
        :param slow_period: The period used for the long-term EMA (default is 26).
        :param fast_period: The period used for the short-term EMA (default is 12).
        :param signal_line_period: The period used for the signal line EMA (default is 9).
        :param max_momentum_lookback: The number of periods to look back for momentum analysis (default is 100).
        :param momentum_signal_weight: The weight assigned to the momentum signal (default is 1).
        :param zero_line_crossover_weight: The weight assigned to the zero line crossover signal (default is 1).
        :param zero_line_pullback_lookback: The number of periods to look back for the zero line pullback (default is 10).
        :param zero_line_pullback_tolerance_percent: The threshold for detecting pullbacks from the zero line (default is 0.1).
        :param zero_line_pullback_weight: The weight assigned to the zero line pullback signal (default is 1).
        :param return_pullback_strength: Whether to return the strength of the pullback.
        :param magnitude_weight: The weight for the magnitude calculation.
        :param rate_of_change_weight: The weight for the rate of change calculation.
        :param weight_impact: The weight impact factor.
        :param index: The index in the DataFrame up to which the calculation should be done (default is -1, i.e., the entire DataFrame).

        :return: A float representing the trade signal confidence (0-1 for buy, -1-0 for sell, 0 for neutral).
        """
        long_term_ema: Series = df['Close'].iloc[:index].ewm(span=slow_period, adjust=False).mean()
        short_term_ema: Series = df['Close'].iloc[:index].ewm(span=fast_period, adjust=False).mean()

        macd_line = short_term_ema - long_term_ema
        signal_line_ema: Series = macd_line.ewm(span=signal_line_period, adjust=False).mean()

        histogram: Series = macd_line - signal_line_ema

        current_macd_value: float = macd_line.iloc[-1]
        current_signal_value: float = signal_line_ema.iloc[-1]
        current_histogram_value: float = histogram.iloc[-1]

        # The momentum is the strength of the trend and an indication
        max_momentum = max(abs(histogram.iloc[-max_momentum_lookback:]))
        max_momentum = 1 if max_momentum == 0 else max_momentum
        normalized_momentum_signal: float = (current_histogram_value / max_momentum) ** 2

        # The Zero Line Crossover
        crossover = check_crossover(current_macd_value, current_signal_value, macd_line.iloc[-2],
                                    signal_line_ema.iloc[-2], True)

        zero_line_crossover_signal = crossover
        if crossover > 0 and current_macd_value > 0:
            zero_line_crossover_signal = crossover
        elif crossover < 0 and current_macd_value < 0:
            zero_line_crossover_signal = -crossover

        tolerance = zero_line_pullback_tolerance_percent * max_momentum
        zero_line_pullback_signal = trend_based_pullback(macd_line, 0, tolerance,
                                                         zero_line_pullback_lookback,
                                                         return_pullback_strength=True)

        if not zero_line_pullback_signal:
            zero_line_pullback_signal = 0

        base_weight = momentum_signal_weight + zero_line_crossover_weight + zero_line_pullback_weight
        weight = 1 if base_weight == 0 else (normalized_momentum_signal * momentum_signal_weight +
                                             zero_line_crossover_signal * zero_line_crossover_weight +
                                             zero_line_pullback_signal * zero_line_pullback_weight) / base_weight

        if current_histogram_value > 0:
            return 1 - (1 - weight) * weight_impact
        elif current_histogram_value < 0:
            return -(1 - (1 - weight) * weight_impact)
        else:
            return 0

    @staticmethod
    def evaluate(df: DataFrame, fast_period: int = 26, slow_period: int = 12,
                 signal_line_period: int = 9, max_momentum_lookback: int = 100, momentum_signal_weight: int = 0,
                 zero_line_crossover_weight: int = 0.5, zero_line_pullback_lookback: int = 100,
                 zero_line_pullback_tolerance_percent: float = 0.1, zero_line_pullback_weight: float = 0,
                 return_pullback_strength: bool = True, magnitude_weight: float = 1, rate_of_change_weight: float = 1,
                 weight_impact: float = 1) -> float | int | None:
        """
        Evaluates the trade signal by calculating the MACD and signal line for the given data frame.

        This method calculates the short-term and long-term EMAs, the MACD line (difference between short-term
        and long-term EMAs), and the signal line (9-period EMA of the MACD). It then calls
        `determine_trade_signal` to generate the buy/sell/neutral signal.

        :param df: The pandas DataFrame containing the market data (at least a 'Close' column).
        :param fast_period: The period used for the long-term EMA (default is 26).
        :param slow_period: The period used for the short-term EMA (default is 12).
        :param signal_line_period: The period used for the signal line EMA (default is 9).
        :param max_momentum_lookback: The number of periods to look back for momentum analysis (default is 100).
        :param momentum_signal_weight: The weight assigned to the momentum signal (default is 1).
        :param zero_line_crossover_weight: The weight assigned to the zero line crossover signal (default is 1).
        :param zero_line_pullback_lookback: The number of periods to look back for the zero line pullback (default is 10).
        :param zero_line_pullback_tolerance_percent: The threshold for detecting pullbacks from the zero line (default is 0.1).
        :param zero_line_pullback_weight: The weight assigned to the zero line pullback signal (default is 1).
        :param return_pullback_strength: Whether to return the strength of the pullback.
        :param magnitude_weight: The weight for the magnitude calculation.
        :param rate_of_change_weight: The weight for the rate of change calculation.
        :param weight_impact: The weight impact factor.

        :return: The trade signal as an integer (1 for buy, -1 for sell, 0 for neutral),
                 or None if the DataFrame is empty or invalid.

        :raises ValueError: If fast_period is less than slow_period.
        """
        if fast_period < slow_period:
            raise ValueError("fast_period must be greater than slow_period")

        return MovingAverageConvergenceDivergence.determine_trade_signal(df, fast_period, slow_period,
                                                                         signal_line_period, max_momentum_lookback,
                                                                         momentum_signal_weight,
                                                                         zero_line_crossover_weight,
                                                                         zero_line_pullback_lookback,
                                                                         zero_line_pullback_tolerance_percent, weight_impact)

    @staticmethod
    def backtest(df: DataFrame, partition_amount: int = 1, fast_period: int = 12, slow_period: int = 26,
                 signal_line_period: int = 9,
                 sell_percent: float = -0.8, buy_percent: float = 0.8, max_momentum_lookback: int = 100,
                 momentum_signal_weight: float = 0,
                 zero_line_crossover_weight: float = 0, zero_line_pullback_lookback: int = 10,
                 zero_line_pullback_tolerance_percent: float = 1, zero_line_pullback_weight: float = 0,
                 return_pullback_strength: bool = True, magnitude_weight: float = 1, rate_of_change_weight: float = 1,
                 weight_impact: float = 1) -> list[float]:
        """
        Backtests the MACD strategy on historical data.

        This method simulates a buy/sell trading strategy based on the MACD indicator over a given period.
        It tracks the balance and number of shares owned and calculates the final Return on Investment (ROI).

        :param df: The pandas DataFrame containing the market data (at least a 'Close' column).
        :param partition_amount: The number of partitions to divide the data into for backtesting,
                                 which determines how often the Return on Investment (ROI) is recalculated.
        :param fast_period: The period used for the long-term EMA (default is 26).
        :param slow_period: The period used for the short-term EMA (default is 12).
        :param signal_line_period: The period used for the signal line EMA (default is 9).
        :param sell_percent: The percentage of when to sell, (default is -0.8).
        :param buy_percent: The percentage of when to buy, (default is 0.8).
        :param max_momentum_lookback: The number of periods to look back for momentum analysis (default is 100).
        :param momentum_signal_weight: The weight assigned to the momentum signal (default is 1).
        :param zero_line_crossover_weight: The weight assigned to the zero line crossover signal (default is 1).
        :param zero_line_pullback_lookback: The number of periods to look back for the zero line pullback (default is 10).
        :param zero_line_pullback_tolerance_percent: The threshold for detecting pullbacks from the base line in percentage (default is 0.1).
        :param zero_line_pullback_weight: The weight assigned to the zero line pullback signal (default is 1).
        :param return_pullback_strength: Whether to return the strength of the pullback.
        :param magnitude_weight: The weight for the magnitude calculation.
        :param rate_of_change_weight: The weight for the rate of change calculation.
        :param weight_impact: The weight impact factor.

        :return: A list of ROI values calculated at each partition of the backtest.

        :raises ValueError: If fast_period is less than slow_period.
        """
        if fast_period > slow_period:
            raise ValueError("fast_period must be lesser than slow_period")

        signal_func_kwargs: dict[str, any] = {
            "df": df,
            "fast_period": fast_period,
            "slow_period": slow_period,
            "signal_line_period": signal_line_period,
            "max_momentum_lookback": max_momentum_lookback,
            "momentum_signal_weight": momentum_signal_weight,
            "zero_line_crossover_weight": zero_line_crossover_weight,
            "zero_line_pullback_lookback": zero_line_pullback_lookback,
            "zero_line_pullback_tolerance_percent": zero_line_pullback_tolerance_percent,
            "zero_line_pullback_weight": zero_line_pullback_weight,
            "return_pullback_strength": return_pullback_strength,
            "magnitude_weight": magnitude_weight,
            "rate_of_change_weight": rate_of_change_weight,
            "weight_impact": weight_impact
        }

        return BaseModel.backtest(
            df=df,
            indicator_cls=MovingAverageConvergenceDivergence,
            invalid_values=fast_period,
            func_kwargs=signal_func_kwargs,
            buy_percent=buy_percent,
            sell_percent=sell_percent,
            partition_amount=partition_amount,
            strategy_name="MACD"
        )
