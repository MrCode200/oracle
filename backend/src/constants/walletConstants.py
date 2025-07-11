from src.api import fetch_exchange_info

VALID_TICKERS: list[str] = [ticker["symbol"] for ticker in fetch_exchange_info()["symbols"] if ticker["quoteAsset"].endswith("EUR")]
