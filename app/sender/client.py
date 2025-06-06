"""
HTTP‑клиент на основе **httpx.AsyncClient** с автоматическими
ретраями через библиотеку **backoff**.

Зачем отдельный файл?
* Чётко отделяем логику сетевого взаимодействия от бизнес‑кода.
* У нас единая точка, где настроены таймауты, заголовки и backoff‑политика.
"""
import httpx, asyncio, backoff
from typing import Any
from core.settings import settings
from .constants import HDR_PROJECT, HDR_APIKEY

TIMEOUT = httpx.Timeout(10.0, connect=5.0)

# экспоненциальный back-off до 3 повторов
def give_up(exc):
    return isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code < 500

@backoff.on_exception(backoff.expo, (httpx.TransportError, httpx.HTTPStatusError),
                      max_tries=3, giveup=give_up)
async def post_json(url: str, json_: Any, headers: dict[str, str]) -> httpx.Response:
    async with httpx.AsyncClient(http2=True, timeout=TIMEOUT) as client:
        resp = await client.post(url, json=json_, headers=headers)
        resp.raise_for_status()
        return resp
