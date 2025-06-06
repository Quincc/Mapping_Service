"""
Pydantic-схемы ответов эндпоинтов «upload».
"""
from pydantic import BaseModel

class UploadResponse(BaseModel):
    """
    Pydantic-схемы ответов эндпоинтов «upload».
    """
    detail: str = "file_saved"
    path: str
