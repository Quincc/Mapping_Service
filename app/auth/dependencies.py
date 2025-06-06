from fastapi import Header, HTTPException
from pydantic import BaseModel

# Pydantic-модель проекта — пока только id и api_key
class Project(BaseModel):
    id: str
    api_key: str

async def get_current_project(
    x_project_id: str = Header(..., alias="X-PROJECT-ID"),
    x_api_key:   str = Header(..., alias="X-API-KEY"),
) -> Project:
    """
    Черновая проверка:
    • если id == 'demo' и ключ == 'secret' → ок
    • иначе 403
    Замените на запрос к БД, Redis, Keycloak — что понадобится.
    """
    if not (x_project_id == "demo" and x_api_key == "secret"):
        raise HTTPException(status_code=403, detail="invalid credentials")

    return Project(id=x_project_id, api_key=x_api_key)
