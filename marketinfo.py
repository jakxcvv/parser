import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

COIN_IDS = {
    "Bitcoin": "bitcoin", "Ethereum": "ethereum", "Solana": "solana",
    "XRP": "ripple", "BNB": "binancecoin", "Dogecoin": "dogecoin",
    "Cardano": "cardano", "Avalanche": "avalanche-2", "Polkadot": "polkadot",
    "Polygon": "matic-network", "Chainlink": "chainlink", "Uniswap": "uniswap",
    "Shiba Inu": "shiba-inu", "Litecoin": "litecoin", "Tron": "tron",
    "Toncoin": "the-open-network", "Cosmos": "cosmos", "Filecoin": "filecoin",
    "Aave": "aave", "Algorand": "algorand", "The Graph": "the-graph",
    "Stacks": "stacks", "Maker": "maker", "Injective": "injective-protocol",
    "Render": "render-token", "Optimism": "optimism", "Arbitrum": "arbitrum",
    "Sui": "sui", "Sei": "sei-network", "Aptos": "aptos",
    "Near Protocol": "near", "Flow": "flow", "Quant": "quant-network",
    "Theta Network": "theta-token", "MultiversX": "multiversx-egld",
    "Tezos": "tezos", "Neo": "neo", "Zcash": "zcash",
    "Chiliz": "chiliz", "Mina": "mina-protocol",
}

def get_market_info(coin_name):
    coin_id = COIN_IDS.get(coin_name)
    if not coin_id:
        return None
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}?localization=false&tickers=false&community_data=false&developer_data=false&sparkline=false"
    try:
        r = requests.get(url, timeout=15, verify=False)
        r.raise_for_status()
        data = r.json()
        market = data.get("market_data", {})
        return {
            "market_cap": market.get("market_cap", {}).get("usd"),
            "market_cap_rank": market.get("market_cap_rank"),
            "total_volume": market.get("total_volume", {}).get("usd"),
            "high_24h": market.get("high_24h", {}).get("usd"),
            "low_24h": market.get("low_24h", {}).get("usd"),
            "price_change_percentage_7d": market.get("price_change_percentage_7d"),
            "circulating_supply": market.get("circulating_supply"),
        }
    except Exception as e:
        print(f"CoinGecko error for {coin_name}: {e}")
        return None