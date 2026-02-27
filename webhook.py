# api/webhook.py — Vercel Serverless Function (вебхук для Telegram)
# Vercel вызывает этот файл при каждом POST-запросе от Telegram

import os
import json
import asyncio
import logging
from http.server import BaseHTTPRequestHandler

from telegram import Update, Bot
from telegram.ext import Application

# Импортируем регистратор обработчиков из handlers.py
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from handlers import register_handlers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── Читаем конфиг из переменных окружения (Vercel Environment Variables) ────
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Синглтон-приложение: пересоздаём при каждом cold start
_app: Application | None = None


def get_application() -> Application:
    global _app
    if _app is None:
        _app = Application.builder().token(BOT_TOKEN).build()
        register_handlers(_app)
    return _app


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

        # Запускаем обработку обновления
        asyncio.run(self._process_update(data))

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
        app = get_application()
        # Инициализируем приложение, если ещё не инициализировано
        async with app:
            update = Update.de_json(data, app.bot)
            await app.process_update(update)
