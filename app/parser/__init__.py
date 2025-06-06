"""
Модуль **app.parser**

Содержит:
    • readers.py    – функции чтения CSV / XLSX / JSON
    • preview.py    – выборка первых N столбцов для UI
    • exceptions.py – пользовательские ошибки парсинга
    • pipeline.py   – сквозной ETL-пайплайн:

          parse → mapping → quality → send

Внешний код обычно импортирует только:

    from app.parser.pipeline import run_full_pipeline
"""

from .readers import parse_file        # re-export