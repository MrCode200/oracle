import logging
import requests
import time

logger = logging.getLogger("oracle.app")  # Correct logger import

def fetch_market_chart(coin_id: str, days_ago: str, interval: str = "daily", precision: str = "10",
                       currency: str = 'usd') -> dict[str, list[list[int]]]:
    """
    Fetch market chart data from the geckocoin api.
    On specific status error 429 it stops for 30 seconds and then returns None

    :param coin_id: The unique identifier of the coin
    :param days_ago: Number of days ago to fetch data from
    :key interval: The time interval for each data point (default: 10)
    :key precision: The max number of decimal points fo each data point (default: 10)
    :key currency: The value of each coin in the given currency (default: 'usd')
    :return: A dictionary containing the fetched market chart data.
    """
    url: str = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params: dict[str, str] = {
        'vs_currency': currency,
        'days': days_ago,
        'interval': interval,
        'precision': precision
    }

    response = requests.get(url, params)

    if response.status_code == 200:
        data = response.json()
        logger.info(f"Fetched Data: coin_id = {coin_id}; days_ago = {days_ago}; interval = {interval}; precision = {precision}; currency = {currency}")
        return data
    elif response.status_code == 429:
        logger.warning(f"Request limit reached, waiting 30 seconds")
        for sec in range(30):
            print(f"{30 - sec} Remaining...", end='\r', flush=True)
            time.sleep(1)
        print("Rate limit refreshed!            ")
        time.sleep(1)

        return 429
    else:
        logger.error(f"Error fetching data: {response.status_code}")  # Use error() instead of ERROR()
        return None