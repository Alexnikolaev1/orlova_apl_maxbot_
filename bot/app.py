"""Application assembly and runtime entrypoints."""

from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import Application, ContextTypes

from bot.handlers import register_handlers
from bot.settings import load_settings


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def _on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled telegram update error: %s", context.error)
    del update


def build_application() -> Application:
    settings = load_settings()
    app = Application.builder().token(settings.bot_token).build()
    register_handlers(app, settings)
    app.add_error_handler(_on_error)
    return app


def run() -> None:
    app = build_application()
    logger.info("Бот Галины Орловой | APL GO запущен")
    app.run_polling(allowed_updates=[Update.MESSAGE, Update.CALLBACK_QUERY])

