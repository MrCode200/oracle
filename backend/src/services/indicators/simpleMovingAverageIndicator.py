import logging

import pandas
from pandas import DataFrame, Series
from pandas_ta import sma

from src.services.indicators import BaseIndicator
from src.services.indicators.utils import check_crossover

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

    def __init__(
        self,
        short_period: int = 14,
        long_period: int = 50,
        return_crossover_weight: bool = True,
        max_crossover_gradient_degree: float = 90,
        crossover_gradient_signal_weight: float = 1,
        crossover_weight_impact: float = 1,
    ):
        """
        Initializes the SimpleMovingAverage class.

        :param short_period: The period for the short-term SMA (default is 14).
        :param long_period: The period for the long-term SMA (default is 50).
        :key return_crossover_weight: If True, also returns the strength of the crossover.
        :key max_crossover_gradient_degree: The maximum degree of the gradient which gets used to calculate the strength of the crossover.
        :key crossover_gradient_signal_weight: The weight used for the strength calculated based on the gradient for the crossover.
        :key crossover_weight_impact: How strong the impact of the weights are on the crossover output. Example: 1 - (1- weight) * weight_impact
        """
        self.short_period: int = short_period
        self.long_period: int = long_period
        self.return_crossover_weight: bool = return_crossover_weight
        self.max_crossover_gradient_degree: float = max_crossover_gradient_degree
        self.crossover_gradient_signal_weight: float = crossover_gradient_signal_weight
        self.crossover_weight_impact: float = crossover_weight_impact

    def evaluate(self, df: DataFrame) -> float:
        """
        Evaluates the latest SMA cross and logs the decision.

        This method calculates the short and long period SMAs for the provided data.
        It then determines the trade signal based on the crossover of the SMAs and returns the decision.

        :param df: The DataFrame containing the market data with a 'Close' column.

        :return: The trade confidence (1 for Buy, -1 for Sell, or 0 for Hold).
        """
        if len(df) < self.long_period:
            return 0

        short_sma_series: pandas.Series = sma(close=df.Close, length=self.short_period)
        long_sma_series: pandas.Series = sma(close=df.Close, length=self.long_period)

        short_sma_latest: float = short_sma_series.iloc[-1]
        long_sma_latest: float = long_sma_series.iloc[-1]
        short_sma_previous: float = short_sma_series.iloc[-2]
        long_sma_previous: float = long_sma_series.iloc[-2]

        crossover_signal = check_crossover(
            short_sma_latest,
            long_sma_latest,
            short_sma_previous,
            long_sma_previous,
            self.return_crossover_weight,
            self.max_crossover_gradient_degree,
            self.crossover_gradient_signal_weight,
            self.crossover_weight_impact,
        )

        logger.info(f"Evaluated a confidence of {crossover_signal}", extra={"indicator": self.__class__.__name__})


        return crossover_signal