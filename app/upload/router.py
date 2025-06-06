"""
Эндпоинты загрузки файла.

* `POST /upload/local` — форма multipart (из UI) или cURL
* В ответе 201 + путь сохранённого файла
"""
from fastapi import APIRouter, BackgroundTasks, UploadFile, File, Depends, HTTPException, status
from app.project.auth import get_current_project
from .service import store_local_file, store_s3_object
from .schemas import UploadResponse
from .tasks import launch_pipeline

router = APIRouter(prefix="/upload", tags=["upload"])

# локальный upload
@router.post("/local", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_local(
    bg: BackgroundTasks,
    project = Depends(get_current_project),
    file: UploadFile = File(...)
):
    """
        Сохраняем файл в локальную ФС и отстреливаем фоновую задачу.

        • Авторизация идёт через заголовки (`get_current_project`).
        • Событие `file_received` пишем синхронно, чтобы гарантировать
          наличие записи, даже если фон не запустится.
        """
    try:
        saved_path = await store_local_file(project.id, file)
    except ValueError:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "unsupported_file_type")

    bg.add_task(launch_pipeline, project.id, str(saved_path))  # ⬅ парсинг/валидация
    return UploadResponse(path=str(saved_path))

# S3
@router.post("/s3/{bucket}/{key:path}", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_s3(
    bg: BackgroundTasks,
    bucket: str,
    key: str,
    project = Depends(get_current_project),
):
    saved_path = await store_s3_object(project.id, bucket, key)
    bg.add_task(launch_pipeline, project.id, str(saved_path))
    return UploadResponse(path=str(saved_path))
