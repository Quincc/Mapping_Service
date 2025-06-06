"""
ORM-модель + Pydantic-схемы для “Project”.

* **SQLAlchemy** ─ структура таблицы `projects`
* **Pydantic**    ─ входящие/исходящие DTO для API
"""
import uuid, secrets
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, UTC

from .db import Base
from pydantic import BaseModel, Field

# ---------- SQLAlchemy ----------
class Project(Base):
    """
    Таблица проектов маппинга.

    * `id`         – UUID в строковом виде (PK)
    * `name`       – уникальное человекочитаемое имя
    * `description`– опциональный текст
    * `api_key`    – токен, который кладётся в заголовок при отправке
    * `created_at` – время создания (UTC, TZ-aware)
    """
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str | None]
    api_key: Mapped[str] = mapped_column(String, nullable=False, default=lambda: secrets.token_hex(16))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )

# ---------- Pydantic ----------
class ProjectCreate(BaseModel):
    """JSON-тело запроса при создании проекта (POST /projects/)."""

    name: str
    description: str | None = None

class ProjectCreated(ProjectCreate):
    """
    Ответ API при успешном создании.

    * `api_key` возвращается один раз – покажите и сохраните.
    """

    id: str
    created_at: datetime
    api_key: str

    model_config = {"from_attributes": True}

class ProjectRead(BaseModel):
    """DTO для выдачи проекта в GET-эндпоинтах."""

    id: str
    name: str
    description: str | None
    created_at: datetime
    api_key: str