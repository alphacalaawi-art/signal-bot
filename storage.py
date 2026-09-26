"""
Storage fudud oo JSON ku salaysan.
"""
import json
import os
from datetime import datetime, timezone

import config


def _load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ---------- SIGNALS LOG ----------
def append_signals(signals: list):
    log = _load_json(config.SIGNALS_LOG_FILE, [])
    log.extend(signals)
    log = log[-300:]
    _save_json(config.SIGNALS_LOG_FILE, log)


def get_recent_signals(limit: int = 50) -> list:
    log = _load_json(config.SIGNALS_LOG_FILE, [])
    return list(reversed(log))[:limit]


# ---------- SUBSCRIBERS + SETTINGS ----------
def _default_settings() -> dict:
    return {
        "interval_minutes": config.DEFAULT_USER_INTERVAL,
        "market": config.DEFAULT_USER_MARKET,
        "last_sent": None,
    }


def _load_all() -> dict:
    return _load_json(config.SUBSCRIBERS_FILE, {})


def _save_all(data: dict):
    _save_json(config.SUBSCRIBERS_FILE, data)


def load_subscribers() -> list:
    return [int(cid) for cid in _load_all().keys()]


def get_settings(chat_id: int) -> dict:
    return _load_all().get(str(chat_id), _default_settings())


def add_subscriber(chat_id: int):
    data = _load_all()
    key = str(chat_id)
    if key not in data:
        data[key] = _default_settings()
        _save_all(data)


def remove_subscriber(chat_id: int):
    data = _load_all()
    data.pop(str(chat_id), None)
    _save_all(data)


def update_settings(chat_id: int, **kwargs):
    data = _load_all()
    key = str(chat_id)
    settings = data.get(key, _default_settings())
    settings.update(kwargs)
    data[key] = settings
    _save_all(data)


def mark_sent(chat_id: int):
    update_settings(chat_id, last_sent=datetime.now(timezone.utc).isoformat())


def due_for_check(chat_id: int) -> bool:
    settings = get_settings(chat_id)
    if not settings.get("last_sent"):
        return True
    last_sent = datetime.fromisoformat(settings["last_sent"])
    elapsed = (datetime.now(timezone.utc) - last_sent).total_seconds() / 60
    return elapsed >= settings["interval_minutes"]
