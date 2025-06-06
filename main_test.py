from pathlib import Path
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi import HTTPException, Query
from app.project.db import AsyncSessionLocal
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

# ─── Инициализация БД ────────────────────────────────────────────────────────────
from app.project.db import init_models

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# ────────────────────────────── FABRIC ───────────────────────────────────────────
def create_app() -> FastAPI:
    app = FastAPI(title="Mapping Service")

    # 1. Роутеры
    app.include_router(upload_router)
    app.include_router(mapping_router)
    app.include_router(quality_router)
    app.include_router(sender_router)
    app.include_router(project_router)

    # 2. Startup-хук → создаём таблицы один раз при запуске
    @app.on_event("startup")
    async def _startup() -> None:
        await init_models()

    # 3. UI-страницы
    @app.get("/upload", response_class=HTMLResponse, tags=["ui"])
    async def upload_page(
            request: Request,
            project_id: str = Query(...),
            api_key: str = Query(...),
    ):
        # ── лёгкая проверка, чтобы не подсунули чужой id/key ──
        async with AsyncSessionLocal() as db:
            proj = await get_project(db, project_id)
        if not proj or proj.api_key != api_key:
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
        project = Depends(get_current_project),
    ):
        cols = get_sample_columns(project.id)
        return templates.TemplateResponse(
            "mapping.html",
            {
                "request": request,
                "project_id": project.id,
                "api_key": project.api_key,
                "sample_columns": cols,
            },
        )

    # 4. Редирект с корня
    @app.get("/", include_in_schema=False)
    async def root():
        return RedirectResponse(url="/upload")

    return app


app = create_app()
