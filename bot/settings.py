"""Application settings loading and validation."""

from __future__ import annotations

from dataclasses import dataclass
import importlib
import os
from types import ModuleType
from urllib.parse import urlparse

from dotenv import load_dotenv

TOKEN_PLACEHOLDER = "YOUR_BOT_TOKEN_HERE"


@dataclass(frozen=True, slots=True)
class Settings:
    bot_token: str
    max_bot_token: str
    galina_chat_id: int
    galina_telegram_link: str
    galina_channel_link: str
    official_site: str
    my_site: str
    shop_catalog: str


def load_settings() -> Settings:
    """Load settings from `.env`, env vars, and fallback to legacy `config.py`."""
    load_dotenv()
    legacy = _import_legacy_config()
    settings = Settings(
        bot_token=_read_str("BOT_TOKEN", legacy, TOKEN_PLACEHOLDER),
        max_bot_token=_read_str("MAX_BOT_TOKEN", legacy, ""),
        galina_chat_id=_read_int("GALINA_CHAT_ID", legacy, 0),
        galina_telegram_link=_read_str("GALINA_TELEGRAM_LINK", legacy, ""),
        galina_channel_link=_read_str("GALINA_CHANNEL_LINK", legacy, ""),
        official_site=_read_str("OFFICIAL_SITE", legacy, ""),
        my_site=_read_str("MY_SITE", legacy, ""),
        shop_catalog=_read_str("SHOP_CATALOG", legacy, ""),
    )
    _validate_settings(settings)
    return settings


def _import_legacy_config() -> ModuleType | None:
    try:
        return importlib.import_module("config")
    except ModuleNotFoundError:
        return None


def _read_str(name: str, legacy: ModuleType | None, default: str) -> str:
    value = os.getenv(name)
    if value:
        return value.strip()

    if legacy is not None and hasattr(legacy, name):
        return str(getattr(legacy, name)).strip()

    return default


def _read_int(name: str, legacy: ModuleType | None, default: int) -> int:
    raw_env = os.getenv(name)
    if raw_env:
        try:
            return int(raw_env.strip())
        except ValueError:
            return default

    if legacy is not None and hasattr(legacy, name):
        try:
            return int(getattr(legacy, name))
        except (TypeError, ValueError):
            return default

    return default


def _validate_settings(settings: Settings) -> None:
    errors: list[str] = []

    has_tg = bool(settings.bot_token and settings.bot_token != TOKEN_PLACEHOLDER)
    has_max = bool(settings.max_bot_token)
    if not has_tg and not has_max:
        errors.append("Укажите `BOT_TOKEN` (Telegram) и/или `MAX_BOT_TOKEN` (мессенджер MAX).")

    if settings.galina_chat_id <= 0:
        errors.append(
            "`GALINA_CHAT_ID` — положительный id: в Telegram это user id, в MAX — user id для пересылки обращений."
        )

    for field_name, value in {
        "GALINA_TELEGRAM_LINK": settings.galina_telegram_link,
        "GALINA_CHANNEL_LINK": settings.galina_channel_link,
        "OFFICIAL_SITE": settings.official_site,
        "MY_SITE": settings.my_site,
        "SHOP_CATALOG": settings.shop_catalog,
    }.items():
        if not _is_valid_url(value):
            errors.append(f"`{field_name}` должен быть корректным URL (http/https).")

    if errors:
        joined = "\n- ".join(errors)
        raise ValueError(f"Ошибка конфигурации:\n- {joined}")


def _is_valid_url(value: str) -> bool:
    parsed = urlparse(value)
    return bool(parsed.scheme in {"http", "https"} and parsed.netloc)

