"""Handlers and routes registration."""

from __future__ import annotations

import logging
from typing import Any
from pathlib import Path

from telegram import InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot.keyboards import (
    ABOUT_COMPANY,
    ABOUT_ME,
    ABOUT_PRODUCT,
    BACK_TO_MENU_CALLBACK,
    CB_ABOUT_COMPANY,
    CB_ABOUT_ME,
    CB_ABOUT_PRODUCT,
    CB_CERT,
    CB_CONCERN,
    CB_CONTACTS,
    CB_GEO,
    CB_PRICES,
    CB_REG,
    CERTIFICATES,
    CONCERN,
    CONTACTS,
    GEOGRAPHY,
    MENU_CALLBACK_PATTERN,
    PRICES,
    REGISTRATION,
    back_to_menu_inline,
    channel_and_menu_inline,
    contacts_inline,
    main_menu,
    register_inline,
    shop_and_contact_inline,
)
from bot.menu_filters import ExactReplyButtonText, norm_menu_text
from bot.settings import Settings


logger = logging.getLogger(__name__)

WAITING_FOR_CONCERN = 1


class BotHandlers:
    """Encapsulates handlers to avoid global state and simplify testing."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._main_menu = main_menu()
        self._menu_photo_path = Path(__file__).resolve().parent.parent / "orlova.jpg"
        # Заполняется в register_handlers: пункты главного меню при ожидании текста «Что беспокоит?»
        self._menu_handlers: dict[str, Any] = {}

    async def _reply_section(
        self,
        update: Update,
        text: str,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> None:
        """Ответ раздела: и из текста, и из callback inline-меню (у callback нет message)."""
        if update.callback_query:
            await update.callback_query.answer()
            if update.effective_message:
                await update.effective_message.reply_text(text, reply_markup=reply_markup)
            return
        if update.message:
            await update.message.reply_text(text, reply_markup=reply_markup)

    async def _send_main_menu(self, update: Update, text: str) -> None:
        """Send main menu with photo if available."""
        if not update.message:
            return

        if self._menu_photo_path.exists():
            with self._menu_photo_path.open("rb") as image:
                await update.message.reply_photo(
                    photo=image,
                    caption=text,
                    reply_markup=self._main_menu,
                )
            return

        await update.message.reply_text(text, reply_markup=self._main_menu)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        del context
        user = update.effective_user
        first_name = user.first_name if user and user.first_name else "дорогой друг"
        welcome_text = (
            f"Привет, {first_name}! 👋\n\n"
            "Я Галина Орлова — партнёр сетевой компании APL GO, управляющий директор со своей "
            "международной командой. Готова быть твоим проводником в мире возможностей "
            "здоровья и бизнеса. А в помощь нам — этот бот.\n\n"
            "Выбирай, что тебя интересует 👇"
        )
        await self._send_main_menu(update, welcome_text)

    async def show_about_me(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        del context
        text = (
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
            f"Переходи в мой Telegram-канал: {self.settings.galina_channel_link}\n\n"
            f"Всю остальную информацию можно найти на проверенном сайте: {self.settings.official_site}"
        )
        await self._reply_section(update, text, channel_and_menu_inline(self.settings))

    async def show_about_company(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        del context
        text = (
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
        await self._reply_section(update, text, back_to_menu_inline())

    async def show_about_product(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        del context
        text = (
            "🌱 О продукте\n\n"
            "Главный продукт компании — это драже (клеточное питание). Они производятся "
            "на двух заводах компании: в Кишинёве и в Подмосковье.\n\n"
            "Кроме драже в каталоге есть серия полезных продуктов: чаи, каши, батончики, "
            "кофе, одежда, аксессуары, инструменты для бизнеса.\n\n"
            "Полный список драже и всей продукции с описанием состава и ценами смотри в "
            f"официальном интернет-магазине: {self.settings.shop_catalog}"
        )
        await self._reply_section(update, text, shop_and_contact_inline(self.settings))

    async def show_certificates(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        del context
        text = (
            "📜 Сертификаты\n\n"
            "Продукция APL GO имеет все необходимые сертификаты качества и безопасности. ✅\n\n"
            "Детальную информацию о сертификатах можно найти на главном сайте компании в "
            f"соответствующем разделе: {self.settings.official_site}"
        )
        await self._reply_section(update, text, back_to_menu_inline())

    async def show_geography(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        del context
        text = (
            "🌍 География APL GO\n\n"
            "Продукция компании APL GO распространяется в 76 странах мира. "
            "Нас становится больше с каждым днём! 🚀"
        )
        await self._reply_section(update, text, back_to_menu_inline())

    async def show_registration(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        del context
        text = (
            "✍️ Регистрация\n\n"
            "Отличное решение! 🎉 Чтобы стать партнёром или клиентом компании, нужно "
            "зарегистрироваться. Я лично помогу тебе с этим и проконсультирую.\n\n"
            "👇 Напиши мне в личные сообщения, и мы начнём прямо сейчас!"
        )
        await self._reply_section(update, text, register_inline(self.settings))

    async def show_prices(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        del context
        text = (
            "💰 Цены\n\n"
            "Актуальные цены на всю продукцию всегда представлены в нашем официальном "
            f"интернет-магазине. Ты можешь посмотреть их здесь: {self.settings.shop_catalog}"
        )
        await self._reply_section(update, text, shop_and_contact_inline(self.settings))

    async def show_contacts(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        del context
        u = self.settings.galina_telegram_username.lstrip("@")
        text = (
            "📞 Контакты\n\n"
            "Всегда на связи! 💬\n\n"
            f"📣 Мой Telegram-канал: {self.settings.galina_channel_link}\n"
            f"✉️ Мой личный Telegram: @{u}\n"
            f"🌐 Официальный сайт компании: {self.settings.official_site}\n"
            f"✍️ Мой личный сайт с блогом: {self.settings.my_site}\n"
            f"🛒 Интернет-магазин: {self.settings.shop_catalog}\n"
            f"📞 Мой телефон: +7 913 958 6418\n"
        )
        await self._reply_section(update, text, contacts_inline(self.settings))

    async def route_main_menu_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """Пункты главного меню по callback_data (кроме «Что беспокоит?» — там ConversationHandler)."""
        q = update.callback_query
        if not q or not q.data:
            return
        routes = {
            CB_ABOUT_ME: self.show_about_me,
            CB_ABOUT_COMPANY: self.show_about_company,
            CB_ABOUT_PRODUCT: self.show_about_product,
            CB_CERT: self.show_certificates,
            CB_GEO: self.show_geography,
            CB_REG: self.show_registration,
            CB_PRICES: self.show_prices,
            CB_CONTACTS: self.show_contacts,
        }
        fn = routes.get(q.data)
        if fn:
            await fn(update, context)
        else:
            await q.answer()

    async def concern_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        del context
        text = (
            "💬 Что тебя беспокоит?\n\n"
            "Здоровье — это главное. 🌱 Расскажи, что именно тебя беспокоит? "
            "Напиши в следующем сообщении — я (или моя команда) отвечу лично.\n\n"
            "А пока можешь посмотреть каталог продукции, чтобы понять, какие натуральные "
            f"компоненты могут помочь в твоей ситуации: {self.settings.shop_catalog}"
        )
        await self._reply_section(update, text, shop_and_contact_inline(self.settings))
        return WAITING_FOR_CONCERN

    async def concern_receive(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if not update.message:
            return ConversationHandler.END

        text = (update.message.text or "").strip()
        key = norm_menu_text(text)
        if key in self._menu_handlers:
            result = await self._menu_handlers[key](update, context)
            if result == WAITING_FOR_CONCERN:
                return WAITING_FOR_CONCERN
            return ConversationHandler.END

        user = update.effective_user
        concern_text = text
        forward_text = (
            "📩 Новое обращение от пользователя!\n\n"
            f"👤 Имя: {user.full_name if user else 'неизвестно'}\n"
            f"🆔 Username: @{user.username if user and user.username else 'нет'}\n"
            f"🔗 ID: {user.id if user else 'нет'}\n\n"
            f"💬 Сообщение:\n{concern_text}"
        )

        galina_notified = True
        try:
            await context.bot.send_message(
                chat_id=self.settings.galina_chat_id,
                text=forward_text,
            )
        except Exception:
            logger.exception("Failed to forward concern to Galina")
            galina_notified = False

        if galina_notified:
            reply = (
                "Спасибо, что поделился(-ась)! 🌱 Я получила твоё сообщение и скоро свяжусь с тобой лично.\n\n"
                "Если хочешь написать напрямую прямо сейчас — вот моя личка:\n"
                f"{self.settings.galina_telegram_link}"
            )
        else:
            reply = (
                "Спасибо за сообщение! Сейчас возникла техническая проблема с автоотправкой.\n"
                "Напиши мне напрямую в личку, чтобы я точно увидела твой запрос:\n"
                f"{self.settings.galina_telegram_link}"
            )

        await update.message.reply_text(reply, reply_markup=shop_and_contact_inline(self.settings))
        return ConversationHandler.END

    async def concern_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        del context
        await self._send_main_menu(update, "Хорошо, возвращаемся в главное меню. 🏠")
        return ConversationHandler.END

    async def back_to_menu_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        del context
        if not update.callback_query:
            return
        await update.callback_query.answer()
        if update.callback_query.message:
            if self._menu_photo_path.exists():
                with self._menu_photo_path.open("rb") as image:
                    await update.callback_query.message.reply_photo(
                        photo=image,
                        caption="Выбирай, что тебя интересует 👇",
                        reply_markup=self._main_menu,
                    )
            else:
                await update.callback_query.message.reply_text(
                    "Выбирай, что тебя интересует 👇",
                    reply_markup=self._main_menu,
                )

    async def unknown_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        del context
        text = (
            "Пожалуйста, воспользуйся кнопками меню, чтобы я могла помочь тебе быстрее. 👇\n\n"
            f"Если у тебя личный вопрос — напиши мне в личку: {self.settings.galina_telegram_link}"
        )
        await self._send_main_menu(update, text)


def register_handlers(app: Application, settings: Settings) -> None:
    handlers = BotHandlers(settings)

    concern_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(handlers.concern_start, pattern=f"^{CB_CONCERN}$"),
            MessageHandler(
                filters.TEXT & ~filters.COMMAND & ExactReplyButtonText(CONCERN),
                handlers.concern_start,
            ),
        ],
        states={
            WAITING_FOR_CONCERN: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.concern_receive),
            ]
        },
        fallbacks=[CommandHandler("cancel", handlers.concern_cancel)],
    )

    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(concern_conv)
    app.add_handler(
        CallbackQueryHandler(handlers.route_main_menu_callback, pattern=MENU_CALLBACK_PATTERN)
    )

    menu_routes = {
        ABOUT_ME: handlers.show_about_me,
        ABOUT_COMPANY: handlers.show_about_company,
        ABOUT_PRODUCT: handlers.show_about_product,
        CERTIFICATES: handlers.show_certificates,
        GEOGRAPHY: handlers.show_geography,
        REGISTRATION: handlers.show_registration,
        PRICES: handlers.show_prices,
        CONTACTS: handlers.show_contacts,
    }
    handlers._menu_handlers = {
        norm_menu_text(k): v for k, v in {**menu_routes, CONCERN: handlers.concern_start}.items()
    }
    for button, callback in menu_routes.items():
        app.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND & ExactReplyButtonText(button),
                callback,
            )
        )

    app.add_handler(CallbackQueryHandler(handlers.back_to_menu_callback, pattern=f"^{BACK_TO_MENU_CALLBACK}$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.unknown_text))

