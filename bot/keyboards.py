"""Keyboard factories used by the bot handlers."""

from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

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


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(ABOUT_ME), KeyboardButton(ABOUT_COMPANY)],
            [KeyboardButton(ABOUT_PRODUCT), KeyboardButton(CERTIFICATES)],
            [KeyboardButton(GEOGRAPHY), KeyboardButton(CONCERN)],
            [KeyboardButton(REGISTRATION), KeyboardButton(PRICES)],
            [KeyboardButton(CONTACTS)],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
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

