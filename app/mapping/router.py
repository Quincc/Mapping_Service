"""
REST-эндпойнты модуля «Mapping».

* GET  /mapping?project_id=…      → вернуть текущий JSON-конфиг
* POST /mapping                   → сохранить конфиг из UI-формы
"""
from fastapi import APIRouter, Depends, HTTPException, status
from app.project.auth import get_current_project
from .schemas import MappingConfig
from .storage import save_config, load_config, cfg_path

router = APIRouter(prefix="/mapping", tags=["mapping"])

@router.get("/", response_model=MappingConfig)
async def get_cfg(project = Depends(get_current_project)):
    """Вернуть текущий конфиг; 404, если не создан."""
    if not cfg_path(project.id).exists():
        raise HTTPException(404, "mapping_not_found")
    return load_config(project.id)

@router.put("/", response_model=MappingConfig, status_code=status.HTTP_201_CREATED)
async def put_cfg(cfg: MappingConfig, project = Depends(get_current_project)):
    if cfg.project_id != project.id:
        raise HTTPException(400, "project_id_mismatch")
    save_config(cfg)
    return cfg
