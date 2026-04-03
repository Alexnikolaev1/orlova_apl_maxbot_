"""
Тексты и клавиатуры для MAX — те же сценарии, что в Telegram (bot/handlers.py).
Формат кнопок: https://dev.max.ru/docs-api (inline_keyboard, callback / link).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from bot.keyboards import (
    ABOUT_COMPANY,
    ABOUT_ME,
    ABOUT_PRODUCT,
    CERTIFICATES,
    CONCERN,
    CONTACTS,
    GEOGRAPHY,
    PRICES,
    REGISTRATION,
)
from bot.settings import Settings

# Callback payloads (внутренние, не видны пользователю)
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


def _cb(text: str, payload: str) -> dict[str, Any]:
    return {"type": "callback", "text": text, "payload": payload, "intent": "default"}


def _link(text: str, url: str) -> dict[str, Any]:
    return {"type": "link", "text": text, "url": url}


def _inline_kb(rows: list[list[dict[str, Any]]]) -> dict[str, Any]:
    return {"type": "inline_keyboard", "payload": {"buttons": rows}}


def attachment_main_menu() -> dict[str, Any]:
    rows = [
        [_cb(ABOUT_ME, CB_ABOUT_ME), _cb(ABOUT_COMPANY, CB_ABOUT_COMPANY)],
        [_cb(ABOUT_PRODUCT, CB_ABOUT_PRODUCT), _cb(CERTIFICATES, CB_CERT)],
        [_cb(GEOGRAPHY, CB_GEO), _cb(CONCERN, CB_CONCERN)],
        [_cb(REGISTRATION, CB_REG), _cb(PRICES, CB_PRICES)],
        [_cb(CONTACTS, CB_CONTACTS)],
    ]
    return _inline_kb(rows)


def attachment_back_only() -> dict[str, Any]:
    return _inline_kb([[_cb("🏠 Главное меню", CB_MAIN)]])


def attachment_channel_and_menu(settings: Settings) -> dict[str, Any]:
    return _inline_kb(
        [
            [_link("📣 Перейти в Telegram-канал Галины", settings.galina_channel_link)],
            [_cb("🏠 Главное меню", CB_MAIN)],
        ]
    )


def attachment_shop_and_contact(settings: Settings) -> dict[str, Any]:
    return _inline_kb(
        [
            [_link("🛒 Открыть каталог", settings.shop_catalog)],
            [_link("✉️ Написать Галине лично", settings.galina_telegram_link)],
            [_cb("🏠 Главное меню", CB_MAIN)],
        ]
    )


def attachment_register(settings: Settings) -> dict[str, Any]:
    return _inline_kb(
        [
            [_link("✉️ Написать Галине для регистрации", settings.galina_telegram_link)],
            [_cb("🏠 Главное меню", CB_MAIN)],
        ]
    )


def menu_photo_path() -> Path:
    return Path(__file__).resolve().parent.parent / "orlova.jpg"


# --- Тексты (как в bot/handlers.py) ---


def text_welcome(first_name: str) -> str:
    return (
        f"Привет, {first_name}! 👋\n\n"
        "Я Галина Орлова — партнёр сетевой компании APL GO, управляющий директор со своей "
        "международной командой. Готова быть твоим проводником в мире возможностей "
        "здоровья и бизнеса. А в помощь нам — этот бот.\n\n"
        "Выбирай, что тебя интересует 👇"
    )


def text_about_me(settings: Settings) -> str:
    return (
        "👩 Обо мне\n\n"
        "Меня зовут Галина Орлова. Я с удовольствием пользуюсь продукцией компании APL GO "
        "и рада, что когда-то открыла её для себя. Она снизила мой биологический возраст "
        "на 10 лет по сравнению с паспортным. Она натуральная и безопасная. По сути — "
        "клеточное питание, с почти 100%-ным усвоением за счёт уникальной технологии "
        "извлечения полезных веществ из растений и за счёт сублингвального приёма "
        "(рассасывания под языком). 🌱\n\n"
        "Компания щедрая, порядочная, с высоким индексом надёжности, и поэтому с ней "
        "можно зарабатывать. 💼 Так сказать, здоровье и бизнес в одном флаконе. У тебя "
        "есть выбор остановиться на одном направлении или использовать оба.\n\n"
        f"Переходи в мой Telegram-канал: {settings.galina_channel_link}\n\n"
        f"Всю остальную информацию можно найти на проверенном сайте: {settings.official_site}"
    )


def text_about_company() -> str:
    return (
        "🏢 О компании APL GO\n\n"
        "Сетевая компания APL GO образовалась 11 ноября 2011 года и начинала свой старт "
        "с 3 видов драже. С тех пор ассортимент вырос до 18 видов драже, которые "
        "распространяются в 76 странах мира. 🌍\n\n"
        "Её основатель и президент — Сергей Куликов. Ему 36 лет, он харизматичный, "
        "амбициозный и порядочный человек, верующий в Бога, занимающийся "
        "благотворительностью, поддерживающий семейные ценности. Его жена Ольга — его "
        "верный помощник, директор креативного отдела компании, редактор журнала, "
        "основатель и лицо косметической линии компании — Бьюти. У них четверо детей.\n\n"
        "С компанией можно оздоравливаться, зарабатывать и путешествовать. ✈️ Партнёры "
        "компании посетили более 30 стран. А мне посчастливилось выиграть бесплатный "
        "круиз в Мексику на третий месяц своего пребывания в компании.\n\n"
        "Принцип работы прост: попробуй продукт сам, расскажи о результатах другим. В "
        "бэк-офисе есть база для обучения, а в интернете — тысячи видео с результатами "
        "приёма драже."
    )


def text_about_product(settings: Settings) -> str:
    return (
        "🌱 О продукте\n\n"
        "Главный продукт компании — это драже (клеточное питание). Они производятся "
        "на двух заводах компании: в Кишинёве и в Подмосковье.\n\n"
        "Кроме драже в каталоге есть серия полезных продуктов: чаи, каши, батончики, "
        "кофе, одежда, аксессуары, инструменты для бизнеса.\n\n"
        "Полный список драже и всей продукции с описанием состава и ценами смотри в "
        f"официальном интернет-магазине: {settings.shop_catalog}"
    )


def text_certificates(settings: Settings) -> str:
    return (
        "📜 Сертификаты\n\n"
        "Продукция APL GO имеет все необходимые сертификаты качества и безопасности. ✅\n\n"
        "Детальную информацию о сертификатах можно найти на главном сайте компании в "
        f"соответствующем разделе: {settings.official_site}"
    )


def text_geography() -> str:
    return (
        "🌍 География APL GO\n\n"
        "Продукция компании APL GO распространяется в 76 странах мира. "
        "Нас становится больше с каждым днём! 🚀"
    )


def text_registration() -> str:
    return (
        "✍️ Регистрация\n\n"
        "Отличное решение! 🎉 Чтобы стать партнёром или клиентом компании, нужно "
        "зарегистрироваться. Я лично помогу тебе с этим и проконсультирую.\n\n"
        "👇 Напиши мне в личные сообщения, и мы начнём прямо сейчас!"
    )


def text_prices(settings: Settings) -> str:
    return (
        "💰 Цены\n\n"
        "Актуальные цены на всю продукцию всегда представлены в нашем официальном "
        f"интернет-магазине. Ты можешь посмотреть их здесь: {settings.shop_catalog}"
    )


def text_contacts(settings: Settings) -> str:
    return (
        "📞 Контакты\n\n"
        "Всегда на связи! 💬\n\n"
        f"📣 Мой Telegram-канал: {settings.galina_channel_link}\n"
        f"✉️ Мой личный Telegram (для связи и регистрации): {settings.galina_telegram_link}\n"
        f"🌐 Официальный сайт компании: {settings.official_site}\n"
        f"✍️ Мой личный сайт с блогом: {settings.my_site}\n"
        f"🛒 Интернет-магазин: {settings.shop_catalog}\n"
        f"📞 Мой телефон: +7 913 958 6418\n"
    )


def text_concern_start(settings: Settings) -> str:
    return (
        "💬 Что тебя беспокоит?\n\n"
        "Здоровье — это главное. 🌱 Расскажи, что именно тебя беспокоит? "
        "Напиши в следующем сообщении — я (или моя команда) отвечу лично.\n\n"
        "А пока можешь посмотреть каталог продукции, чтобы понять, какие натуральные "
        f"компоненты могут помочь в твоей ситуации: {settings.shop_catalog}"
    )


def text_unknown(settings: Settings) -> str:
    return (
        "Пожалуйста, воспользуйся кнопками меню, чтобы я могла помочь тебе быстрее. 👇\n\n"
        f"Если у тебя личный вопрос — напиши мне в личку: {settings.galina_telegram_link}"
    )


def text_concern_ok(settings: Settings) -> str:
    return (
        "Спасибо, что поделился(-ась)! 🌱 Я получила твоё сообщение и скоро свяжусь с тобой лично.\n\n"
        "Если хочешь написать напрямую прямо сейчас — вот моя личка:\n"
        f"{settings.galina_telegram_link}"
    )


def text_concern_fail(settings: Settings) -> str:
    return (
        "Спасибо за сообщение! Сейчас возникла техническая проблема с автоотправкой.\n"
        "Напиши мне напрямую в личку, чтобы я точно увидела твой запрос:\n"
        f"{settings.galina_telegram_link}"
    )


def text_cancel_menu() -> str:
    return "Хорошо, возвращаемся в главное меню. 🏠"


def text_forward_concern(user_name: str, username: str | None, user_id: int, text: str) -> str:
    return (
        "📩 Новое обращение от пользователя!\n\n"
        f"👤 Имя: {user_name}\n"
        f"🆔 Username: @{username if username else 'нет'}\n"
        f"🔗 ID: {user_id}\n\n"
        f"💬 Сообщение:\n{text}"
    )


LABEL_TO_CB: dict[str, str] = {
    ABOUT_ME: CB_ABOUT_ME,
    ABOUT_COMPANY: CB_ABOUT_COMPANY,
    ABOUT_PRODUCT: CB_ABOUT_PRODUCT,
    CERTIFICATES: CB_CERT,
    GEOGRAPHY: CB_GEO,
    CONCERN: CB_CONCERN,
    REGISTRATION: CB_REG,
    PRICES: CB_PRICES,
    CONTACTS: CB_CONTACTS,
}
