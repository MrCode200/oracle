import requests
import os

api_key: str = os.getenv("NOBITEX_API_KEY")

# هدرهای درخواست
headers = {
    "Authorization": f"Token {api_key}"
}

# ارسال درخواست GET

def get_wallet(ticker: str | None = None,):
    url = "https://api.nobitex.ir/users/wallets/list"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Parse JSON response
        data = response.json()

        # Check if the response status is "ok"
        if data.get("status") == "ok":
            wallets = data.get("wallets", [])

            # Create a dictionary of wallets
            wallets_dict = {}
            for wallet in wallets:
                currency = wallet.get("currency", "Unknown")
                wallets_dict[currency] = {
                    "balance": wallet.get("balance", "0"),
                    "active_balance": wallet.get("activeBalance", "0"),
                    "deposit_address": wallet.get("depositAddress", "N/A"),
                }
            return wallets_dict
        else:
            print("Error: Response status is not 'ok'.")
            return {}
    else:
        print(f"Error {response.status_code}: {response.text}")
        return {}

    # Call the function and print the result


wallets_dict = get_wallet()
print(wallets_dict)

