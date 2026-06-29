import concurrent.futures
import time

def fetch_all_parallel(exchange_configs):
    tasks = []
    for name, func, coins, fee in exchange_configs:
        for coin_name, symbol in coins.items():
            tasks.append((name, coin_name, func, symbol, fee))

    results = {}
    # Ограничиваем число одновременных запросов, чтобы не получать 429
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        future_to_key = {}
        for name, coin_name, func, symbol, fee in tasks:
            future = pool.submit(func, symbol, fee)
            future_to_key[future] = (name, coin_name)
            time.sleep(0.05)  # маленькая задержка между отправкой задач

        for future in concurrent.futures.as_completed(future_to_key):
            key = future_to_key[future]
            try:
                results[key] = future.result()
            except Exception as e:
                results[key] = e
    return results