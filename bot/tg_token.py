"""Токен Telegram Bot API (@BotFather). Не путать с MAX_BOT_TOKEN (мессенджер MAX)."""

from __future__ import annotations

import os


def telegram_bot_token_from_env() -> str:
    """Читает токен Telegram: BOT_TOKEN или TELEGRAM_BOT_TOKEN (алиас для Vercel)."""
    return (
        os.environ.get("BOT_TOKEN", "").strip()
        or os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    )
