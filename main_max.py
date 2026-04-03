"""Локальный запуск бота MAX через long polling (разработка и тест)."""

from __future__ import annotations

import asyncio
import logging
import os
import sys

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def _run() -> None:
    from dotenv import load_dotenv

    load_dotenv()

    from bot.settings import load_settings
    from max_bot.client import MaxApiClient
    from max_bot.engine import process_max_update

    settings = load_settings()
    token = (settings.max_bot_token or os.environ.get("MAX_BOT_TOKEN", "")).strip()
    if not token:
        logger.error("Укажите MAX_BOT_TOKEN в .env или config.py")
        sys.exit(1)

    client = MaxApiClient(token)
    marker: int | None = None
    types = ["message_created", "message_callback", "bot_started"]

    logger.info("MAX long polling запущен (Ctrl+C для остановки)")

    while True:
        data = await client.get_updates(marker=marker, limit=100, timeout=30, types=types)
        updates = data.get("updates") or []
        for upd in updates:
            try:
                await process_max_update(upd, settings, client)
            except Exception:
                logger.exception("Ошибка обработки update")
        if data.get("marker") is not None:
            marker = data["marker"]


def main() -> None:
    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        logger.info("Остановлено")


if __name__ == "__main__":
    main()
