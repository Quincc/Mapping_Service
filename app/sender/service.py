"""
Функция верхнего уровня `send_dataframe`.
Принимает pandas.DataFrame + идентификаторы проекта,
преобразует в JSON и вызывает client.send_json().
"""
import pandas as pd, orjson, structlog
from .client   import post_json
from .schemas  import SendResult
from .constants import DEFAULT_ENDPOINT, HDR_PROJECT, HDR_APIKEY

log = structlog.get_logger()

async def send_dataframe(df: pd.DataFrame, project_id: str, api_key: str,
                         url: str = DEFAULT_ENDPOINT) -> SendResult:
    """Отправляет DataFrame как JSON‑массив.

    * **ok=True**  → сервер вернул 2xx;
    * **ok=False** → были network‑ошибки или 4xx/5xx после retry.
    """
    payload = orjson.loads(df.to_json(orient="records"))
    headers = {HDR_PROJECT: project_id, HDR_APIKEY: api_key}

    attempts = 0
    try:
        resp = await post_json(url, payload, headers)
        attempts = resp.num_traces if hasattr(resp, "num_traces") else 1
        return SendResult(status_code=resp.status_code, ok=True,
                          attempts=attempts, response=resp.text[:200])
    except Exception as exc:
        log.error("send_failed", error=str(exc))
        return SendResult(status_code=getattr(exc, "status_code", 0),
                          ok=False, attempts=attempts or 3,
                          response=str(exc)[:200])

async def send_dataframe_local(df: pd.DataFrame):
     df.to_json("saves/save1.json", index=False)