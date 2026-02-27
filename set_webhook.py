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
from telegram import Bot


async def set_webhook(token: str, webhook_url: str):
    bot = Bot(token=token)

    # Удаляем старый вебхук (если был)
    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ Старый вебхук удалён.")

    # Устанавливаем новый
    full_url = f"{webhook_url.rstrip('/')}/api/webhook"
    result = await bot.set_webhook(url=full_url)

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
        help="Токен бота (если не указан, читается из переменной окружения BOT_TOKEN)",
    )
    parser.add_argument(
        "--url",
        required=True,
        help="URL вашего Vercel-проекта, например: https://your-project.vercel.app",
    )
    args = parser.parse_args()

    import os
    token = args.token or os.environ.get("BOT_TOKEN")
    if not token:
        print("❌ Укажите токен через --token или переменную окружения BOT_TOKEN")
        exit(1)

    asyncio.run(set_webhook(token, args.url))
