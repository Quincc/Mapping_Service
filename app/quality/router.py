"""
FastAPI‑роуты для модуля quality.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from app.project.auth import get_current_project
router = APIRouter(prefix="/quality", tags=["quality"])

@router.get("/report")
async def download_report(project = Depends(get_current_project)):
    path = Path("reports") / project.id / "quality_report.csv"
    if not path.exists():
        raise HTTPException(404, "report_not_found")
    return FileResponse(path, filename="quality_report.csv", media_type="text/csv")
