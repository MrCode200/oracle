from time import timezone
from typing import Optional
import time
from requests import Response, get
from datetime import datetime, timezone
from tzlocal import get_localzone

from pandas import DataFrame, to_datetime, concat
from dateutil.relativedelta import relativedelta

from src.api.utils import handle_binance_status

url_fetch_ticker_price: str = "https://api.binance.com/api/v3/ticker/price"
url_fetch_klines: str = "https://api.binance.com/api/v3/klines"
url_fetch_exchange_info: str = "https://api.binance.com/api/v3/exchangeInfo"

unix_utc_offset: int = int(datetime.now(get_localzone()).utcoffset().total_seconds()) * 1000


columns = [
    'OpenTime',
    'Open',
    'High',
    'Low',
    'Close',
    'Volume',
    'CloseTime',
    'QuoteAssetVolume',
    'NumberOfTrades',
    'TakerBuyBaseAssetVolume',
    'TakerBuyQuoteAssetVolume',
    'unused'
]


def fetch_ticker_price(ticker) -> float:
    param: dict = {
        'symbol': ticker
    }
    response: Response = get(url_fetch_ticker_price, params=param)
    data: dict = response.json()

    handle_binance_status(response.status_code, data)

    return float(data["price"])


def fetch_exchange_info(tickers: Optional[list[str]] = None) -> dict:
    response: Response = get(url_fetch_exchange_info)

    data: dict = response.json()

    handle_binance_status(response.status_code, data)

    return data

# TODO: change from adding relative time to setting relative time
def fetch_klines(
        ticker: str,
        interval: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
        years: float = 0,
        months: float = 0,
        weeks: float = 0,
        days: float = 0,
        hours: float = 0,
        minutes: float = 0,
        seconds: float = 0,
        max_klines: Optional[int] = None,
        is_utc_time: bool = False
):
    """
    Retrieves klines from Binance

    :param ticker: The ticker of the asset
    :param interval: The interval of the klines ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
    :param start: The start time in the format 'YYYY-MM-DD HH:MM:SS'
    :param end: The end time in the format 'YYYY-MM-DD HH:MM:SS'
    :param years: The number of years to go back or forth
    :param months: The number of months to go back or forth
    :param weeks: The number of weeks to go back or forth
    :param days: The number of days to go back or forth
    :param hours: The number of hours to go back or forth
    :param minutes: The number of minutes to go back or forth
    :param seconds: The number of seconds to go back or forth
    :param max_klines: The maximum number of klines to retrieve
    :param is_utc_time: Whether the given end and start times are given in UTC
    :return: DataFrame
    """
    # After finding if relative time was used, subtract one due to it adding +x relative time but not setting the limit to x relative time
    uses_relative_time: bool = any(v != 0 for v in [years, months, weeks, days, hours, minutes, seconds])

    time_format = "%Y-%m-%d %H:%M:%S"

    if end is not None:
        end_timestamp: datetime = datetime.strptime(end, time_format)
    else:
        end_timestamp: datetime = datetime.now(timezone.utc)

    if start is not None:
        start_timestamp: datetime = datetime.strptime(start, time_format)
    else:
        start_timestamp: datetime = end_timestamp - relativedelta(
            years=years,
            months=months,
            weeks=weeks,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds
        )

    if start is not None and uses_relative_time:
        end_timestamp = start_timestamp + relativedelta(
            years=years,
            months=months,
            weeks=weeks,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds
        )

    if is_utc_time:
        # Assume `start_timestamp` and `end_timestamp` are in local time and need adjustment
        start_timestamp = start_timestamp.replace(tzinfo=timezone.utc)
        end_timestamp = end_timestamp.replace(tzinfo=timezone.utc)

    # Convert to UNIX timestamp
    start_timestamp: int = int(time.mktime(start_timestamp.timetuple())) * 1000
    end_timestamp: int = int(time.mktime(end_timestamp.timetuple())) * 1000

    if is_utc_time:
        start_timestamp += unix_utc_offset
        end_timestamp += unix_utc_offset

    df: DataFrame = DataFrame(columns=columns)
    limit: int = 1000

    while end_timestamp > start_timestamp:
        if max_klines is not None:
            if max_klines == len(df):
                break
            else:
                limit = min(1000, max_klines - len(df))

        params: dict = {
            'symbol': ticker,
            'interval': interval,
            'startTime': start_timestamp,
            'endTime': end_timestamp,
            'limit': limit
        }

        response: Response = get(url_fetch_klines, params=params)

        data = response.json()

        handle_binance_status(response.status_code, data)


        if len(data) == 0:
            break

        new_df: DataFrame = DataFrame(data, columns=columns)

        new_df["timestamp"] = to_datetime(new_df["OpenTime"], unit="ms", utc=True)
        new_df.set_index("timestamp", inplace=True)

        if df.empty:
            df = new_df
        else:
            df = concat([df, new_df])

        # +1 to start the next request just after the current one ends.
        start_timestamp = data[-1][6] + 1

    df.drop("unused", axis=1, inplace=True)

    for column in df.columns:
        df[column] = df[column].astype(float)

    return df

if __name__ == '__main__':
    df = fetch_klines("BTCUSDT", "1h", start="2022-03-03 00:00:00", end="2022-03-05 08:00:00")
    i = len(df) - 1
    print(str(df.index[i])[:-6])
    data = fetch_klines(
                    "BTCUSDT",
                    "1h",
                    start=str(df.index[i])[:-6],
                    max_klines=1,
                    is_utc_time=True
                )['Close']
    print("-----------------------")
    print(data)