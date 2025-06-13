"""
Сквозной асинхронный ETL-конвейер:

    1. parse_file      – raw → DataFrame
    2. apply_mapping   – DataFrame → нормализованные колонки
    3. check_dataframe – контроль качества → issues / report.csv
    4. send_dataframe  – POST в внешний сервис (с ретраями)

Ошибки на любом шаге логируются и «пробрасываются» наружу,
чтобы фоновая задача `launch_pipeline` могла опубликовать
`file_failed` и поднять алёрт.
"""
from pathlib import Path
import structlog
import pandas as pd

from app.parser.readers  import parse_file
from app.mapping.storage import load_config
from app.mapping.engine  import apply_mapping
from app.quality.checker import check_dataframe
from app.quality.storage import save_report
from app.sender.service  import send_dataframe, send_dataframe_local
from app.auth.project    import get_project_api_key

log = structlog.get_logger()

async def run_full_pipeline(project_id: str, file_path: str):
    """
    Выполняет все шаги для одного файла.

    Возвращает объект SendResult (ok / attempts / status_code).
    """
    path = Path(file_path)
    log.info("pipeline.start", project_id=project_id, file=file_path)

    # 1) Парсинг
    df: pd.DataFrame = parse_file(path)
    log.info("pipeline.parsed", rows=len(df))

    # 2) Маппинг
    try:
        cfg = load_config(project_id)
        df = apply_mapping(df, cfg)
        log.info("pipeline.mapped", cols=list(df.columns))
    except FileNotFoundError:
        log.warning("mapping_not_found", project_id=project_id)

    # 3) Контроль качества
    qc = check_dataframe(df)
    if qc.issues:
        rep = save_report(project_id, qc)
        log.warning("pipeline.quality_issues", count=len(qc.issues), report=str(rep))
    else:
        log.info("pipeline.quality_ok")

    # 4) Отправка наружу
    api_key = await get_project_api_key(project_id)          # достаём ваш ключ проекта
    send_res = await send_dataframe(df, project_id, api_key)
    res = await send_dataframe_local(df)
    if send_res.ok:
        log.info("pipeline.sent", status=send_res.status_code, attempts=send_res.attempts)
    else:
        log.error("pipeline.send_failed", status=send_res.status_code, attempts=send_res.attempts)

    log.info("pipeline.done", project_id=project_id, file=file_path)
