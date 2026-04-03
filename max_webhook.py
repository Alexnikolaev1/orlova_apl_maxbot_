# max_webhook.py — Vercel: входящие вебхуки MAX (HTTPS POST JSON Update)
# https://dev.max.ru/docs-api/methods/POST/subscriptions

import asyncio
import json
import logging
import os
from http.server import BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        logger.info(format, *args)

    def do_POST(self) -> None:
        secret = os.environ.get("MAX_WEBHOOK_SECRET", "").strip()
        if secret:
            got = self.headers.get("X-Max-Bot-Api-Secret") or ""
            if got != secret:
                self._respond(403, "Forbidden")
                return

        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as e:
            logger.error("MAX webhook JSON: %s", e)
            self._respond(400, "Bad Request")
            return

        asyncio.run(_handle(data))
        self._respond(200, "OK")

    def do_GET(self) -> None:
        self._respond(200, "MAX webhook endpoint OK")

    def _respond(self, status: int, text: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(text.encode("utf-8"))


async def _handle(data: dict) -> None:
    from bot.settings import load_settings
    from max_bot.client import MaxApiClient
    from max_bot.engine import process_max_update

    try:
        settings = load_settings()
    except ValueError as e:
        logger.error("Конфиг: %s", e)
        return
    token = (settings.max_bot_token or os.environ.get("MAX_BOT_TOKEN", "")).strip()
    if not token:
        logger.error("MAX_BOT_TOKEN не задан")
        return
    client = MaxApiClient(token)
    await process_max_update(data, settings, client)
