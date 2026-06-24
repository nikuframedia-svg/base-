"""Endpoints dos KPIs da estação de extrusão.

- GET /api/extrusion-kpi/          -> KPIs em JSON
- GET /api/extrusion-kpi/dashboard -> dashboard HTML self-contained

Os ficheiros de dados são procurados em ``app/data/extrusion`` (configurável
via variável de ambiente ``EXTRUSION_DATA_DIR``).
"""

import logging
import os
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse

from app.extrusion_kpi.kpi_engine import compute_kpis, ExtrusionKPIConfig
from app.extrusion_kpi.dashboard import render_dashboard

router = APIRouter()
logger = logging.getLogger(__name__)


def _build_config(data_dir: Optional[str]) -> ExtrusionKPIConfig:
    cfg = ExtrusionKPIConfig()
    if data_dir:
        cfg.data_dir = data_dir
    elif os.getenv("EXTRUSION_DATA_DIR"):
        cfg.data_dir = os.getenv("EXTRUSION_DATA_DIR")
    return cfg


@router.get("/")
async def get_kpis(data_dir: Optional[str] = Query(default=None)):
    """Devolve os KPIs de planeamento da extrusão em JSON."""
    try:
        cfg = _build_config(data_dir).resolve()
        if not any([cfg.production_log, cfg.order_book, cfg.overview]):
            raise HTTPException(
                status_code=404,
                detail=f"Sem ficheiros de extrusão em '{cfg.data_dir}'. "
                       f"Coloque os .xlsx ou defina EXTRUSION_DATA_DIR.",
            )
        return compute_kpis(cfg)
    except HTTPException:
        raise
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Falha a calcular KPIs de extrusão")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(data_dir: Optional[str] = Query(default=None)):
    """Devolve o dashboard HTML dos KPIs."""
    cfg = _build_config(data_dir)
    return HTMLResponse(content=render_dashboard(compute_kpis(cfg)))
