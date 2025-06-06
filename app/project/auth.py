"""
Зависимости FastAPI для доступа к БД и авторизации проекта.
"""
from fastapi import Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .db import AsyncSessionLocal
from .crud import get_project

async def get_db():
    """Yield-контекст для асинхронной сессии."""
    async with AsyncSessionLocal() as session:
        yield session

async def get_current_project(
    x_project_id: str = Header(..., alias="X-PROJECT-ID"),
    x_api_key:   str = Header(..., alias="X-API-KEY"),
    db: AsyncSession = Depends(get_db),
):
    """
    Проверка заголовков авторизации.

    • 403, если проект не найден или ключ не совпал.
    • Возвращает объект `Project`, чтобы эндпоинты не делали лишний select.
    """
    proj = await get_project(db, x_project_id)
    if not proj or proj.api_key != x_api_key:
        raise HTTPException(403, "invalid credentials")
    return proj