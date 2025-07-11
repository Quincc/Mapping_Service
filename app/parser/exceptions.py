"""
Специализированные исключения парсера.

Используем свои типы, чтобы:
    • отличать «ожидаемые» проблемы (не тот формат, пустой файл)
      от системных (OSError, pandas.ParserError).
    • правильно возвращать HTTP-коды (422, 400) в API-слое.
"""
class UnsupportedFormat(Exception):
    """Формат файла не поддерживается."""

class ParseError(Exception):
    """Невозможно разобрать файл (битый CSV, плохая кодировка и т.п.)."""
