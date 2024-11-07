import logging

from pandas import DataFrame, isna
from pandas_ta import rsi

from .indicatorBase import Indicator

logger = logging.getLogger("oracle.app")

class RelativeStrengthIndex(Indicator):
    @staticmethod
    def determine_trade_signal(rsi_value: float, lower_band: int = 30, upper_band: int = 70) -> int | None:
        if rsi_value < lower_band:
            return 1
        elif rsi_value > upper_band:
            return 0
        else:
            return None

    @staticmethod
    def evaluate(data_frame: DataFrame, period: int = 14, lower_band: int = 30, upper_band: int = 70) -> int | None:
        rsi_series = rsi(close=data_frame['Close'], length=period)
        signal = RelativeStrengthIndex.determine_trade_signal(rsi_series.iloc[-1])

        decision = "hold" if signal is None else "buy" if signal == 1 else "sell"
        logger.info("RSI evaluation result: {}".format(decision), extra={"strategy": "RSI"})

        return signal

    @staticmethod
    def backtest(data_frame: DataFrame, period: int = 14, lower_band: int = 30, upper_band: int = 70) -> float:
        initial_balance = 1_000_000
        balance = initial_balance
        shares = 0

        rsi_series = rsi(close=data_frame['Close'], length=period)

        for i in range(len(rsi_series)):
            if isna(rsi_series.iloc[i]):
                continue

            signal = RelativeStrengthIndex.determine_trade_signal(rsi_series.iloc[i], lower_band, upper_band)

            if signal == 1 and balance >= data_frame.iloc[i]['Close']:
                shares = balance // data_frame.iloc[i]['Close']
                balance -= shares * data_frame.iloc[i]['Close']
                logger.debug("Executed Buy of {} shares in iteration {}; date: {}".format(shares, i, data_frame.index[i]), extra={"strategy": "RSI"})
            elif signal == 0 and shares > 0:
                logger.debug("Executed Sell of {} shares in iteration {}; date: {}".format(shares,i, data_frame.index[i]), extra={"strategy": "RSI"})
                balance += shares * data_frame.iloc[i]['Close']
                shares = 0

        balance += shares * data_frame.iloc[-1]['Close']
        return_on_investment = balance / initial_balance

        logger.info(f"Backtest completed with Return on Investment of {return_on_investment:.2%}",
                    extra={"strategy": "RSI"})

        return return_on_investment
