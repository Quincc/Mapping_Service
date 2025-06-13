"""
Pydantic-схемы для REST-эндпойнтов модуля «Mapping».

* MappingRule   — одна строка таблицы (source → target + transform, type)
* MappingConfig — целый JSON-файл проекта
"""
from pydantic import BaseModel, Field
from typing import Literal, Any

TransformName = Literal["trim", "title", "lower", "upper", "datefmt"]

class MappingRule(BaseModel):
    source: str = Field(..., examples=["customer_name"])
    target: str = Field(..., examples=["name"])
    type:   Literal["string", "int", "float", "date"] = "string"
    transform: TransformName | None = None
    date_format: str | None = None

class MappingConfig(BaseModel):
    project_id: str
    rules: list[MappingRule]