from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.project.db import AsyncSessionLocal
from app.project.crud import get_project     # <- уже есть
import json

PROJECTS_FILE = Path("config") / "projects.json"

class ProjectNotFound(Exception):
    """Проект не найден в projects.json."""


async def get_project_api_key(project_id: str) -> str:
    """
    Вернёт API-ключ проекта или бросит ProjectNotFound.
    Читает файл формата:
    [
      {"id": "demo", "api_key": "secret"},
      {"id": "proj2", "api_key": "abcd1234"}
    ]
    """
    async with AsyncSessionLocal() as db:
        proj = await get_project(db, project_id)
    if not proj:
        raise ProjectNotFound(f"project {project_id} not found")
    return proj.api_key
