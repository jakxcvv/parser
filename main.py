import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


PRIORITY_EXCHANGE = "Binance"


COINS_USDT = {                 
    "Bitcoin":  "BTCUSDT",
    "Ethereum": "ETHUSDT",
    "Solana":   "SOLUSDT",
    "XRP":      "XRPUSDT",
    "BNB":      "BNBUSDT",
    "Dogecoin": "DOGEUSDT",
}

COINS_DASH = {               
    "Bitcoin":  "BTC-USDT",
    "Ethereum": "ETH-USDT",
    "Solana":   "SOL-USDT",
    "XRP":      "XRP-USDT",
    "BNB":      "BNB-USDT",
    "Dogecoin": "DOGE-USDT",
}

COINS_KRAKEN = {                 
    "Bitcoin":  "XBTUSDT",
    "Ethereum": "ETHUSDT",
    "Solana":   "SOLUSDT",
    "XRP":      "XRPUSDT",
    "BNB":      "BNBUSDT",
    "Dogecoin": "XDGUSDT",
}

COINS_GATEIO = {              
    "Bitcoin":  "BTC_USDT",
    "Ethereum": "ETH_USDT",
    "Solana":   "SOL_USDT",
    "XRP":      "XRP_USDT",
    "BNB":      "BNB_USDT",
    "Dogecoin": "DOGE_USDT",
}

COINS_COINBASE = {               
    "Bitcoin":  "BTC-USD",        
    "Ethereum": "ETH-USD",
    "Solana":   "SOL-USD",
    "XRP":      "XRP-USD",
    "Dogecoin": "DOGE-USD",
}

def fetch_binance(symbol):
    url = "https://api.binance.com/api/v3/ticker/24hr"
    r = requests.get(url, params={"symbol": symbol}, timeout=10)
    r.raise_for_status()
    d = r.json()
    return {
        "price":   float(d["lastPrice"]),
        "volume":  float(d["quoteVolume"]),
        "change":  float(d["priceChangePercent"]),
        "high":    float(d["highPrice"]),
        "low":     float(d["lowPrice"]),
    }


def fetch_okx(symbol):
    url = "https://www.okx.com/api/v5/market/ticker"
    r = requests.get(url, params={"instId": symbol}, timeout=10)
    r.raise_for_status()
    ticker = r.json()["data"][0]
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


def fetch_kraken(pair):
    url = "https://api.kraken.com/0/public/Ticker"
    r = requests.get(url, params={"pair": pair}, timeout=10)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise ValueError(data["error"])
    ticker = next(iter(data["result"].values()))
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


def fetch_kucoin(symbol):
    url = "https://api.kucoin.com/api/v1/market/stats"
    r = requests.get(url, params={"symbol": symbol}, timeout=10)
    r.raise_for_status()
    d = r.json()["data"]
    return {
        "price":   float(d["last"]),
        "volume":  float(d["volValue"]),
        "change":  float(d["changeRate"]) * 100,
        "high":    float(d["high"]),
        "low":     float(d["low"]),
    }


def fetch_bybit(symbol):
    url = "https://api.bybit.com/v5/market/tickers"
    r = requests.get(url, params={"category": "spot", "symbol": symbol}, timeout=10)
    r.raise_for_status()
    d = r.json()["result"]["list"][0]
    return {
        "price":   float(d["lastPrice"]),
        "volume":  float(d["turnover24h"]),
        "change":  float(d["price24hPcnt"]) * 100, 
        "high":    float(d["highPrice24h"]),
        "low":     float(d["lowPrice24h"]),
    }


def fetch_bitget(symbol):
    url = "https://api.bitget.com/api/v2/spot/market/tickers"
    r = requests.get(url, params={"symbol": symbol}, timeout=10)
    r.raise_for_status()
    d = r.json()["data"][0]
    return {
        "price":   float(d["lastPr"]),
        "volume":  float(d["quoteVolume"]),
        "change":  float(d["change24h"]) * 100,   
        "high":    float(d["high24h"]),
        "low":     float(d["low24h"]),
    }


def fetch_gateio(pair):
    url = "https://api.gateio.ws/api/v4/spot/tickers"
    r = requests.get(url, params={"currency_pair": pair}, timeout=10)
    r.raise_for_status()
    d = r.json()[0]
    return {
        "price":   float(d["last"]),
        "volume":  float(d["quote_volume"]),
        "change":  float(d["change_percentage"]), 
        "high":    float(d["high_24h"]),
        "low":     float(d["low_24h"]),
    }


def fetch_coinbase(symbol):
    url = f"https://api.exchange.coinbase.com/products/{symbol}/stats"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    d = r.json()
    last = float(d["last"])
    open_ = float(d["open"])
    volume_base = float(d["volume"])            
    change_pct = (last - open_) / open_ * 100 if open_ else 0
    return {
        "price":   last,
        "volume":  volume_base * last,         
        "change":  change_pct,
        "high":    float(d["high"]),
        "low":     float(d["low"]),
    }



EXCHANGES = [
    ("Binance",  fetch_binance,  COINS_USDT),
    ("OKX",      fetch_okx,      COINS_DASH),
    ("Kraken",   fetch_kraken,   COINS_KRAKEN),
    ("KuCoin",   fetch_kucoin,   COINS_DASH),
    ("Bybit",    fetch_bybit,    COINS_USDT),
    ("Bitget",   fetch_bitget,   COINS_USDT),
    ("Gate.io",  fetch_gateio,   COINS_GATEIO),
    ("Coinbase", fetch_coinbase, COINS_COINBASE),
]


def fetch_all_parallel():
    tasks = []
    for exchange_name, fetch_func, coins in EXCHANGES:
        for coin_name, symbol in coins.items():
            tasks.append((exchange_name, coin_name, fetch_func, symbol))

    results = {}
    with ThreadPoolExecutor(max_workers=len(tasks)) as pool:
        future_to_task = {
            pool.submit(fetch_func, symbol): (exchange_name, coin_name)
            for exchange_name, coin_name, fetch_func, symbol in tasks
        }
        for future in as_completed(future_to_task):
            key = future_to_task[future]
            try:
                results[key] = future.result()
            except Exception as e:
                results[key] = e   

    return results


def main():
    results = fetch_all_parallel()

    header = (
        f"{'Биржа':<10}{'Монета':<10}{'Цена':>14}"
        f"{'Объём(USDT)':>18}{'24ч%':>9}{'High':>14}{'Low':>14}"
        f"{'Δ vs ' + PRIORITY_EXCHANGE:>16}"
    )
    print(header)
    print("-" * len(header))

    for exchange_name, fetch_func, coins in EXCHANGES:
        for coin_name, symbol in coins.items():
            data = results[(exchange_name, coin_name)]

            if isinstance(data, Exception):
                print(f"{exchange_name:<10}{coin_name:<10}{'-- ОШИБКА --':>14}  {str(data)[:60]}")
                continue

            anchor = results.get((PRIORITY_EXCHANGE, coin_name))
            if exchange_name == PRIORITY_EXCHANGE:
                deviation_str = "(якорь)"
            elif isinstance(anchor, dict) and anchor.get("price"):
                deviation_pct = (data["price"] - anchor["price"]) / anchor["price"] * 100
                deviation_str = f"{deviation_pct:+.3f}%"
            else:
                deviation_str = "n/a"

            print(
                f"{exchange_name:<10}{coin_name:<10}"
                f"{data['price']:>14.2f}{data['volume']:>18.2f}"
                f"{data['change']:>8.2f}%{data['high']:>14.2f}{data['low']:>14.2f}"
                f"{deviation_str:>16}"
            )


if __name__ == "__main__":
    main()