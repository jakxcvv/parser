import requests

def fetch_binance():
    url = "https://api.binance.com/api/v3/ticker/24hr"
    params = {"symbol": "BTCUSDT"}
    r = requests.get(url, params=params)
    return {
        "price":   float(r.json()["lastPrice"]),
        "volume":  float(r.json()["quoteVolume"]),
        "change":  float(r.json()["priceChangePercent"]),
        "high":    float(r.json()["highPrice"]),
        "low":     float(r.json()["lowPrice"]),
    }

def fetch_okx():
    url = "https://www.okx.com/api/v5/market/ticker"
    params = {"instId": "BTC-USDT"}
    r = requests.get(url, params=params)
    data = r.json()
    ticker = data["data"][0]
    last = float(ticker["last"])
    change_pct = 0.0
    if "open24h" in ticker:
        open24 = float(ticker["open24h"])
        if open24 != 0:
            change_pct = ((last - open24) / open24) * 100
    if "volCcy24h" in ticker:
        volume = float(ticker["volCcy24h"])
    else:
        volume_btc = float(ticker["vol24h"])
        volume = volume_btc * last
    return {
        "price":   last,
        "volume":  volume,
        "change":  change_pct,
        "high":    float(ticker["high24h"]),
        "low":     float(ticker["low24h"]),
    }

def fetch_kraken():
    url = "https://api.kraken.com/0/public/Ticker"
    params = {"pair": "XBTUSDT"}
    r = requests.get(url, params=params)
    data = r.json()
    ticker = data["result"]["XBTUSDT"]
    last = float(ticker["c"][0])
    open24 = float(ticker["o"])
    change_pct = ((last - open24) / open24) * 100 if open24 else 0
    volume_btc = float(ticker["v"][1])  
    volume_usdt = volume_btc * last
    return {
        "price":   last,
        "volume":  volume_usdt,
        "change":  change_pct,
        "high":    float(ticker["h"][1]),
        "low":     float(ticker["l"][1]),
    }

def fetch_kucoin():
    url = "https://api.kucoin.com/api/v1/market/stats"
    params = {"symbol": "BTC-USDT"}
    r = requests.get(url, params=params)
    data = r.json()
    d = data["data"]
    last = float(d["last"])
    change_pct = float(d["changeRate"]) * 100
    return {
        "price":   last,
        "volume":  float(d["volValue"]),  
        "change":  change_pct,
        "high":    float(d["high"]),
        "low":     float(d["low"]),
    }

EXCHANGES = [
    ("Binance", fetch_binance),
    ("OKX",     fetch_okx),
    ("Kraken",  fetch_kraken),
    ("KuCoin",  fetch_kucoin),
]

def main():
    header = f"{'Биржа':<10} {'Цена':>12} {'Объём(USDT)':>16} {'24ч%':>8} {'High':>12} {'Low':>12}"
    print(header)
    print("-" * len(header))

    for name, fetch_func in EXCHANGES:
        try:
            data = fetch_func()
            print(f"{name:<10} {data['price']:>12.2f} {data['volume']:>16.2f} {data['change']:>7.2f}% {data['high']:>12.2f} {data['low']:>12.2f}")
        except Exception as e:
            print(f"{name:<10} {'-- ОШИБКА --':>12} {str(e)[:60]}")

if __name__ == "__main__":
    main()