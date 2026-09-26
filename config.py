"""
Config-ka Signal Bot v2 - loo diyaariyay Render.com.

Buuxi TELEGRAM_BOT_TOKEN iyo TWELVEDATA_API_KEY sida "Environment Variables"
Render dashboard-kiisa (ma aha .env file, taasi waa kaliya tijaabo local ah).
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ---------- TELEGRAM ----------
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "PUT_YOUR_TELEGRAM_BOT_TOKEN_HERE")

# ---------- CRYPTO (via ccxt / Binance public API - ma baahna key) ----------
CRYPTO_EXCHANGE = "binance"
CRYPTO_SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"]
CRYPTO_TIMEFRAME = "15m"

# ---------- FOREX (via TwelveData) ----------
TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY", "PUT_YOUR_TWELVEDATA_API_KEY_HERE")
TWELVEDATA_INTERVAL = "15min"
FOREX_SYMBOLS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD",
    "USD/CAD", "EUR/JPY", "EUR/GBP",
]

MARKET_LABELS = {"forex": "Forex", "crypto": "Crypto", "both": "Labadaba"}
AVAILABLE_MARKETS = ["forex", "crypto", "both"]
DEFAULT_USER_MARKET = "both"


def symbols_for_market(market: str) -> list:
    if market == "forex":
        return list(FOREX_SYMBOLS)
    if market == "crypto":
        return list(CRYPTO_SYMBOLS)
    return list(FOREX_SYMBOLS) + list(CRYPTO_SYMBOLS)


def source_for_symbol(symbol: str) -> str:
    return "ccxt" if symbol in CRYPTO_SYMBOLS else "twelvedata"


# ---------- STRATEGY (RSI + EMA + MACD) ----------
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
EMA_FAST = 12
EMA_SLOW = 26
MACD_SIGNAL = 9

# ---------- SCHEDULER ----------
CHECK_INTERVAL_MINUTES = 5
AVAILABLE_INTERVALS = [5, 15, 30, 60, 120]
DEFAULT_USER_INTERVAL = 15

# ---------- WEB SERVER ----------
DASHBOARD_HOST = "0.0.0.0"
DASHBOARD_PORT = int(os.getenv("PORT", 5000))

# ---------- DATA STORAGE ----------
SIGNALS_LOG_FILE = os.path.join(os.path.dirname(__file__), "signals_log.json")
SUBSCRIBERS_FILE = os.path.join(os.path.dirname(__file__), "subscribers.json")
