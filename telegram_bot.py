"""
Telegram Bot: /start, /stop, /settings (market + interval), /signals.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

import config
import storage


WELCOME_MSG = (
    "🤖 Ku soo dhawoow Signal Bot!\n\n"
    "Waxaan ku diri doonaa signals BUY/SELL — Forex iyo Crypto.\n\n"
    "Isticmaal /settings si aad u doorato suuqa iyo interval-ka.\n"
    "/signals - Arag 5-tii signal ee ugu dambeeyay\n"
    "/stop - Ka bax wargelinta\n"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    storage.add_subscriber(update.effective_chat.id)
    await update.message.reply_text(WELCOME_MSG)


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    storage.remove_subscriber(update.effective_chat.id)
    await update.message.reply_text("Waad ka baxday wargelinta. /start si aad mar kale u soo biirto.")


def format_signal_message(s: dict) -> str:
    emoji = "🟢" if s["action"] == "BUY" else "🔴" if s["action"] == "SELL" else "⚪"
    reasons = "\n  • " + "\n  • ".join(s["reasons"])
    return (
        f"{emoji} {s['action']} - {s['symbol']}\n"
        f"Qiimaha: {s['price']}\n"
        f"Confidence: {s['confidence']}%\n"
        f"RSI: {s['rsi']} | MACD hist: {s['macd_hist']}\n"
        f"Sababaha:{reasons}"
    )


async def signals_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    recent = storage.get_recent_signals(limit=5)
    if not recent:
        await update.message.reply_text("Weli ma jiraan signals la diiwaan geliyay.")
        return
    for s in recent:
        await update.message.reply_text(format_signal_message(s))


def _settings_text(chat_id: int) -> str:
    s = storage.get_settings(chat_id)
    return (
        "⚙️ Settings-kaaga:\n\n"
        f"Suuq: {config.MARKET_LABELS[s['market']]}\n"
        f"Interval: {s['interval_minutes']} daqiiqo\n\n"
        "Dooro maxaad rabto inaad bedesho:"
    )


def _main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌍 Suuqa", callback_data="menu:market")],
        [InlineKeyboardButton("⏱ Interval-ka", callback_data="menu:interval")],
        [InlineKeyboardButton("✅ Dhammee", callback_data="menu:done")],
    ])


async def settings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    storage.add_subscriber(chat_id)
    await update.message.reply_text(_settings_text(chat_id), reply_markup=_main_kb())


def _market_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(config.MARKET_LABELS[m], callback_data=f"market:{m}")] for m in config.AVAILABLE_MARKETS]
        + [[InlineKeyboardButton("« Dib u noqo", callback_data="menu:back")]]
    )


def _interval_kb() -> InlineKeyboardMarkup:
    rows, row = [], []
    for i in config.AVAILABLE_INTERVALS:
        row.append(InlineKeyboardButton(f"{i} daq", callback_data=f"interval:{i}"))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton("« Dib u noqo", callback_data="menu:back")])
    return InlineKeyboardMarkup(rows)


async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat_id
    data = query.data
    await query.answer()

    if data == "menu:back":
        await query.edit_message_text(_settings_text(chat_id), reply_markup=_main_kb())
    elif data == "menu:done":
        await query.edit_message_text("✅ Settings waa la kaydiyay.")
    elif data == "menu:market":
        await query.edit_message_text("🌍 Dooro suuqa:", reply_markup=_market_kb())
    elif data == "menu:interval":
        await query.edit_message_text("⏱ Dooro interval-ka:", reply_markup=_interval_kb())
    elif data.startswith("market:"):
        storage.update_settings(chat_id, market=data.split(":", 1)[1])
        await query.edit_message_text(_settings_text(chat_id), reply_markup=_main_kb())
    elif data.startswith("interval:"):
        storage.update_settings(chat_id, interval_minutes=int(data.split(":", 1)[1]))
        await query.edit_message_text(_settings_text(chat_id), reply_markup=_main_kb())


def build_app() -> Application:
    app = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("signals", signals_cmd))
    app.add_handler(CommandHandler("settings", settings_cmd))
    app.add_handler(CallbackQueryHandler(on_button))
    return app


def _signal_matches(signal: dict, settings: dict) -> bool:
    if settings["market"] == "both":
        return True
    market_symbols = config.symbols_for_market(settings["market"])
    return signal["symbol"] in market_symbols


async def broadcast_signals(app: Application, all_signals: list):
    if not all_signals:
        return
    for chat_id in storage.load_subscribers():
        settings = storage.get_settings(chat_id)
        if not storage.due_for_check(chat_id):
            continue
        matching = [s for s in all_signals if _signal_matches(s, settings)]
        if not matching:
            continue
        for s in matching:
            try:
                await app.bot.send_message(chat_id=chat_id, text=format_signal_message(s))
            except Exception as e:
                print(f"[telegram_bot] Khalad u dirid {chat_id}: {e}")
        storage.mark_sent(chat_id)
