import requests
import time

def fetch_market_chart(coin_id: str, days_ago: str, interval: str = "daily", precision: str = "10", currency: str = 'usd') -> dict[str, list[list[int]]]:
    url: str = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params: dict[str, str] = {
        'vs_currency' : currency,
        'days' : days_ago,
        'interval' : interval,
        'precision' : precision
    }

    response = requests.get(url, params)

    if response.status_code == 200:
        data = response.json()
        return data
    elif response.status_code == 429:
        print("Rate limit exceeded. Waiting for 1 minute...")
        for sec in range(60):
            print(f"{60 - sec} Remaining...", end='\r', flush=True)
            time.sleep(1)
        print("Rate limit refreshed!            ")
        time.sleep(1)

        return 429
    else:
        print(f"Error fetching data: {response.status_code}")
        return None