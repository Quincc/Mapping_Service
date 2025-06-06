"""
Физическое сохранение загружаемых файлов.

Поддерживаются **два источника**:

1. **multipart-форма** (UI, cURL)     → `store_local_file`
2. **объект в S3-совместимом хранилище** → `store_s3_object`

Сохраняем файлы в `<UPLOAD_DIR>/<project_id>/` под уникальным именем
(`UUID + оригинальное_расширение`) и сразу публикуем событие
`file_received`, чтобы пайплайн или мониторинг могли отреагировать.
"""
import uuid, shutil, aiofiles
from pathlib import Path
import boto3, botocore
from fastapi import UploadFile
from .utils import publish_event
from core import settings

# допустимые расширения (напр. ".csv,.xlsx,.json")
ALLOWED = {ext.strip().lower() for ext in settings.ALLOWED_EXT.split(",")}

# ---------- multipart ----------
async def store_local_file(project_id: str, file: UploadFile) -> Path:
    """
    Сохраняет файл, пришедший multipart-формой, и возвращает абсолютный
    путь до него.

    Args:
        project_id: UUID проекта (каталог внутри UPLOAD_DIR)
        file:       объект UploadFile от FastAPI

    Raises:
        ValueError: если тип файла не из разрешённого списка.

    Side-effects:
        • создает директории (parents=True)
        • логирует событие 'file_received'
    """
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED:
        raise ValueError("unsupported_file_type")

    dest_dir = Path(settings.UPLOAD_DIR) / project_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{uuid.uuid4()}{ext}"

    async with aiofiles.open(dest, "wb") as out:
        while chunk := await file.read(1024 * 1024):
            await out.write(chunk)

    await publish_event("file_received", {"project_id": project_id, "path": str(dest)})
    return dest

# ---------- S3 ----------
# сессия и клиент инициализируем один раз — boto3 потокобезопасен
_session = boto3.session.Session()
_s3 = _session.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT,
    region_name=settings.S3_REGION,
    aws_access_key_id=settings.S3_KEY,
    aws_secret_access_key=settings.S3_SECRET,
)

async def store_s3_object(project_id: str, bucket: str, key: str) -> Path:
    """
    Копирует объект из S3 и кладёт в локальный UPLOAD_DIR.

    Args:
        project_id: UUID проекта
        bucket:     имя S3-бакета
        key:        ключ объекта (path/to/file.csv)

    Raises:
        RuntimeError: если возникла ошибка S3-клиента.

    Returns:
        Путь до сохранённого файла.
    """
    dest_dir = Path(settings.UPLOAD_DIR) / project_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{uuid.uuid4()}_{Path(key).name}"

    try:
        obj = _s3.get_object(Bucket=bucket, Key=key)
        with dest.open("wb") as f:
            shutil.copyfileobj(obj["Body"], f)
    except botocore.exceptions.ClientError as e:
        raise RuntimeError(f"S3 error: {e}")

    await publish_event("file_received", {"project_id": project_id, "path": str(dest)})
    return dest
