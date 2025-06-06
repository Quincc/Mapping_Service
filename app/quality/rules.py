"""
Набор правил качества.

Каждое правило наследует базовый класс RuleBase и реализует метод
`check(df) -> list[Issue]`.

* MissingFieldRule  – проверяет наличие обязательных колонок
* NotNullRule       – проверка на отсутствие пустых значений
  (можно задавать список колонок)
"""
from typing import TypedDict, Literal

FieldType = Literal["string", "int", "float", "date"]

class FieldRule(TypedDict):
    required: bool
    type: FieldType

# целевой шаблон
REQUIRED_SCHEMA: dict[str, FieldRule] = {
    "name":      {"required": True,  "type": "string"},
    "email":     {"required": True,  "type": "string"},
    "birthdate": {"required": True, "type": "date"},
    "amount":    {"required": False, "type": "float"},
}
