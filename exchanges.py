import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_binance(symbol, fee_rate):
    url = "https://api.binance.com/api/v3/ticker/24hr"
    r = requests.get(url, params={"symbol": symbol}, timeout=10, verify=False)
    r.raise_for_status()
    d = r.json()
    price = float(d["lastPrice"])
    try:
        k = requests.get("https://api.binance.com/api/v3/klines",
                         params={"symbol": symbol, "interval": "1d", "limit": 7}, timeout=10, verify=False)
        k.raise_for_status()
        c = k.json()
        if len(c) >= 7:
            close_7d_ago = float(c[0][4])
            change_7d = (price - close_7d_ago) / close_7d_ago * 100
        else:
            change_7d = None
    except Exception:
        change_7d = None
    return {
        "price": price,
        "volume": float(d["quoteVolume"]),
        "change_24h": float(d["priceChangePercent"]),
        "high": float(d["highPrice"]),
        "low": float(d["lowPrice"]),
        "change_7d": change_7d,
        "buy_price_with_fee": price * (1 + fee_rate),
        "sell_price_with_fee": price * (1 - fee_rate),
    }

def fetch_okx(symbol, fee_rate):
    url = "https://www.okx.com/api/v5/market/ticker"
    r = requests.get(url, params={"instId": symbol}, timeout=10, verify=False)
    r.raise_for_status()
    t = r.json()["data"][0]
    price = float(t["last"])
    chg = 0.0
    if "open24h" in t:
        open24 = float(t["open24h"])
        if open24: chg = (price - open24) / open24 * 100
    vol = float(t.get("volCcy24h", 0)) or float(t["vol24h"]) * price
    try:
        k = requests.get("https://www.okx.com/api/v5/market/candles",
                         params={"instId": symbol, "bar": "1D", "limit": 7}, timeout=10, verify=False)
        k.raise_for_status()
        c = k.json()["data"]
        if len(c) >= 7:
            close_7d_ago = float(c[-1][4])
            change_7d = (price - close_7d_ago) / close_7d_ago * 100
        else:
            change_7d = None
    except Exception:
        change_7d = None
    return {
        "price": price,
        "volume": vol,
        "change_24h": chg,
        "high": float(t["high24h"]),
        "low": float(t["low24h"]),
        "change_7d": change_7d,
        "buy_price_with_fee": price * (1 + fee_rate),
        "sell_price_with_fee": price * (1 - fee_rate),
    }

def fetch_kraken(pair, fee_rate):
    url = "https://api.kraken.com/0/public/Ticker"
    r = requests.get(url, params={"pair": pair}, timeout=10, verify=False)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise ValueError(str(data["error"]))
    t = next(iter(data["result"].values()))
    price = float(t["c"][0])
    open24 = float(t["o"])
    chg = ((price - open24) / open24) * 100 if open24 else 0.0
    vol_btc = float(t["v"][1])
    change_7d = None
    return {
        "price": price,
        "volume": vol_btc * price,
        "change_24h": chg,
        "high": float(t["h"][1]),
        "low": float(t["l"][1]),
        "change_7d": change_7d,
        "buy_price_with_fee": price * (1 + fee_rate),
        "sell_price_with_fee": price * (1 - fee_rate),
    }

def fetch_kucoin(symbol, fee_rate):
    url = "https://api.kucoin.com/api/v1/market/stats"
    r = requests.get(url, params={"symbol": symbol}, timeout=10, verify=False)
    r.raise_for_status()
    resp = r.json()
    if resp.get("code") != "200000":
        raise ValueError(resp.get("msg", "KuCoin error"))
    d = resp["data"]
    price = float(d["last"])
    try:
        k = requests.get("https://api.kucoin.com/api/v1/market/candles",
                         params={"symbol": symbol, "type": "1day", "limit": 7}, timeout=10, verify=False)
        k.raise_for_status()
        c = k.json()["data"]
        if len(c) >= 7:
            close_7d_ago = float(c[-1][2])
            change_7d = (price - close_7d_ago) / close_7d_ago * 100
        else:
            change_7d = None
    except Exception:
        change_7d = None
    return {
        "price": price,
        "volume": float(d.get("volValue", 0)),
        "change_24h": float(d.get("changeRate", 0)) * 100,
        "high": float(d["high"]),
        "low": float(d["low"]),
        "change_7d": change_7d,
        "buy_price_with_fee": price * (1 + fee_rate),
        "sell_price_with_fee": price * (1 - fee_rate),
    }

