"""
Ручной запуск отправки из UI‑страницы маппинга.
Потребуется, если пользователь хочет переотправить данные
из последнего загруженного файла проекта.
"""
from fastapi import APIRouter, Depends, HTTPException
from app.project.auth import get_current_project
from app.parser.preview import get_dataframe_last
from .service import send_dataframe
from .schemas  import SendResult

router = APIRouter(prefix="/send", tags=["sender"])

@router.post("/manual", response_model=SendResult)
async def send_manual(project = Depends(get_current_project)):
    df = get_dataframe_last(project.id)
    if df is None:
        raise HTTPException(404, "no_data")
    api_key = project.api_key
    result = await send_dataframe(df, project.id, api_key)
    return result
