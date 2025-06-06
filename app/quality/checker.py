"""
Проверка качества DataFrame на основе зарегистрированных правил.

Алгоритм:
    1. Берём список правил из rules.RULES (экземпляры классов RuleBase).
    2. Каждый Rule проверяет DataFrame и возвращает 0+ Issue объектов.
    3. Собираем все Issue, сохраняем отчёт (storage.save_report) и
       возвращаем объект QualityReport.

Добавить новый тип проверки → реализовать класс в rules.py, положить его
в список RULES.
"""
import pandas as pd
from .schemas import Issue, QCReport
from .rules import REQUIRED_SCHEMA

def check_dataframe(df: pd.DataFrame) -> QCReport:
    """Применяем все правила к DataFrame и сохраняем отчёт CSV."""

    issues: list[Issue] = []

    # 1) наличие обязательных колонок
    for col, rule in REQUIRED_SCHEMA.items():
        if rule["required"] and col not in df.columns:
            issues.append(Issue(row=None, column=col,
                                type="missing_field",
                                detail="required column absent"))

    # 2) построчные проверки
    for idx, row in df.iterrows():
        for col, rule in REQUIRED_SCHEMA.items():
            if col not in row:
                continue

            val = row[col]
            # пустые значения
            if pd.isna(val) or val == "":
                issues.append(Issue(row=int(idx), column=col,
                                    type="null_value", detail="empty"))
                continue

            # типы
            expected = rule["type"]
            if expected == "int" and not pd.api.types.is_integer(val):
                issues.append(Issue(row=int(idx), column=col,
                                    type="type_mismatch", detail="expected int"))
            elif expected == "float" and not isinstance(val, float):
                issues.append(Issue(row=int(idx), column=col,
                                    type="type_mismatch", detail="expected float"))
            elif expected == "date" and not isinstance(val, str):
                # дата уже в строковом fmt после маппинга
                issues.append(Issue(row=int(idx), column=col,
                                    type="type_mismatch", detail="expected date str"))

    return QCReport(total_rows=len(df), issues=issues)
