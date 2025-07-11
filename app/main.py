from pathlib import Path

from fastapi import FastAPI, Request, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.project.db import AsyncSessionLocal, init_models
from app.project.crud import get_project

# ─── REST-роутеры ────────────────────────────────────────────────────────────────
from app.upload.router   import router as upload_router
from app.mapping.router  import router as mapping_router
from app.quality.router  import router as quality_router
from app.sender.router   import router as sender_router
from app.project.router  import router as project_router

# ─── Авторизация и preview-helper ────────────────────────────────────────────────
from app.project.auth   import get_current_project
from app.parser.preview import get_sample_columns

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def create_app() -> FastAPI:
    app = FastAPI(title="Mapping Service")

    # 1. Подключаем все REST-роутеры
    app.include_router(upload_router)
    app.include_router(mapping_router)
    app.include_router(quality_router)
    app.include_router(sender_router)
    app.include_router(project_router)

    # 2. Создание таблиц при старте
    @app.on_event("startup")
    async def _startup() -> None:
        await init_models()

    # 3. UI-страницы

    @app.get("/upload", response_class=HTMLResponse, tags=["ui"])
    async def upload_page(
        request: Request,
        project_id: str = Query(..., description="UUID проекта"),
        api_key: str   = Query(..., description="API-ключ проекта"),
    ):
        """
        Страница загрузки файла.
        Ручная проверка project_id + api_key в URL:
          GET /upload?project_id=<id>&api_key=<key>
        """
        # ── Простая валидация: если отсутствует проект или ключ не совпадает, 403 ──
        async with AsyncSessionLocal() as db:
            proj = await get_project(db, project_id)
        if proj is None or proj.api_key != api_key:
            raise HTTPException(403, "invalid credentials")

        return templates.TemplateResponse(
            "upload.html",
            {
                "request": request,
                "project_id": project_id,
                "api_key": api_key,
            },
        )

    @app.get("/ui/mapping", response_class=HTMLResponse, tags=["ui"])
    async def mapping_page(
        request: Request,
        project_id: str = Query(..., description="UUID проекта"),
        api_key: str   = Query(..., description="API-ключ проекта"),
    ):
        # 1) валидация credentials вручную, как в upload_page
        async with AsyncSessionLocal() as db:
            proj = await get_project(db, project_id)
        if proj is None or proj.api_key != api_key:
            raise HTTPException(403, "invalid credentials")

        # 2) получаем колонки для первоначального рендера
        cols = get_sample_columns(project_id)

        return templates.TemplateResponse(
            "mapping.html",
            {
                "request": request,
                "project_id": project_id,
                "api_key": api_key,
                "sample_columns": cols,
            },
        )


    @app.get("/ui/quality", response_class=HTMLResponse, tags=["ui"])
    async def quality_page(
        request: Request,
        project = Depends(get_current_project),
    ):
        """
        Заглушка для страницы проверки качества.
        Если у вас появится шаблон quality.html — подключите здесь:
        """
        # Например, можно передать путь к отчёту, список столбцов и т.д.
        return templates.TemplateResponse(
            "quality.html",  # <-- создайте этот файл, если понадобится
            {
                "request": request,
                "project_id": project.id,
                "api_key": project.api_key,
            },
        )

    @app.get("/", include_in_schema=False)
    async def root():
        """
        Редирект на страницу загрузки.
        Пользователь должен добавить ?project_id=...&api_key=... вручную.
        """
        return RedirectResponse(url="/upload")

    return app


app = create_app()