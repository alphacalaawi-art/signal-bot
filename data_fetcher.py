"""
Data Fetcher: crypto via ccxt (Binance), forex via TwelveData.
"""
import pandas as pd
import requests
import ccxt

import config


def get_crypto_ohlcv(symbol: str, limit: int = 100) -> pd.DataFrame:
    exchange_class = getattr(ccxt, config.CRYPTO_EXCHANGE)
    exchange = exchange_class({"enableRateLimit": True})
    raw = exchange.fetch_ohlcv(symbol, timeframe=config.CRYPTO_TIMEFRAME, limit=limit)
    df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df


def get_forex_ohlcv(symbol: str, outputsize: int = 100) -> pd.DataFrame:
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": symbol,
        "interval": config.TWELVEDATA_INTERVAL,
        "outputsize": outputsize,
        "apikey": config.TWELVEDATA_API_KEY,
    }
    resp = requests.get(url, params=params, timeout=15)
    data = resp.json()
    if "values" not in data:
        raise RuntimeError(f"TwelveData error for {symbol}: {data}")
    df = pd.DataFrame(data["values"]).rename(columns={"datetime": "timestamp"})
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    for col in ["open", "high", "low", "close"]:
        df[col] = df[col].astype(float)
    return df.sort_values("timestamp").reset_index(drop=True)


def fetch_by_symbol(symbol: str, limit: int = 100) -> pd.DataFrame:
    if config.source_for_symbol(symbol) == "ccxt":
        df = get_crypto_ohlcv(symbol, limit=limit)
    else:
        df = get_forex_ohlcv(symbol, outputsize=limit)
    df["symbol"] = symbol
    return df


def fetch_all(symbols) -> dict:
    out = {}
    for sym in symbols:
        try:
            out[sym] = fetch_by_symbol(sym)
        except Exception as e:
            print(f"[data_fetcher] Khalad {sym}: {e}")
    return out
