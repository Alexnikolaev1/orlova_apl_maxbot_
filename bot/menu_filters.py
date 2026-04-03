"""Фильтры для точного совпадения текста reply-кнопок (Unicode NFC)."""

from __future__ import annotations

import unicodedata

from telegram import Message
from telegram.ext.filters import MessageFilter


def norm_menu_text(s: str | None) -> str:
    """Нормализация как у клиентов Telegram (эмодзи + кириллица)."""
    return unicodedata.normalize("NFC", (s or "").strip())


class ExactReplyButtonText(MessageFilter):
    """Сообщение ровно равно подписи кнопки главного меню (после NFC)."""

    __slots__ = ("_norm",)

    def __init__(self, label: str) -> None:
        super().__init__(name=f"ExactReplyButton({label[:32]!r})")
        self._norm = norm_menu_text(label)

    def filter(self, message: Message) -> bool:
        if not message.text:
            return False
        return norm_menu_text(message.text) == self._norm
