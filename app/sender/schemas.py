"""
Pydantic‑схемы результатов отправки.
Используется в service.py и router.py, чтобы не таскать "сырые"
объекты httpx.Response.
"""
from pydantic import BaseModel

class SendResult(BaseModel):
    status_code: int
    ok: bool
    attempts: int
    response: str
