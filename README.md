# 🤖 Telegram-бот «Галина Орлова | APL GO»

## Структура проекта

```text
orlova_apl_bot/
├── bot/
│   ├── app.py
│   ├── handlers.py
│   ├── keyboards.py
│   └── settings.py
├── max_bot/
│   ├── client.py      # HTTP-клиент platform-api.max.ru
│   ├── engine.py      # Логика (как в Telegram)
│   └── galina.py      # Тексты и inline-клавиатуры MAX
├── .env.example
├── config.py
├── main.py            # Telegram: polling
├── main_max.py        # MAX: long polling (локально)
├── webhook.py         # Vercel: Telegram webhook
├── max_webhook.py     # Vercel: MAX webhook
├── set_webhook.py
├── set_max_subscription.py
└── vercel.json
```

## Локальный запуск (сначала проверить бота локально)

1. Установи зависимости:

```bash
pip install -r requirements.txt
```

2. Создай `.env` из шаблона `.env.example` и заполни реальными значениями:

- `BOT_TOKEN` (Telegram) и/или `MAX_BOT_TOKEN` (мессенджер MAX)
- `GALINA_CHAT_ID`
- `GALINA_TELEGRAM_LINK` (например `https://t.me/Orlova_Gal`)
- `GALINA_TELEGRAM_USERNAME` (без `@`, например `Orlova_Gal` — как показывается в разделе «Контакты»)
- `GALINA_MAX_CONTACT_LINK` (опционально, по умолчанию `tel:+79287603233` — кнопка «в МАХ»)
- `GALINA_CHANNEL_LINK`
- `OFFICIAL_SITE`
- `SHOP_CATALOG`

3. Запусти:

```bash
python main.py
```

> Бот автоматически читает переменные из `.env` (через `python-dotenv`).

## Мессенджер MAX (тот же сценарий, что и в Telegram)

Документация платформы: [dev.max.ru/docs](https://dev.max.ru/docs/), API: [dev.max.ru/docs-api](https://dev.max.ru/docs-api).

1. Создай и промодерируй бота в [MAX для партнёров](https://business.max.ru/self), возьми токен (**Интеграция → Получить токен**).
2. В `.env` укажи `MAX_BOT_TOKEN`. Для пересылки раздела «Что тебя беспокоит?» в `GALINA_CHAT_ID` укажи **user id пользователя в MAX** (тот же смысл, что id в Telegram, но в экосистеме MAX).
3. Локально (long polling, удобно для отладки):

```bash
python main_max.py
```

4. Продакшен: только **webhook** на HTTPS (см. [POST /subscriptions](https://dev.max.ru/docs-api/methods/POST/subscriptions)). После деплоя на Vercel:

```bash
python set_max_subscription.py --url https://your-project.vercel.app
```

Эндпоинт вебхука: `https://your-project.vercel.app/api/max-webhook`. Опционально задай `MAX_WEBHOOK_SECRET` в Vercel и в подписке — тот же секрет проверяется заголовком `X-Max-Bot-Api-Secret` в `max_webhook.py`.

> Ограничение serverless: состояние «ожидаю текст обращения» хранится в памяти инстанса (как и `ConversationHandler` у Telegram на Vercel). Для высокой нагрузки понадобится внешнее хранилище.

## Vercel (после локальной проверки)

- Добавь те же переменные окружения в Vercel Project Settings.
- Установи вебхук:

```bash
python set_webhook.py --url https://your-project.vercel.app
```

Пример продакшен-домена MAX-деплоя: [orlovaaplmaxbot.vercel.app](https://orlovaaplmaxbot.vercel.app).
