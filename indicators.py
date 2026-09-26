"""
Indicators: RSI, EMA, MACD - dhammaantood lagu dhisay pandas/numpy kaliya.
"""
import pandas as pd
import numpy as np

import config


def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def rsi(series: pd.Series, period: int = None) -> pd.Series:
    period = period or config.RSI_PERIOD
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi_val = 100 - (100 / (1 + rs))
    return rsi_val.fillna(50)


def macd(series: pd.Series, fast: int = None, slow: int = None, signal: int = None):
    fast = fast or config.EMA_FAST
    slow = slow or config.EMA_SLOW
    signal = signal or config.MACD_SIGNAL
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["rsi"] = rsi(df["close"])
    df["ema_fast"] = ema(df["close"], config.EMA_FAST)
    df["ema_slow"] = ema(df["close"], config.EMA_SLOW)
    macd_line, signal_line, hist = macd(df["close"])
    df["macd"] = macd_line
    df["macd_signal"] = signal_line
    df["macd_hist"] = hist
    return df
