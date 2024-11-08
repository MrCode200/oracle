import logging

import yfinance as yf  # type: ignore
from pandas import DataFrame

from backend.src.exceptions import DataFetchError
logger: logging.Logger = logging.getLogger("oracle.app")


def fetch_historical_data(ticker: str, period: str = "1m", interval: str = "1d", start: str = None, end: str = None) -> DataFrame | int:
    """
    Fetch historical market chart data from Yahoo Finance using yfinance.

    :param ticker: The ticker symbol of the coin (e.g., 'BTC-USD' for Bitcoin)
    :param period: Number of days of historical data to fetch, this will be ignored if start and end are passed.
    :param interval: The time interval for each data point (default: '1d')
    :param start: The start date of the historical data (default: None)
    :param end: The end date of the historical data (default: None)
    :return: A DataFrame containing the fetched market chart data or None on error
    """
    try:
        ticker_obj  = yf.Ticker(ticker)

        if ticker_obj.info.get("longName") is None:
            logger.error(f"Invalid Ticker: {ticker}")
            raise AttributeError(f"Invalid Ticker: {ticker}")
    except Exception as e:
        if not isinstance(e, AttributeError):
            logger.error(f"Error fetching info data: {e}")
            raise DataFetchError(f"Failed to fetch info data: {e}", ticker=ticker)
        raise

    try:
        # Fetch historical market data as pandas DataFrame
        data_frame = ticker_obj .history(period=period, interval=interval, start=start, end=end)

        if not data_frame.empty:
            logger.info(f"Fetched Data: {ticker = }; {period = }; {interval = };")
            return data_frame
        else:
            logger.error("No data fetched for the given parameters, try using max for period")
            raise DataFetchError(message="Data Frame is empty. No data fetched for the given parameters",
                                 ticker=ticker,
                                 period=period,
                                 interval=interval,
                                 start=start,
                                 end=end)
    
    except Exception as e:
        if not isinstance(e, DataFetchError):
            logger.error(f"Error fetching history data: {e}")
            raise DataFetchError(f"Failed to fetch history data: {e}")
        raise