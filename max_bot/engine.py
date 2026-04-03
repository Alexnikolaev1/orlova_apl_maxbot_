"""Обработка обновлений MAX: те же сценарии, что у Telegram-бота."""

from __future__ import annotations

import logging
from typing import Any

from bot.settings import Settings

from max_bot.client import MaxApiClient
from max_bot import galina as g

logger = logging.getLogger(__name__)

# Ожидание текста для «Что тебя беспокоит?» (как ConversationHandler в Telegram)
_concern_user_ids: set[int] = set()

# Кэш токена загруженного фото меню (на инстансе процесса)
_menu_image_token: str | None = None


def resolve_outgoing_target(update: dict) -> tuple[int | None, int | None]:
    """Кому отвечать: user_id и/или chat_id для POST /messages."""
    ut = update.get("update_type")
    if ut == "bot_started":
        u = update.get("user") or {}
        uid = u.get("user_id")
        if uid is not None:
            return (int(uid), None)
        cid = update.get("chat_id")
        if cid is not None:
            return (None, int(cid))
        return (None, None)

    if ut == "message_callback":
        cb = update.get("callback") or {}
        u = cb.get("user") or {}
        uid = u.get("user_id")
        if uid is not None:
            return (int(uid), None)

    msg = update.get("message") or {}
    sender = msg.get("sender") or {}
    if not sender.get("is_bot") and sender.get("user_id") is not None:
        return (int(sender["user_id"]), None)

    rec = msg.get("recipient") or {}
    if rec.get("user_id") is not None:
        return (int(rec["user_id"]), None)
    if rec.get("chat_id") is not None:
        return (None, int(rec["chat_id"]))
    return (None, None)


def _sender_name(sender: dict) -> str:
    fn = (sender.get("first_name") or "").strip()
    ln = (sender.get("last_name") or "").strip()
    name = f"{fn} {ln}".strip()
    if name:
        return name
    return (sender.get("name") or "неизвестно").strip()


async def _send(
    client: MaxApiClient,
    *,
    user_id: int | None,
    chat_id: int | None,
    text: str,
    attachments: list[dict[str, Any]] | None = None,
) -> None:
    await client.send_message(user_id=user_id, chat_id=chat_id, text=text, attachments=attachments)


async def _send_main_menu(
    client: MaxApiClient,
    settings: Settings,
    *,
    user_id: int | None,
    chat_id: int | None,
    caption: str,
) -> None:
    global _menu_image_token
    path = g.menu_photo_path()
    attachments: list[dict[str, Any]] = [g.attachment_main_menu()]
    if path.exists():
        try:
            if not _menu_image_token:
                _menu_image_token = await client.upload_image_file(path)
            attachments.insert(
                0,
                {"type": "image", "payload": {"token": _menu_image_token}},
            )
        except Exception:
            logger.exception("MAX: не удалось загрузить фото меню, отправляю только текст")
    await _send(client, user_id=user_id, chat_id=chat_id, text=caption, attachments=attachments)


