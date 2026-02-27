"""Compatibility shim for legacy imports."""

from telegram.ext import Application

from bot.handlers import register_handlers as _new_register_handlers
from bot.settings import load_settings


def register_handlers(app: Application) -> None:
    """Legacy adapter: keeps old `register_handlers(app)` contract."""
    _new_register_handlers(app, load_settings())


__all__ = ["register_handlers"]
