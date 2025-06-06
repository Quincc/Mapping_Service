"""Pydantic‑схемы объектов проверки качества."""

from pydantic import BaseModel
from typing import Literal

IssueType = Literal["missing_field", "null_value", "type_mismatch"]

class Issue(BaseModel):
    row: int | None    # None для проблем «на уровне колонки»
    column: str
    type: IssueType
    detail: str

class QCReport(BaseModel):
    total_rows: int
    issues: list[Issue]
