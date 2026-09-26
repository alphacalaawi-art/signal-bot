"""
Signal Engine: RSI + EMA crossover + MACD -> BUY / SELL / HOLD + confidence.

  BUY  -> EMA fast > EMA slow (uptrend) AND RSI < overbought AND MACD hist > 0
  SELL -> EMA fast < EMA slow (downtrend) AND RSI > oversold AND MACD hist < 0
  HOLD -> haddii kale
"""
from datetime import datetime, timezone

import config
from indicators import add_all_indicators


def evaluate(df) -> dict:
    df = add_all_indicators(df)
    last = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else last

    ema_bullish = last["ema_fast"] > last["ema_slow"]
    ema_bearish = last["ema_fast"] < last["ema_slow"]
    macd_cross_up = prev["macd_hist"] <= 0 and last["macd_hist"] > 0
    macd_cross_down = prev["macd_hist"] >= 0 and last["macd_hist"] < 0

    action = "HOLD"
    reasons = []
    score = 0

    if ema_bullish and last["rsi"] < config.RSI_OVERBOUGHT and last["macd_hist"] > 0:
        action = "BUY"
        score += 40
        reasons.append("EMA fast > EMA slow (uptrend)")
        if last["rsi"] < 50:
            score += 15
            reasons.append(f"RSI={last['rsi']:.1f} (weli ma gaarin overbought)")
        if macd_cross_up:
            score += 30
            reasons.append("MACD hist bullish cross")
        score += 15

    elif ema_bearish and last["rsi"] > config.RSI_OVERSOLD and last["macd_hist"] < 0:
        action = "SELL"
        score += 40
        reasons.append("EMA fast < EMA slow (downtrend)")
        if last["rsi"] > 50:
            score += 15
            reasons.append(f"RSI={last['rsi']:.1f} (weli ma gaarin oversold)")
        if macd_cross_down:
            score += 30
            reasons.append("MACD hist bearish cross")
        score += 15
    else:
        reasons.append("Shuruudaha BUY/SELL lama buuxin - suuqu wuu jilicsanyahay")

    return {
        "symbol": last.get("symbol", "UNKNOWN"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "price": round(float(last["close"]), 6),
        "action": action,
        "confidence": min(score, 100),
        "rsi": round(float(last["rsi"]), 2),
        "macd_hist": round(float(last["macd_hist"]), 6),
        "reasons": reasons,
    }


def evaluate_many(symbol_to_df: dict) -> list:
    results = []
    for symbol, df in symbol_to_df.items():
        try:
            if len(df) < max(config.EMA_SLOW, config.RSI_PERIOD) + 2:
                continue
            df = df.copy()
            df["symbol"] = symbol
            results.append(evaluate(df))
        except Exception as e:
            print(f"[signal_engine] Khalad {symbol}: {e}")
    return results
