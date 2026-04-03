"""HTTP client for MAX Bot API (https://dev.max.ru/docs-api)."""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)

BASE_URL = "https://platform-api.max.ru"


class MaxApiClient:
    def __init__(self, access_token: str) -> None:
        self._token = access_token
        self._headers = {"Authorization": access_token}

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=BASE_URL, headers=self._headers, timeout=60.0)

    async def send_message(
        self,
        *,
        user_id: int | None = None,
        chat_id: int | None = None,
        text: str | None = None,
        attachments: list[dict[str, Any]] | None = None,
        fmt: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if user_id is not None:
            params["user_id"] = user_id
        if chat_id is not None:
            params["chat_id"] = chat_id
        body: dict[str, Any] = {}
        if text is not None:
            body["text"] = text
        if attachments:
            body["attachments"] = attachments
        if fmt:
            body["format"] = fmt

        async with self._client() as c:
            last_exc: Exception | None = None
            for attempt in range(5):
                r = await c.post("/messages", params=params, json=body)
                try:
                    data = r.json()
                except json.JSONDecodeError:
                    r.raise_for_status()
                    return {}
                if r.status_code == 200:
                    return data
                code = (data or {}).get("code") if isinstance(data, dict) else None
                if code == "attachment.not.ready":
                    delay = 0.5 * (2**attempt)
                    logger.warning("MAX attachment not ready, retry in %ss", delay)
                    await asyncio.sleep(delay)
                    continue
                last_exc = httpx.HTTPStatusError(
                    f"MAX API {r.status_code}: {data}",
                    request=r.request,
                    response=r,
                )
                break
            if last_exc:
                raise last_exc
            r.raise_for_status()
            return {}

    async def get_updates(
        self,
        *,
        marker: int | None = None,
        limit: int = 100,
        timeout: int = 30,
        types: list[str] | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"limit": limit, "timeout": timeout}
        if marker is not None:
            params["marker"] = marker
        if types:
            params["types"] = ",".join(types)
        async with self._client() as c:
            r = await c.get("/updates", params=params)
            r.raise_for_status()
            return r.json()

    async def set_subscription(
        self,
        webhook_url: str,
        update_types: list[str],
        secret: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"url": webhook_url, "update_types": update_types}
        if secret:
            body["secret"] = secret
        async with self._client() as c:
            r = await c.post("/subscriptions", json=body)
            if r.status_code >= 400:
                try:
                    detail = r.json()
                except json.JSONDecodeError:
                    detail = r.text
                raise RuntimeError(f"MAX subscriptions {r.status_code}: {detail}")
            try:
                return r.json()
            except json.JSONDecodeError:
                return {"ok": True}

    async def upload_image_file(self, path: Path) -> str:
        """Upload local image; returns attachment token for messages."""
        async with self._client() as c:
            r = await c.post("/uploads", params={"type": "image"})
            r.raise_for_status()
            meta = r.json()
        upload_url = meta.get("url")
        if not upload_url:
            raise RuntimeError(f"MAX uploads: no url in response: {meta}")

        data = path.read_bytes()
        async with httpx.AsyncClient(timeout=120.0) as up:
            resp = await up.post(
                upload_url,
                files={"data": (path.name, data, "application/octet-stream")},
            )
        resp.raise_for_status()
        try:
            done = resp.json()
        except json.JSONDecodeError:
            raise RuntimeError(f"MAX upload: bad JSON: {resp.text[:500]}") from None
        token = done.get("token") or meta.get("token")
        if not token:
            raise RuntimeError(f"MAX upload: no token in {done}")
        return str(token)
