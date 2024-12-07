import logging
from typing import Optional

from pandas import DataFrame
from yfinance import Ticker  # type: ignore

from backend.src.exceptions import DataFetchError

from backend.src.api.utils import compress_data, determine_interval  # type: ignore

logger: logging.Logger = logging.getLogger("oracle.app")


def fetch_info_data(ticker: str) -> Optional[dict]:  # type: ignore
    """
    Fetch information about a coin from Yahoo Finance using yfinance.
    :param ticker: The ticker symbol of the coin (e.g., 'BTC-USD' for Bitcoin)
    :return: A dictionary containing the fetched information or None on error
    :raises DataFetchError: If an error occurs while fetching data
    """
    try:
        ticker_obj = Ticker(ticker)
        info = ticker_obj.info
        if not info:
            logger.warning(
                f"Failed to fetch info data, probably due to invalid ticker: {ticker}"
            )
            raise DataFetchError(
                message="Failed to fetch info data, probably due to invalid ticker",
                ticker=ticker,
            )

        return ticker_obj.info

    except Exception as e:
        if not isinstance(e, DataFetchError):
            logger.error(f"Error fetching info data: {e}")
            raise DataFetchError(f"Failed to fetch info data: {e}")


def fetch_historical_data(  # type: ignore
    ticker: str,
    period: str = "1m",
    interval: str = "1d",
    start: str | None = None,
    end: str | None = None,
) -> DataFrame:
    """
    Fetch historical market chart data from Yahoo Finance using yfinance.
    :param ticker: The ticker symbol of the coin (e.g., 'BTC-USD' for Bitcoin)
    :param period: Number of days of historical data to fetch, this will be ignored if start and end are passed.
    :param interval: The time interval for each data point (default: '1d')
    :param start: The start date of the historical data (default: None)
    :param end: The end date of the historical data (default: None)
    :return: A DataFrame containing the fetched market chart data or None on error
    :raises AttributeError: If the ticker is invalid
    :raises DataFetchError: If an error occurs while fetching data
    """
    try:
        ticker_obj = Ticker(ticker)

        df = ticker_obj.history(
            period=period, interval=determine_interval(interval), start=start, end=end
        )

        df = compress_data(df, interval)

        if not df.empty:
            logger.info(f"Fetched Data: {ticker = }; {period = }; {interval = };")
            return df
        else:
            logger.error(
                "No data fetched for the given parameters, try using max for period",
                exc_info=True,
            )
            raise DataFetchError(
                message="Data Frame is empty. No data fetched for the given parameters",
                ticker=ticker,
                period=period,
                interval=interval,
                start=start,
                end=end,
            )

    except Exception as e:
        if not isinstance(e, DataFetchError):
            logger.error(f"Error fetching history data: {e}")
            raise DataFetchError(f"Failed to fetch history data: {e}")


if __name__ == '__main__':
    print(type(fetch_info_data("TSLA")['currentPrice']))