from logging import getLogger

from pandas import DataFrame, Series

from .indicatorBase import BaseIndicator

logger = getLogger("oracle.app")


class ExponentialMovingAverage(BaseIndicator):
    _EA_SETTINGS: dict[str, dict[str, int | float]] = {}

    @staticmethod
    def determine_trade_signal(df: DataFrame, period: int, index: int = -1) -> float:
        ewm = df['Close'].iloc[:index].ewm(span=period, adjust=False).mean()

        if ewm.iloc[-1] > df['Close'].iloc[-1]:
            return 1
        elif ewm.iloc[-1] < df['Close'].iloc[-1]:
            return -1
        else:
            return 0

    @staticmethod
    def evaluate(df: DataFrame, period: int) -> float | int | None:
        return ExponentialMovingAverage.determine_trade_signal(df, period)

    @staticmethod
    def backtest(df: DataFrame, period: int, partition_amount: int = 1) -> list[float]:
        signal_func_kwargs: dict[str, any] = {
            "df": df,
            "period": period
        }

        return super().backtest(
            df=df,
            func_kwargs=signal_func_kwargs,
            invalid_values=period,
            partition_amount=partition_amount,
            strategy_name="EMA"
        )
