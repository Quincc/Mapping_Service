"""
apply_mapping() — преобразует DataFrame согласно JSON-конфигу проекта.

Поддерживает:
    • строковые трансформации (trim / lower / …)
    • приведение типов (int / float / date)
    • slugify целевых имён (кириллица → latin, пробелы → _)

Если колонка отсутствует — оставляем NaN, но не падаем.
"""
import pandas as pd
from .schemas import MappingConfig
from .transforms import TRANSFORMS, datefmt
from slugify import slugify


def apply_mapping(df: pd.DataFrame, cfg: MappingConfig) -> pd.DataFrame:
    """
    Применяет все правила из `cfg` и возвращает новый DataFrame.

    • Не модифицирует исходный `df` (создаёт `out`).
    • Отсутствующие колонки → NaN (в тестах это допустимо).
    """
    out = pd.DataFrame()

    for rule in cfg.rules:
        col = df[rule.source]

        # преобразование типа
        if rule.type == "int":
            col = pd.to_numeric(col, errors="coerce").astype("Int64")
        elif rule.type == "float":
            col = pd.to_numeric(col, errors="coerce")
        elif rule.type == "date":
            fmt = rule.date_format or "%Y-%m-%d"
            col = datefmt(col, fmt)

        # строковые трансформации
        if rule.transform in TRANSFORMS:
            col = col.map(TRANSFORMS[rule.transform])

        out[rule.target] = col

    # опционально: нормализуем имена
    out.columns = [slugify(c, separator="_") for c in out.columns]
    return out