async def _route_menu_payload(
    payload: str,
    client: MaxApiClient,
    settings: Settings,
    *,
    user_id: int | None,
    chat_id: int | None,
    welcome_name: str = "друг",
) -> None:
    if user_id is not None:
        _concern_user_ids.discard(user_id)

    if payload == g.CB_MAIN:
        await _send_main_menu(
            client,
            settings,
            user_id=user_id,
            chat_id=chat_id,
            caption=g.text_welcome(welcome_name),
        )
        return

    mapping: dict[str, tuple[str, list[dict[str, Any]]]] = {
        g.CB_ABOUT_ME: (g.text_about_me(settings), [g.attachment_channel_and_menu(settings)]),
        g.CB_ABOUT_COMPANY: (g.text_about_company(), [g.attachment_back_only()]),
        g.CB_ABOUT_PRODUCT: (g.text_about_product(settings), [g.attachment_shop_and_contact(settings)]),
        g.CB_CERT: (g.text_certificates(settings), [g.attachment_back_only()]),
        g.CB_GEO: (g.text_geography(), [g.attachment_back_only()]),
        g.CB_REG: (g.text_registration(), [g.attachment_register(settings)]),
        g.CB_PRICES: (g.text_prices(settings), [g.attachment_shop_and_contact(settings)]),
        g.CB_CONTACTS: (g.text_contacts(settings), [g.attachment_shop_and_contact(settings)]),
    }

    if payload == g.CB_CONCERN:
        if user_id is not None:
            _concern_user_ids.add(user_id)
        await _send(
            client,
            user_id=user_id,
            chat_id=chat_id,
            text=g.text_concern_start(settings),
            attachments=[g.attachment_shop_and_contact(settings)],
        )
        return

    if payload in mapping:
        text, ats = mapping[payload]
        await _send(client, user_id=user_id, chat_id=chat_id, text=text, attachments=ats)
        return


async def process_max_update(update: dict, settings: Settings, client: MaxApiClient) -> None:
    """Точка входа для одного JSON Update от MAX (webhook или long polling)."""
    ut = update.get("update_type")
    user_id, chat_id = resolve_outgoing_target(update)

    if ut == "bot_started":
        u = update.get("user") or {}
        first = (u.get("first_name") or "друг").strip() or "друг"
        await _send_main_menu(
            client,
            settings,
            user_id=user_id,
            chat_id=chat_id,
            caption=g.text_welcome(first),
        )
        return

    if ut == "message_callback":
        cb = update.get("callback") or {}
        payload = cb.get("payload")
        u = cb.get("user") or {}
        wname = ((u.get("first_name") or "друг").strip() or "друг")
        if isinstance(payload, str):
            await _route_menu_payload(
                payload,
                client,
                settings,
                user_id=user_id,
                chat_id=chat_id,
                welcome_name=wname,
            )
        return

    if ut != "message_created":
        return

    msg = update.get("message") or {}
    sender = msg.get("sender") or {}
    if sender.get("is_bot"):
        return

    body = msg.get("body") or {}
    text = (body.get("text") or "").strip()
    uid = int(sender.get("user_id") or 0)

    if not text and uid not in _concern_user_ids:
        return

    if uid in _concern_user_ids and text and not text.startswith("/"):
        _concern_user_ids.discard(uid)
        uname = sender.get("username")
        forward = g.text_forward_concern(
            _sender_name(sender),
            uname if isinstance(uname, str) else None,
            uid,
            text,
        )
        ok = True
        try:
            await client.send_message(
                user_id=settings.galina_chat_id,
                text=forward,
            )
        except Exception:
            logger.exception("MAX: пересылка обращения владельцу")
            ok = False

        reply = g.text_concern_ok(settings) if ok else g.text_concern_fail(settings)
        await _send(
            client,
            user_id=user_id,
            chat_id=chat_id,
            text=reply,
            attachments=[g.attachment_shop_and_contact(settings)],
        )
        return

    lower = text.lower()
    if lower.startswith("/cancel"):
        _concern_user_ids.discard(uid)
        await _send_main_menu(
            client,
            settings,
            user_id=user_id,
            chat_id=chat_id,
            caption=g.text_cancel_menu(),
        )
        return

    if lower.startswith("/start") or text in g.LABEL_TO_CB:
        pl = g.LABEL_TO_CB.get(text)
        if pl:
            await _route_menu_payload(pl, client, settings, user_id=user_id, chat_id=chat_id)
            return
        fn = (sender.get("first_name") or "друг").strip() or "друг"
        await _send_main_menu(
            client,
            settings,
            user_id=user_id,
            chat_id=chat_id,
            caption=g.text_welcome(fn),
        )
        return

    await _send_main_menu(
        client,
        settings,
        user_id=user_id,
        chat_id=chat_id,
        caption=g.text_unknown(settings),
    )
