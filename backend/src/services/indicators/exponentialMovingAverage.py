from logging import getLogger

from pandas import DataFrame

from backend.src.services.baseModel import BaseModel

logger = getLogger("oracle.app")


class ExponentialMovingAverage(BaseModel):
    _EA_SETTINGS: dict[str, dict[str, int | float]] = {}

    def __init__(self, period: int):
        """
        Initializes the ExponentialMovingAverage with a specified period.

        :param period: The number of periods to use for calculating the EMA.
        """
        self.period = period

    def determine_trade_signal(self, df: DataFrame, index: int = -1) -> float:
        """
        Evaluates the trade signal for a given period.

        :param df: The DataFrame containing market data with a 'Close' column.
        :returns: The trade signal for the specified period.
        """
        ewm = df['Close'].iloc[:index].ewm(span=self.period, adjust=False).mean()

        if ewm.iloc[-1] > df['Close'].iloc[-1]:
            return 1
        elif ewm.iloc[-1] < df['Close'].iloc[-1]:
            return -1
        else:
            return 0

    def evaluate(self, df: DataFrame) -> float:
        signal: float = self.determine_trade_signal(df, self.period)
        logger.info("RSI evaluation result: {}".format(signal), extra={"strategy": "RSI"})
        return signal

    def backtest(self, df: DataFrame, partition_amount: int = 1, sell_percent: float = -0.8,
                 buy_percent: float = 0.8) -> list[float]:
        """
        Conducts a backtest using the EMA strategy on the provided market data.

        :param df: The pandas DataFrame containing the market data (at least a 'Close' column).
        :param partition_amount: The number of partitions to divide the data into for backtesting,
                                 which determines how often the Return on Investment (ROI) is recalculated.
        :param sell_percent: The percentage of when to sell, (default is -0.8).
        :param buy_percent: The percentage of when to buy, (default is 0.8).

        :return: A list of ROI values calculated at each partition of the backtest.
        """
        signal_func_kwargs: dict[str, any] = {
            "df": df,
        }

        return BaseModel.backtest(
            df=df,
            func_kwargs=signal_func_kwargs,
            invalid_values=self.period,
            partition_amount=partition_amount,
            strategy_name="EMA"
        )
