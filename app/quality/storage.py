"""Сохранение отчёта о качестве в CSV."""

from pathlib import Path
import pandas as pd
from .schemas import QCReport
from core.settings import settings

def save_report(project_id: str, report: QCReport) -> Path:
    out_dir = Path("reports") / project_id
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "quality_report.csv"

    df = pd.DataFrame([i.model_dump() for i in report.issues])
    df.to_csv(path, index=False)
    return path
