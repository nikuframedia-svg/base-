"""
════════════════════════════════════════════════════════════════════════════════════════════════════
EVALUATION API - REST Endpoints for KPI, Model Metrics, and Data Quality
════════════════════════════════════════════════════════════════════════════════════════════════════

Endpoints for evaluation operations:
- GET /evaluation/kpis - Get KPI metrics
- GET /evaluation/model-metrics - Get model metrics
- GET /evaluation/data-quality - Get data quality report
- POST /evaluation/data-quality/snr - Calculate SNR
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

try:
    from .kpi_engine import get_kpi_metrics
    from .model_metrics import get_model_metrics
    from .data_quality import get_data_quality_report, calculate_snr
    HAS_EVALUATION = True
except ImportError:
    HAS_EVALUATION = False

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


# ═══════════════════════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class SNRRequest(BaseModel):
    """Request to calculate SNR."""
    variable: str = Field(..., description="Variable name")
    time_range: Optional[Dict[str, str]] = None


@router.get("/status")
async def get_evaluation_status():
    """Get status of evaluation module."""
    return {
        "available": HAS_EVALUATION,
        "version": "1.0.0",
        "features": [
            "kpi_engine",
            "model_metrics",
            "data_quality",
            "snr_analysis"
        ]
    }


@router.get("/kpis")
async def get_kpis(
    category: Optional[str] = Query(None, description="KPI category"),
    time_range: Optional[str] = Query(None, description="Time range")
):
    """Get KPI metrics."""
    if not HAS_EVALUATION:
        raise HTTPException(status_code=501, detail="Evaluation not available")
    
    try:
        kpis = get_kpi_metrics(category, time_range)
        return {"kpis": kpis, "status": "success"}
    except Exception as e:
        logger.error(f"Error getting KPIs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model-metrics")
async def get_model_metrics(
    model_name: Optional[str] = Query(None, description="Model name"),
    metric_type: Optional[str] = Query(None, description="Metric type")
):
    """Get model metrics."""
    if not HAS_EVALUATION:
        raise HTTPException(status_code=501, detail="Evaluation not available")
    
    try:
        metrics = get_model_metrics(model_name, metric_type)
        return {"metrics": metrics, "status": "success"}
    except Exception as e:
        logger.error(f"Error getting model metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data-quality")
async def get_data_quality(
    dataset: Optional[str] = Query(None, description="Dataset name"),
    time_range: Optional[str] = Query(None, description="Time range")
):
    """Get data quality report."""
    if not HAS_EVALUATION:
        raise HTTPException(status_code=501, detail="Evaluation not available")
    
    try:
        report = get_data_quality_report(dataset, time_range)
        return {"report": report, "status": "success"}
    except Exception as e:
        logger.error(f"Error getting data quality report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data-quality/snr")
async def calculate_snr_analysis(request: SNRRequest):
    """Calculate Signal-to-Noise Ratio."""
    if not HAS_EVALUATION:
        raise HTTPException(status_code=501, detail="Evaluation not available")
    
    try:
        snr = calculate_snr(request.variable, request.time_range)
        return {"snr": snr, "variable": request.variable, "status": "success"}
    except Exception as e:
        logger.error(f"Error calculating SNR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

