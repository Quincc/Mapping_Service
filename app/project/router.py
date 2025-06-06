"""
REST-роуты модуля проектов.

prefix = /projects
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .crud import create_project, list_projects, get_project, delete_project
from .models import ProjectCreate, ProjectCreated, ProjectRead
from .auth import get_db, get_current_project

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", response_model=ProjectCreated, status_code=201)
async def create_(data: ProjectCreate, db: AsyncSession = Depends(get_db)):
    """Создать новый проект."""
    return await create_project(db, data)

@router.get("/", response_model=list[ProjectRead])
async def list_(db: AsyncSession = Depends(get_db)):
    """Список всех проектов (MVP без пагинации)."""
    return await list_projects(db)

@router.get("/{proj_id}", response_model=ProjectRead)
async def get_(proj_id: str, db: AsyncSession = Depends(get_db)):
    """Получить один проект по UUID (404, если нет)."""
    proj = await get_project(db, proj_id)
    if proj is None:
        raise HTTPException(404, "not found")
    return proj

@router.delete("/{proj_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_(proj_id: str,
                  _=Depends(get_current_project),   # только владелец может удалять
                  db: AsyncSession = Depends(get_db)):
    """Удалить проект (только владелец)."""
    await delete_project(db, proj_id)
