import requests


def fetch_market_chart(ID: str, days_ago: str, interval: str = "daily", precision: str = "10", currency: str = 'usd'):
    url = f"https://api.coingecko.com/api/v3/coins/{ID}/market_chart"
    params = {
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
        """print("Rate limit exceeded. Waiting for 1 minute...")
        for sec in range(60):
            print(f"{60 - sec} Remaining...", end='\r', flush=True)
            time.sleep(1)
        print("Rate limit refreshed!            ")
        time.sleep(1)"""

        return 429
    else:
        print(f"Error fetching data: {response.status_code}")
        return None