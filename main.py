"""
Main: wadaha dashboard-ka (Flask) iyo Telegram bot-ka hal process ah - waa
lama huraan Render free tier maadaama uu kaliya bixiyo hal "Web Service".
"""
import asyncio
import threading
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

import config
import data_fetcher
import signal_engine
import storage
import telegram_bot
import dashboard


def run_dashboard_in_thread():
    t = threading.Thread(
        target=lambda: dashboard.app.run(
            host=config.DASHBOARD_HOST, port=config.DASHBOARD_PORT, debug=False, use_reloader=False
        ),
        daemon=True,
    )
    t.start()
    print(f"Dashboard wuu socdaa: {config.DASHBOARD_HOST}:{config.DASHBOARD_PORT}")


def get_active_symbols() -> set:
    active = set()
    for chat_id in storage.load_subscribers():
        s = storage.get_settings(chat_id)
        active.update(config.symbols_for_market(s["market"]))
    if not active:
        active.update(config.symbols_for_market("both"))
    return active


async def check_markets_job(tg_app):
    active = get_active_symbols()
    print(f"[{datetime.now().isoformat()}] Hubinta {len(active)} symbol...")
    all_data = data_fetcher.fetch_all(active)
    results = signal_engine.evaluate_many(all_data)
    actionable = [r for r in results if r["action"] in ("BUY", "SELL")]
    if actionable:
        storage.append_signals(actionable)
        print(f"  -> {len(actionable)} signal cusub")
        await telegram_bot.broadcast_signals(tg_app, actionable)
    else:
        print("  -> Signal cusub lama helin")


async def main_async():
    run_dashboard_in_thread()
    tg_app = telegram_bot.build_app()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        check_markets_job, "interval",
        minutes=config.CHECK_INTERVAL_MINUTES, args=[tg_app],
        next_run_time=datetime.now(),
    )
    scheduler.start()

    print("Nidaamka Signal Bot v2 wuu shaqeynayaa.")
    async with tg_app:
        await tg_app.start()
        await tg_app.updater.start_polling()
        try:
            await asyncio.Event().wait()
        finally:
            await tg_app.updater.stop()
            await tg_app.stop()


if __name__ == "__main__":
    asyncio.run(main_async())
