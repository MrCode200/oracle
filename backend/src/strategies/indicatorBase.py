import logging
from abc import ABC, abstractmethod

from pandas import DataFrame, isna
import pandas_ta as ta

logger = logging.getLogger("oracle.app")

class Indicator(ABC):
    """
    Defines an abstract base class for indicators.

    Methods
        - run(database: Iterable) -> float: Abstract method to run the strategies on the provided database.
        - test_accuracy(database: Iterable) -> float: Abstract method to test the accuracy of the strategies on the provided database.
    """
    @staticmethod
    @abstractmethod
    def determine_trade_signal():
        ...

    @staticmethod
    @abstractmethod
    def evaluate(data_frame: DataFrame) -> int | None:
        ...

    @staticmethod
    @abstractmethod
    def backtest(data_frame: DataFrame) -> float:
        initial_balance = 100_000
        balance = initial_balance
        shares = 0

        ... # Evaluate the indicator

        for i in len(data_frame):
            if isna(data_frame.iloc[i]['Close']):
                continue

            signal = ...

            if shares > 0:
                logger.warning("IT WORKED, TELL NAVID IMIDIATLY") if data_frame.iloc[i].Dividends != 0.0 else None
                balance += shares * data_frame.iloc[i].Dividends

            if signal == 1 and balance >= data_frame.iloc[i]['Close']:
                shares = balance // data_frame.iloc[i]['Close']
                balance -= shares * data_frame.iloc[i]['Close']
                logger.debug("Executed Buy of {} shares in iteration {}; date: {}".format(shares, i, data_frame.iloc[i]['Date']), extra={"strategy": "Unknown"})
            elif signal == 0 and shares > 0:
                logger.debug("Executed Sell of {} shares in iteration {}; date: {}".format(shares,i, data_frame.iloc[i]['Date']), extra={"strategy": "Unknown"})
                balance += shares * data_frame.iloc[i]['Close']
                shares = 0

        # Log the result of the backtest
        balance += shares * data_frame.iloc[-1]['Close']
        return_on_investment = balance / initial_balance

        logger.info(f"Backtest completed with Return on Investment of {return_on_investment:.2%}",
                    extra={"strategy": "Unknown"})

        return return_on_investment


if __name__ == '__main__':
    print(help(ta.Strategy))