"""
Хелпер для UI-страницы маппинга.

Берёт _заголовок_ самого нового файла проекта и возвращает первые N
колонок (чтобы не грузить большой CSV в браузер).
"""
from pathlib import Path
import pandas as pd
import structlog

from core.settings import settings
from app.parser.readers  import parse_file
from app.mapping.storage import load_config
from app.mapping.engine  import apply_mapping

log = structlog.get_logger()


# ---------- внутренний помощник ----------
def _latest_file(project_id: str) -> Path | None:
    """
    Возвращает самый «свежий» файл проекта или None,
    если каталог пуст / не создан.
    """
    upload_dir = Path(settings.UPLOAD_DIR) / project_id
    if not upload_dir.exists():
        return None

    files = list(upload_dir.glob("*.*"))
    return max(files, key=lambda p: p.stat().st_mtime) if files else None


# ---------- API для шаблона UI ----------
def get_sample_columns(project_id: str, limit: int = 50) -> list[str]:
    """
    Args:
        project_id: UUID проекта
        limit:      макс. число колонок вернуть (защита UI)

    Returns:
        Список названий колонок (в оригинальном регистре).

    Возвращает первые `limit` названий столбцов из последнего загруженного файла.
    Если файлов нет — отдаёт пустой список.
    """
    latest = _latest_file(project_id)
    if latest is None:
        return []

    # читаем только заголовок
    df = pd.read_csv(latest, nrows=0)
    return df.columns.tolist()[:limit]


# ---------- API для кнопки "Отправить" ----------
def get_dataframe_last(project_id: str) -> pd.DataFrame | None:
    """
    1. Берёт последний файл проекта.
    2. Читает его любым поддерживаемым парсером.
    3. Применяет маппинг, если он сохранён.
    4. Возвращает DataFrame или None.
    """
    latest = _latest_file(project_id)
    if latest is None:
        return None

    log.info("preview.latest_file", project_id=project_id, file=str(latest))

    df = parse_file(latest)

    # применяем маппинг, если есть
    try:
        cfg = load_config(project_id)
        df = apply_mapping(df, cfg)
        log.info("preview.mapped", cols=list(df.columns))
    except FileNotFoundError:
        log.warning("preview.mapping_not_found", project_id=project_id)

    return df
