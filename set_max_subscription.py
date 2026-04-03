#!/usr/bin/env python3
"""Подписка MAX на webhook: POST /subscriptions (https://dev.max.ru/docs-api/methods/POST/subscriptions)."""

from __future__ import annotations

import argparse
import asyncio
import os
import sys

from dotenv import load_dotenv


async def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="MAX: установить URL вебхука")
    parser.add_argument(
        "--url",
        required=True,
        help="Базовый URL проекта, например https://xxx.vercel.app (без /api/max-webhook)",
    )
    parser.add_argument(
        "--token",
        default=None,
        help="Токен бота MAX (иначе переменная MAX_BOT_TOKEN)",
    )
    parser.add_argument(
        "--secret",
        default=None,
        help="Секрет для заголовка X-Max-Bot-Api-Secret (иначе MAX_WEBHOOK_SECRET)",
    )
    args = parser.parse_args()

    token = (args.token or os.environ.get("MAX_BOT_TOKEN", "")).strip()
    if not token:
        print("❌ Укажите --token или MAX_BOT_TOKEN")
        sys.exit(1)

    base = args.url.rstrip("/")
    webhook_url = f"{base}/api/max-webhook"
    secret = (args.secret or os.environ.get("MAX_WEBHOOK_SECRET", "") or "").strip() or None

    from max_bot.client import MaxApiClient

    client = MaxApiClient(token)
    types = ["message_created", "message_callback", "bot_started"]
    await client.set_subscription(webhook_url, types, secret=secret)
    print(f"✅ Подписка отправлена: {webhook_url}")
    if secret:
        print("   (с секретом — проверяйте X-Max-Bot-Api-Secret на сервере)")


if __name__ == "__main__":
    asyncio.run(main())
