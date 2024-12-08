from logging import getLogger

from pandas import DataFrame, Series
import numpy as np

from src.services.indicators import BaseIndicator
from src.services.indicators.utils import check_crossover, trend_based_pullback

logger = getLogger("oracle.app")


class MovingAverageConvergenceDivergence(BaseIndicator):
    """
    A class to represent the Moving Average Convergence Divergence (MACD) strategy.

    This strategy uses the MACD and signal line crossovers, momentum, and pullbacks to generate buy and sell signals.
    """

    _EA_SETTINGS = {}

    def __init__(self, fast_period: int = 12, slow_period: int = 26,
                 signal_line_period: int = 9, momentum_max_lookback: int = 100, momentum_signal_weight: float = 1,
                 crossover_return_weight: bool = True, crossover_max_gradient_degree: float = 90,
                 crossover_gradient_signal_weight: float = 1.0, crossover_weight_impact: float = 1.0,
                 zero_line_crossover_weight: float = 1, zero_line_pullback_lookback: int = 10,
                 zero_line_pullback_tolerance_percent: float = 0.1, zero_line_pullback_weight: float = 1,
                 return_pullback_strength: bool = True, magnitude_weight: float = 1, rate_of_change_weight: float = 1,
                 weight_impact: float = 1):
        """
        Initializes a new instance of the MovingAverageConvergenceDivergence class.

        :key slow_period: The period used for the long-term EMA (default is 26).
        :key fast_period: The period used for the short-term EMA (default is 12).
        :key signal_line_period: The period used for the signal line EMA (default is 9).
        :key momentum_max_lookback: The number of periods to look back for momentum analysis (default is 100).
        :key momentum_signal_weight: The weight assigned to the momentum signal (default is 1).
        :key crossover_return_weight: If True, also returns the strength of the crossover.
        :key crossover_max_gradient_degree: The maximum degree of the gradient which gets used to calculate the strength of the crossover.
        :key crossover_gradient_signal_weight: The weight used for the strength calculated based on the gradient for the crossover.
        :key crossover_weight_impact: How strong the impact of the weights are on the crossover output. Example: 1 - (1- weight) * weight_impact
        :key zero_line_crossover_weight: The weight assigned to the zero line crossover signal (default is 1).
        :key zero_line_pullback_lookback: The number of periods to look back for the zero line pullback (default is 10).
        :key zero_line_pullback_tolerance_percent: The limit for detecting pullbacks from the zero line (default is 0.1).
        :key zero_line_pullback_weight: The weight assigned to the zero line pullback signal (default is 1).
        :key return_pullback_strength: Whether to return the strength of the pullback.
        :key magnitude_weight: The weight for the magnitude calculation.
        :key rate_of_change_weight: The weight for the rate of change calculation.
        :key weight_impact: The weight impact factor.

        :raises ValueError: If fast_period is less than slow_period.
        """
        if fast_period > slow_period:
            raise ValueError("fast_period must be smaller than slow_period")

        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_line_period = signal_line_period
        self.max_momentum_lookback = momentum_max_lookback
        self.momentum_signal_weight = momentum_signal_weight
        self.return_crossover_weigth = crossover_return_weight
        self.max_crossover_gradient_degree = crossover_max_gradient_degree
        self.crossover_gradient_signal_weight = crossover_gradient_signal_weight
        self.crossover_weight_impact = crossover_weight_impact
        self.zero_line_crossover_weight = zero_line_crossover_weight
        self.zero_line_pullback_lookback = zero_line_pullback_lookback
        self.zero_line_pullback_tolerance_percent = zero_line_pullback_tolerance_percent
        self.zero_line_pullback_weight = zero_line_pullback_weight
        self.return_pullback_strength = return_pullback_strength
        self.magnitude_weight = magnitude_weight
        self.rate_of_change_weight = rate_of_change_weight
        self.weight_impact = weight_impact


    def evaluate(self, df: DataFrame) -> float:
        """
        Evaluates the trade signal by calculating the MACD and signal line for the given data frame.

        This method calculates the short-term and long-term EMAs, the MACD line (difference between short-term
        and long-term EMAs), and the signal line (9-period EMA of the MACD). It then calls
        `determine_trade_signal` to generate the buy/sell/neutral signal.

        :param df: The pandas DataFrame containing the market data (at least a 'Close' column).

        :return: The trade signal as an integer (1 for buy, -1 for sell, 0 for neutral),
                 or None if the DataFrame is empty or invalid.
        """
        if len(df) < self.slow_period:
            return 0

        long_term_ema: Series = df['Close'].ewm(span=self.slow_period, adjust=False).mean()
        short_term_ema: Series = df['Close'].ewm(span=self.fast_period, adjust=False).mean()

        macd_line = short_term_ema - long_term_ema
        signal_line_ema: Series = macd_line.ewm(span=self.signal_line_period, adjust=False).mean()

        histogram: Series = macd_line - signal_line_ema

        current_macd_value: float = macd_line.iloc[-1]
        current_signal_value: float = signal_line_ema.iloc[-1]
        current_histogram_value: float = histogram.iloc[-1]

        # Calculate momentum as the maximum absolute value of the histogram over the lookback period.
        # This shows the strength of the trend.
        max_momentum = max(np.abs(histogram.iloc[-self.max_momentum_lookback:]))
        max_momentum = 1 if max_momentum == 0 else max_momentum  # Avoid division by zero
        normalized_momentum_signal: float = (current_histogram_value / max_momentum) ** 2

        # The Zero Line Crossover: Checks if the MACD line crosses above or below the signal line.
        crossover = check_crossover(current_macd_value, current_signal_value, macd_line.iloc[-2],
                                    signal_line_ema.iloc[-2], self.return_crossover_weigth,
                                    self.max_crossover_gradient_degree,
                                    self.crossover_gradient_signal_weight, self.crossover_weight_impact)

        zero_line_crossover_signal = crossover
        # Adjust the crossover signal depending on the position of the MACD line (above or below zero).
        if crossover > 0 and current_macd_value > 0:
            zero_line_crossover_signal = crossover
        elif crossover < 0 and current_macd_value < 0:
            zero_line_crossover_signal = -crossover

        # Calculate the zero line pullback signal, which checks if the MACD line pulls back to the zero line.
        tolerance = self.zero_line_pullback_tolerance_percent * max_momentum
        zero_line_pullback_signal = trend_based_pullback(macd_line, 0, tolerance,
                                                         self.zero_line_pullback_lookback,
                                                         return_pullback_strength=True)

        # If no pullback signal is generated, set it to 0.
        if not zero_line_pullback_signal:
            zero_line_pullback_signal = 0
        else:
            # Can be removed if it ever happens (o′┏▽┓｀o)
            logger.critical(f"Zero Line Pullback Signal: {zero_line_pullback_signal}", extra={"indicator": "MACD"})

        base_weight = self.momentum_signal_weight + self.zero_line_crossover_weight + self.zero_line_pullback_weight
        weight = 1 if base_weight == 0 else (normalized_momentum_signal * self.momentum_signal_weight +
                                             zero_line_crossover_signal * self.zero_line_crossover_weight +
                                             zero_line_pullback_signal * self.zero_line_pullback_weight) / base_weight

        # Calculate the final confidence score based on the current histogram value.
        # If the histogram is positive, the confidence is increased, otherwise decreased.
        confidence: float = 0
        if current_histogram_value > 0:
            confidence = 1 - (1 - weight) * self.weight_impact
        elif current_histogram_value < 0:
            confidence = -(1 - (1 - weight) * self.weight_impact)

        # Log the MACD evaluation result for debugging and analysis purposes.
        logger.info(f"Evaluated a confidence of {confidence}", extra={"indicator": self.__class__.__name__})

        return confidence