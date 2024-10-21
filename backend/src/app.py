from datetime import datetime, timedelta

from api import fetch

one_week_back = (datetime.now() - timedelta(weeks=1)).strftime('%d %b %Y')

print(fetch("BTCUSDT", "1d", one_week_back))