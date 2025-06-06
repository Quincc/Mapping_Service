"""
Сохранение / загрузка JSON-конфига маппинга.

Файлы лежат в директории `config/<project_id>.json`.
"""
from pathlib import Path
import json, orjson
from core.settings import settings
from .schemas import MappingConfig

CFG_DIR = Path("config")

def cfg_path(project_id: str) -> Path:
    return CFG_DIR / f"{project_id}.json"

def save_config(cfg: MappingConfig) -> None:
    """Сериализация схемы в JSON (pretty-print для удобства git-diff)."""
    CFG_DIR.mkdir(exist_ok=True)
    cfg_path(cfg.project_id).write_bytes(orjson.dumps(cfg.model_dump(), option=orjson.OPT_INDENT_2))

def load_config(project_id: str) -> MappingConfig:
    """Загрузка схемы; FileNotFoundError, если ещё не создали."""
    raw = json.loads(cfg_path(project_id).read_text())
    return MappingConfig(**raw)
