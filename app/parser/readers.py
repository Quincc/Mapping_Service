"""
Функции чтения разных форматов в **pandas.DataFrame**.

Поддерживаем три формата, перечисленные в ALLOWED_EXT:

    .csv   → read_csv
    .xlsx  → read_excel (первый лист)
    .json  → read_json (строгий режим, каждая строка - объект)

Если нужно добавить новый тип (паркет, avro) — дописываем функцию
`_read_parquet()` и регистрируем пары `".parquet": _read_parquet`
в READERS.
"""
from pathlib import Path
import pandas as pd
import orjson
from .exceptions import UnsupportedFormat, ParseError

ALLOWED_EXT = {".csv", ".xlsx", ".json"}

def read_csv(path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(path)
    except Exception as exc:
        raise ParseError(f"CSV error: {exc}") from exc

def read_xlsx(path: Path) -> pd.DataFrame:
    try:
        return pd.read_excel(path, engine="openpyxl")
    except Exception as exc:
        raise ParseError(f"XLSX error: {exc}") from exc

def read_json(path: Path) -> pd.DataFrame:
    try:
        with open(path, "rb") as f:
            data = orjson.loads(f.read())
        return pd.DataFrame(data)
    except Exception as exc:
        raise ParseError(f"JSON error: {exc}") from exc

def parse_file(path: Path) -> pd.DataFrame:
    """
    Определяет reader по расширению и возвращает DataFrame.

    Args:
        path: абсолютный/относительный путь к файлу

    Raises:
        UnsupportedFormatError: если формат неизвестен
        EmptyFileError: если файл открылся, но данных нет
    """
    ext = path.suffix.lower()
    if ext not in ALLOWED_EXT:
        raise UnsupportedFormat(ext)

    if ext == ".csv":
        return read_csv(path)
    if ext == ".xlsx":
        return read_xlsx(path)
    return read_json(path)        # .json
