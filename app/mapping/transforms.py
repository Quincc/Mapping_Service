"""
Готовые строковые трансформации, которые может выбрать пользователь
в UI-конструкторе маппинга (см. mapping.html).

Ключи словаря ➜ название трансформации в JSON-конфиге.
Значение ➜ функция `str -> str`.
"""
import pandas as pd
from slugify import slugify

def trim(x):   return x.strip() if isinstance(x, str) else x
def title(x):  return x.title() if isinstance(x, str) else x
def lower(x):  return x.lower() if isinstance(x, str) else x
def upper(x):  return x.upper() if isinstance(x, str) else x

def datefmt(series: pd.Series, fmt: str):
    return pd.to_datetime(series, errors="coerce").dt.strftime(fmt)

TRANSFORMS = {"trim": trim, "title": title, "lower": lower, "upper": upper}
