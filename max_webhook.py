# max_webhook.py — Vercel: входящие вебхуки MAX (HTTPS POST JSON Update)
# https://dev.max.ru/docs-api/methods/POST/subscriptions

import asyncio
import json
import logging
import os
import sys
from http.server import BaseHTTPRequestHandler

# Vercel показывает stdout/stderr в Runtime Logs — явно пишем в stdout и форсируем конфиг
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
    force=True,
)
logger = logging.getLogger("max_webhook")


class handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        logger.info(format, *args)

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        logger.info(
            "MAX webhook POST path=%s content_length=%s",
            getattr(self, "path", ""),
            length,
        )

        secret = os.environ.get("MAX_WEBHOOK_SECRET", "").strip()
        if secret:
            got = self.headers.get("X-Max-Bot-Api-Secret") or ""
            if got != secret:
                logger.warning("MAX webhook: неверный X-Max-Bot-Api-Secret")
                self._respond(403, "Forbidden")
                return

        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as e:
            logger.error("MAX webhook JSON: %s", e)
            self._respond(400, "Bad Request")
            return

        ut = data.get("update_type") if isinstance(data, dict) else None
        logger.info("MAX update received: update_type=%s", ut)

        try:
            asyncio.run(_handle(data))
        except Exception as e:
            # В Runtime Logs смотри строку «MAX webhook failed» и traceback ниже
            logger.error("MAX webhook failed: %s: %s", type(e).__name__, e)
            logger.exception("MAX: traceback")
            self._respond(500, "Internal Error")
            return

        logger.info("MAX update OK: update_type=%s", ut)
        self._respond(200, "OK")

    def do_GET(self) -> None:
        logger.info("MAX webhook GET (health check)")
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
        raise
    token = (settings.max_bot_token or os.environ.get("MAX_BOT_TOKEN", "")).strip()
    if not token:
        logger.error("MAX_BOT_TOKEN не задан в окружении Vercel")
        raise RuntimeError("MAX_BOT_TOKEN is empty")
    client = MaxApiClient(token)
    await process_max_update(data, settings, client)
