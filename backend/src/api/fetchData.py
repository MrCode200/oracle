import logging

import yfinance as yf  # type: ignore
from pandas import DataFrame

logger = logging.getLogger("oracle.app")

def fetch_historical_data(ticker: str, period: str, interval: str = "1d") -> DataFrame:
    """
    Fetch historical market chart data from Yahoo Finance using yfinance.

    :param ticker: The ticker symbol of the coin (e.g., 'BTC-USD' for Bitcoin)
    :param days: Number of days of historical data to fetch
    :param interval: The time interval for each data point (default: '1d')
    :return: A DataFrame containing the fetched market chart data or None on error
    """
    try:
        # Fetch historical market data as pandas DataFrame
        data_frame = yf.Ticker(ticker).history(period=period, interval=interval)

        if not data_frame.empty:
            logger.info(f"Fetched Data: {ticker = }; {period = }; {interval = };")
            return data_frame
        else:
            logger.error("No data fetched for the given parameters.")
            return None
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return None

if __name__ == '__main__':
    data_frame = fetch_historical_data("GOOG", '1mo', "1h")
    print(data_frame.iloc[-1])
    #print(dir(yf))
