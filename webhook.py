# api/webhook.py — Vercel Serverless Function (вебхук для Telegram)
# Vercel вызывает этот файл при каждом POST-запросе от Telegram
#
# Важно:
# 1) Каждый `asyncio.run()` создаёт НОВЫЙ event loop. Один глобальный Application нельзя
#    переиспользовать между POST — у Bot/httpx клиент привязан к циклу (после /start могло
#    «сломаться» всё остальное, включая callback-кнопки).
# 2) На один webhook: собрать Application → initialize → process_update → shutdown в одном run.
# 3) Переустанови вебхук с allowed_updates (см. set_webhook.py), иначе callback_query не приходят.

import os
import json
import asyncio
import logging
from http.server import BaseHTTPRequestHandler

from telegram import Update
from telegram.ext import Application, ContextTypes

# Импортируем регистратор обработчиков из handlers.py
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from handlers import register_handlers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── Читаем конфиг из переменных окружения (Vercel Environment Variables) ────
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

def _build_application() -> Application:
    """Новый Application на каждый POST: asyncio.run() каждый раз создаёт новый event loop,
    а клиент Bot/httpx привязан к циклу — нельзя переиспользовать один и тот же Application."""
    if not BOT_TOKEN.strip():
        raise RuntimeError("BOT_TOKEN пустой в окружении Vercel")
    app = Application.builder().token(BOT_TOKEN).build()
    register_handlers(app)

    async def _on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.exception("Ошибка обработчика Telegram: %s", context.error)
        del update

    app.add_error_handler(_on_error)
    return app


# ─── Точка входа для Vercel ───────────────────────────────────────────────────
class handler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        logger.info(format, *args)

    def do_POST(self):
        """Telegram шлёт POST с JSON-обновлением."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body.decode("utf-8"))
        except Exception as e:
            logger.error("Ошибка парсинга JSON: %s", e)
            self._respond(400, "Bad Request")
            return

        try:
            asyncio.run(self._process_update(data))
        except Exception:
            logger.exception("Ошибка обработки webhook update")
            self._respond(500, "Internal Error")
            return

        self._respond(200, "OK")

    def do_GET(self):
        """Health-check эндпоинт."""
        self._respond(200, "Бот Галины Орловой | APL GO работает! ✅")

    def _respond(self, status: int, text: str):
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(text.encode("utf-8"))

    async def _process_update(self, data: dict):
        app = _build_application()
        if data.get("callback_query"):
            logger.info("Входящий callback_query (inline-кнопка)")
        await app.initialize()
        try:
            update = Update.de_json(data, app.bot)
            await app.process_update(update)
        finally:
            await app.shutdown()
