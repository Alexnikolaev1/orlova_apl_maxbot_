# 🤖 Telegram-бот «Галина Орлова | APL GO»

## Структура проекта

```text
orlova_apl_bot/
├── bot/
│   ├── app.py
│   ├── handlers.py
│   ├── keyboards.py
│   └── settings.py
├── .env.example
├── config.py
├── main.py
├── webhook.py
├── set_webhook.py
└── vercel.json
```

## Локальный запуск (сначала проверить бота локально)

1. Установи зависимости:

```bash
pip install -r requirements.txt
```

2. Создай `.env` из шаблона `.env.example` и заполни реальными значениями:

- `BOT_TOKEN`
- `GALINA_CHAT_ID`
- `GALINA_TELEGRAM_LINK`
- `GALINA_CHANNEL_LINK`
- `OFFICIAL_SITE`
- `SHOP_CATALOG`

3. Запусти:

```bash
python main.py
```

> Бот автоматически читает переменные из `.env` (через `python-dotenv`).

## Vercel (после локальной проверки)

- Добавь те же переменные окружения в Vercel Project Settings.
- Установи вебхук:

```bash
python set_webhook.py --url https://your-project.vercel.app
```
