"""
Фоновая задача, которая запускает полный ETL-пайплайн.

Смысл слоя:
* роутер знает только о `launch_pipeline`
* здесь можно ловить исключения, публиковать события,
  собирать метрики — не трогая логику самого ETL.
"""
from .utils import publish_event
from app.parser.pipeline import run_full_pipeline   # ← ваш модуль парсинга/валидации

async def launch_pipeline(project_id: str, file_path: str):
    """
        Запускаем ETL и публикуем событие о результате.

        NB: Не ретраим здесь — ретрай лучше делать в самом
            `run_full_pipeline` на отдельных шагах.
        """
    try:
        await run_full_pipeline(project_id, file_path)
        await publish_event("file_processed", {"project_id": project_id, "file": file_path})
    except Exception as exc:
        # логируем, чтобы можно было алёртить
        await publish_event("file_failed", {"project_id": project_id, "file": file_path, "error": str(exc)})
        raise