def fetch_bybit(symbol, fee_rate):
    url = "https://api.bybit.com/v5/market/tickers"
    r = requests.get(url, params={"category": "spot", "symbol": symbol}, timeout=10, verify=False)
    r.raise_for_status()
    data = r.json()
    if data.get("retCode") != 0:
        raise ValueError(data.get("retMsg", "Bybit error"))
    result_list = data.get("result", {}).get("list", [])
    if not result_list:
        raise ValueError("Bybit returned empty list")
    d = result_list[0]
    price = float(d["lastPrice"])
    try:
        k = requests.get("https://api.bybit.com/v5/market/kline",
                         params={"category": "spot", "symbol": symbol, "interval": "D", "limit": 7}, timeout=10, verify=False)
        k.raise_for_status()
        c = k.json()["result"]["list"]
        if len(c) >= 7:
            close_7d_ago = float(c[-1][4])
            change_7d = (price - close_7d_ago) / close_7d_ago * 100
        else:
            change_7d = None
    except Exception:
        change_7d = None
    return {
        "price": price,
        "volume": float(d.get("turnover24h", 0)),
        "change_24h": float(d.get("price24hPcnt", 0)) * 100,
        "high": float(d["highPrice24h"]),
        "low": float(d["lowPrice24h"]),
        "change_7d": change_7d,
        "buy_price_with_fee": price * (1 + fee_rate),
        "sell_price_with_fee": price * (1 - fee_rate),
    }

def fetch_bitget(symbol, fee_rate):
    url = "https://api.bitget.com/api/v2/spot/market/tickers"
    r = requests.get(url, params={"symbol": symbol}, timeout=10, verify=False)
    r.raise_for_status()
    data = r.json()
    if data.get("code") != "00000":
        raise ValueError(data.get("msg", "Bitget error"))
    d = data["data"][0]
    price = float(d["lastPr"])
    try:
        k = requests.get("https://api.bitget.com/api/v2/spot/market/candles",
                         params={"symbol": symbol, "granularity": "1D", "limit": 7}, timeout=10, verify=False)
        k.raise_for_status()
        c = k.json()["data"]
        if len(c) >= 7:
            close_7d_ago = float(c[-1][4])
            change_7d = (price - close_7d_ago) / close_7d_ago * 100
        else:
            change_7d = None
    except Exception:
        change_7d = None
    return {
        "price": price,
        "volume": float(d.get("quoteVolume", 0)),
        "change_24h": float(d.get("change24h", 0)) * 100,
        "high": float(d["high24h"]),
        "low": float(d["low24h"]),
        "change_7d": change_7d,
        "buy_price_with_fee": price * (1 + fee_rate),
        "sell_price_with_fee": price * (1 - fee_rate),
    }

def fetch_gateio(pair, fee_rate):
    url = "https://api.gateio.ws/api/v4/spot/tickers"
    r = requests.get(url, params={"currency_pair": pair}, timeout=10, verify=False)
    r.raise_for_status()
    data = r.json()
    if not data:
        raise ValueError("Gate.io returned empty list")
    d = data[0]
    price = float(d["last"])
    try:
        k = requests.get("https://api.gateio.ws/api/v4/spot/candlesticks",
                         params={"currency_pair": pair, "interval": "1d", "limit": 7}, timeout=10, verify=False)
        k.raise_for_status()
        c = k.json()
        if len(c) >= 7:
            close_7d_ago = float(c[-1][2])
            change_7d = (price - close_7d_ago) / close_7d_ago * 100
        else:
            change_7d = None
    except Exception:
        change_7d = None
    return {
        "price": price,
        "volume": float(d["quote_volume"]),
        "change_24h": float(d["change_percentage"]),
        "high": float(d["high_24h"]),
        "low": float(d["low_24h"]),
        "change_7d": change_7d,
        "buy_price_with_fee": price * (1 + fee_rate),
        "sell_price_with_fee": price * (1 - fee_rate),
    }

def fetch_coinbase(symbol, fee_rate):
    url = f"https://api.exchange.coinbase.com/products/{symbol}/stats"
    r = requests.get(url, timeout=10, verify=False)
    r.raise_for_status()
    d = r.json()
    price = float(d["last"])
    open_ = float(d["open"])
    chg = (price - open_) / open_ * 100 if open_ else 0.0
    try:
        k = requests.get(f"https://api.exchange.coinbase.com/products/{symbol}/candles?granularity=86400",
                         timeout=10, verify=False)
        k.raise_for_status()
        c = k.json()
        if len(c) >= 7:
            close_7d_ago = float(c[-1][4])
            change_7d = (price - close_7d_ago) / close_7d_ago * 100
        else:
            change_7d = None
    except Exception:
        change_7d = None
    return {
        "price": price,
        "volume": float(d["volume"]) * price,
        "change_24h": chg,
        "high": float(d["high"]),
        "low": float(d["low"]),
        "change_7d": change_7d,
        "buy_price_with_fee": price * (1 + fee_rate),
        "sell_price_with_fee": price * (1 - fee_rate),
    }

def fetch_candles_binance(symbol, interval="1h", limit=168):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    r = requests.get(url, params=params, timeout=10, verify=False)
    r.raise_for_status()
    candles = r.json()
    return [
        {
            "time": c[0],
            "open": float(c[1]),
            "high": float(c[2]),
            "low": float(c[3]),
            "close": float(c[4]),
        }
        for c in candles
    ]