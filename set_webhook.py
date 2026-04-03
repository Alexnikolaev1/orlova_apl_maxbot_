#!/usr/bin/env python3
# set_webhook.py — Запусти этот скрипт ОДИН РАЗ после деплоя на Vercel,
# чтобы Telegram знал, куда слать обновления.
#
# Использование:
#   python set_webhook.py
#
# Или с аргументами:
#   python set_webhook.py --token YOUR_TOKEN --url https://your-project.vercel.app

import argparse
import asyncio
from telegram import Bot, Update


async def set_webhook(token: str, webhook_url: str):
    bot = Bot(token=token)

    # Удаляем старый вебхук (если был)
    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ Старый вебхук удалён.")

    # Устанавливаем новый
    full_url = f"{webhook_url.rstrip('/')}/api/webhook"
    # Явно запрашиваем callback_query — иначе при старой настройке inline-кнопки не приходят
    result = await bot.set_webhook(
        url=full_url,
        allowed_updates=Update.ALL_TYPES,
    )

    if result:
        print(f"✅ Вебхук успешно установлен: {full_url}")
        info = await bot.get_webhook_info()
        print(f"   URL: {info.url}")
        print(f"   Pending updates: {info.pending_update_count}")
    else:
        print("❌ Не удалось установить вебхук.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Установить Telegram Webhook")
    parser.add_argument(
        "--token",
        default=None,
        help="Токен Telegram (если не указан: BOT_TOKEN или TELEGRAM_BOT_TOKEN в окружении)",
    )
    parser.add_argument(
        "--url",
        required=True,
        help="URL вашего Vercel-проекта, например: https://your-project.vercel.app",
    )
    args = parser.parse_args()

    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from bot.tg_token import telegram_bot_token_from_env

    token = args.token or telegram_bot_token_from_env()
    if not token:
        print(
            "❌ Укажите токен через --token или переменные BOT_TOKEN / TELEGRAM_BOT_TOKEN "
            "(токен Telegram от @BotFather). MAX_BOT_TOKEN — только для MAX, не для set_webhook."
        )
        exit(1)

    asyncio.run(set_webhook(token, args.url))
