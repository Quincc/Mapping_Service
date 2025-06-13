"""
REST-эндпойнты модуля «Mapping» отвечают за получение и сохранение конфигурации маппинга данных.

GET  /mapping/  — вернуть текущий JSON-конфиг
PUT  /mapping/  — сохранить конфиг из UI-формы (плоский JSON от HTMX)

Авторизация по заголовкам X-PROJECT-ID и X-API-KEY.
Конфиги хранятся в файле config/<project_id>.json
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.project.auth import get_current_project
from .schemas import MappingConfig
from .storage import save_config, load_config, cfg_path
import re

router = APIRouter(prefix="/mapping", tags=["mapping"])

@router.get(
    "/", response_model=MappingConfig,
    summary="Получить текущий конфиг маппинга"
)
async def get_cfg(project = Depends(get_current_project)):
    """
    Возвращает JSON-конфиг маппинга для проекта.
    Если конфиг не найден, возвращает 404 mapping_not_found.
    """
    if not cfg_path(project.id).exists():
        raise HTTPException(status_code=404, detail="mapping_not_found")
    return load_config(project.id)

@router.put(
    "/", response_model=MappingConfig,
    status_code=status.HTTP_201_CREATED,
    summary="Создать или обновить конфиг маппинга"
)
async def put_cfg(
    request: Request,
    project = Depends(get_current_project)
):
    """
    Принимает «плоский» JSON из HTMX-формы (ключи вида rules[i][field]),
    преобразует их в список правил, валидирует через Pydantic и сохраняет конфиг.
    """
    raw = await request.json()

    # Проверка project_id
    if raw.get("project_id") != project.id:
        raise HTTPException(status_code=400, detail="project_id_mismatch")

    # Парсим ключи rules[i][field]
    rules_dict: dict[int, dict] = {}
    for key, val in raw.items():
        match = re.match(r"rules\[(\d+)\]\[(\w+)\]", key)
        if not match:
            continue
        idx = int(match.group(1))
        field = match.group(2)
        rules_dict.setdefault(idx, {})[field] = val or None

    # Собираем отсортированный список правил
    rules = [rules_dict[i] for i in sorted(rules_dict)]

    # Валидируем и сохраняем конфиг
    cfg = MappingConfig(project_id=project.id, rules=rules)
    save_config(cfg)
    return cfg
