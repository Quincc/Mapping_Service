"""
Функции доступа к данным (CRUD) для Project.

Вызовов немного, поэтому без отдельного репозитория/сервиса.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Project, ProjectCreate

async def create_project(db: AsyncSession, data: ProjectCreate) -> Project:
    """
    Создать проект.

    Бросает `IntegrityError`, если name уже существует – роутер ловит и
    отдаёт 409 Conflict.
    """
    project = Project(name=data.name, description=data.description)
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project

async def list_projects(db: AsyncSession) -> list[Project]:
    """Вернуть все проекты без пагинации (MVP)."""
    res = await db.execute(select(Project))
    return res.scalars().all()

async def get_project(db: AsyncSession, project_id: str) -> Project | None:
    """Найти проект по UUID (или None)."""
    return await db.get(Project, project_id)

async def delete_project(db: AsyncSession, project_id: str) -> None:
    """
    Удалить проект.

    *Вызывается только после авторизации владельца
    (см. зависимость `get_current_project`).*
    """
    proj = await db.get(Project, project_id)
    if proj:
        await db.delete(proj)
        await db.commit()
