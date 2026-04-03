"""Keyboard factories used by the bot handlers."""

from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.settings import Settings


ABOUT_ME = "👩 Обо мне"
ABOUT_COMPANY = "🏢 О компании"
ABOUT_PRODUCT = "🌱 О продукте"
CERTIFICATES = "📜 Сертификаты"
GEOGRAPHY = "🌍 География"
CONCERN = "💬 Что тебя беспокоит?"
REGISTRATION = "✍️ Регистрация"
PRICES = "💰 Цены"
CONTACTS = "📞 Контакты"

BACK_TO_MENU_CALLBACK = "back_to_menu"

# callback_data главного меню (как в MAX) — не зависит от текста/эмодзи в клиенте
CB_MAIN = "m:main"
CB_ABOUT_ME = "m:about_me"
CB_ABOUT_COMPANY = "m:about_company"
CB_ABOUT_PRODUCT = "m:about_product"
CB_CERT = "m:cert"
CB_GEO = "m:geo"
CB_CONCERN = "m:concern"
CB_REG = "m:reg"
CB_PRICES = "m:prices"
CB_CONTACTS = "m:contacts"
# Номер MAX (tel: в link MAX не работает — отдельная callback-кнопка)
CB_MAX_PHONE = "m:max_phone"

# Один regex для CallbackQueryHandler (все пункты кроме concern — его ведёт ConversationHandler)
MENU_CALLBACK_PATTERN = (
    r"^m:(about_me|about_company|about_product|cert|geo|reg|prices|contacts)$"
)


def main_menu() -> InlineKeyboardMarkup:
    """Главное меню: inline-кнопки со стабильным callback_data (не reply-клавиатура)."""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(ABOUT_ME, callback_data=CB_ABOUT_ME),
                InlineKeyboardButton(ABOUT_COMPANY, callback_data=CB_ABOUT_COMPANY),
            ],
            [
                InlineKeyboardButton(ABOUT_PRODUCT, callback_data=CB_ABOUT_PRODUCT),
                InlineKeyboardButton(CERTIFICATES, callback_data=CB_CERT),
            ],
            [
                InlineKeyboardButton(GEOGRAPHY, callback_data=CB_GEO),
                InlineKeyboardButton(CONCERN, callback_data=CB_CONCERN),
            ],
            [
                InlineKeyboardButton(REGISTRATION, callback_data=CB_REG),
                InlineKeyboardButton(PRICES, callback_data=CB_PRICES),
            ],
            [[InlineKeyboardButton(CONTACTS, callback_data=CB_CONTACTS)]],
        ]
    )


def back_to_menu_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🏠 Главное меню", callback_data=BACK_TO_MENU_CALLBACK)]]
    )


def channel_and_menu_inline(settings: Settings) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📣 Перейти в Telegram-канал Галины", url=settings.galina_channel_link)],
            [InlineKeyboardButton("🏠 Главное меню", callback_data=BACK_TO_MENU_CALLBACK)],
        ]
    )


def shop_and_contact_inline(settings: Settings) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🛒 Открыть каталог", url=settings.shop_catalog)],
            [
                InlineKeyboardButton(
                    "✉️ Написать Галине лично в Телеграм", url=settings.galina_telegram_link
                )
            ],
            [
                InlineKeyboardButton(
                    "✉️ Написать Галине лично в МАХ", url=settings.galina_max_contact_link
                )
            ],
            [InlineKeyboardButton("🏠 Главное меню", callback_data=BACK_TO_MENU_CALLBACK)],
        ]
    )


def contacts_inline(settings: Settings) -> InlineKeyboardMarkup:
    """Раздел «Контакты»: ссылки на канал, личку в Telegram и в MAX."""
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📣 Telegram-канал", url=settings.galina_channel_link)],
            [
                InlineKeyboardButton(
                    "✉️ Мой личный Telegram", url=settings.galina_telegram_link
                )
            ],
            [
                InlineKeyboardButton(
                    "✉️ Мой личный MAX (+79287603233)", url=settings.galina_max_contact_link
                )
            ],
            [InlineKeyboardButton("🏠 Главное меню", callback_data=BACK_TO_MENU_CALLBACK)],
        ]
    )


def register_inline(settings: Settings) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✉️ Написать Галине для регистрации в Телеграм",
                    url=settings.galina_telegram_link,
                )
            ],
            [
                InlineKeyboardButton(
                    "✉️ Написать Галине для регистрации в МАХ",
                    url=settings.galina_max_contact_link,
                )
            ],
            [InlineKeyboardButton("🏠 Главное меню", callback_data=BACK_TO_MENU_CALLBACK)],
        ]
    )

