"""
Инициализация БД модуля «Управление проектами».

* Асинхронный движок (`AsyncEngine`) для единообразия со всем приложением.
* `init_models()` вызывается на старте приложения и создаёт таблицы,
  если их ещё нет (замена Alembic-миграциям в прототипе).
"""
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.settings import settings

# если переменная окружения DB_PATH не задана — кладём БД рядом с кодом
DB_PATH = getattr(settings, "DB_PATH", "mapping.db")
DATABASE_URL = f"sqlite+aiosqlite:///{DB_PATH}"

engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


async def init_models():
    """
       Создать все таблицы (idempotent).

       Важно: импорт `app.project.models` внутри функции,
       чтобы избежать циклической зависимости при старте.
       """
    async with engine.begin() as conn:
        from app.project import models
        await conn.run_sync(Base.metadata.create_all)