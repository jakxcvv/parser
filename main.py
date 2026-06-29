import requests
import time

urls = [
    "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT",
    "https://api.binance.com/api/v3/ticker/24hr?symbol=ETHUSDT",
    "https://api.binance.com/api/v3/ticker/24hr?symbol=SOLUSDT",
]

def fetch(url):
    resp = requests.get(url, timeout=10)
    return resp.json()["lastPrice"]

start = time.time()
prices = [fetch(url) for url in urls]
print(prices)