"""
════════════════════════════════════════════════════════════════════════════════════════════════════
WORKFORCE ANALYTICS API - REST Endpoints for Workforce Performance and Assignment
════════════════════════════════════════════════════════════════════════════════════════════════════

Endpoints for workforce analytics:
- GET /workforce/performance - Get worker performance metrics
- GET /workforce/forecast - Get workforce forecast
- POST /workforce/assign - Optimize worker assignment
- GET /workforce/learning-curves - Get learning curves
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

try:
    from .workforce_performance_engine import (
        compute_worker_performance,
        compute_all_worker_performances,
        compute_learning_curve
    )
    from .workforce_forecasting import forecast_worker_productivity, forecast_all_workers
    from .workforce_assignment_model import optimize_worker_assignment
    HAS_WORKFORCE = True
except ImportError:
    HAS_WORKFORCE = False

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workforce", tags=["Workforce Analytics"])


# ═══════════════════════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class AssignmentRequest(BaseModel):
    """Request to optimize worker assignment."""
    operations: List[Dict[str, Any]] = Field(..., description="List of operations")
    workers: List[Dict[str, Any]] = Field(..., description="List of workers")
    constraints: Optional[Dict[str, Any]] = None


@router.get("/status")
async def get_workforce_status():
    """Get status of workforce analytics module."""
    return {
        "available": HAS_WORKFORCE,
        "version": "1.0.0",
        "features": [
            "performance_analysis",
            "forecasting",
            "assignment_optimization",
            "learning_curves"
        ]
    }


@router.get("/performance")
async def get_worker_performance(
    worker_id: Optional[str] = Query(None, description="Worker ID"),
    time_range: Optional[str] = Query(None, description="Time range")
):
    """Get worker performance metrics."""
    if not HAS_WORKFORCE:
        raise HTTPException(status_code=501, detail="Workforce analytics not available")
    
    try:
        if worker_id:
            performance = compute_worker_performance(worker_id, time_range)
            return {"performance": performance, "status": "success"}
        else:
            performances = compute_all_worker_performances(time_range)
            return {"performances": performances, "status": "success"}
    except Exception as e:
        logger.error(f"Error getting worker performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast")
async def get_workforce_forecast(
    worker_id: Optional[str] = Query(None, description="Worker ID"),
    horizon_days: int = Query(30, description="Forecast horizon in days")
):
    """Get workforce forecast."""
    if not HAS_WORKFORCE:
        raise HTTPException(status_code=501, detail="Workforce analytics not available")
    
    try:
        if worker_id:
            forecast = forecast_worker_productivity(worker_id, horizon_days)
            return {"forecast": forecast, "status": "success"}
        else:
            forecasts = forecast_all_workers(horizon_days)
            return {"forecasts": forecasts, "status": "success"}
    except Exception as e:
        logger.error(f"Error getting workforce forecast: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assign")
async def optimize_assignment(request: AssignmentRequest):
    """Optimize worker assignment."""
    if not HAS_WORKFORCE:
        raise HTTPException(status_code=501, detail="Workforce analytics not available")
    
    try:
        assignment = optimize_worker_assignment(
            request.operations,
            request.workers,
            request.constraints
        )
        return {"assignment": assignment, "status": "success"}
    except Exception as e:
        logger.error(f"Error optimizing assignment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/learning-curves")
async def get_learning_curves(
    worker_id: Optional[str] = Query(None, description="Worker ID")
):
    """Get learning curves."""
    if not HAS_WORKFORCE:
        raise HTTPException(status_code=501, detail="Workforce analytics not available")
    
    try:
        if worker_id:
            curve = compute_learning_curve(worker_id)
            return {"curve": curve, "status": "success"}
        else:
            return {"message": "Please specify worker_id", "status": "error"}
    except Exception as e:
        logger.error(f"Error getting learning curves: {e}")
        raise HTTPException(status_code=500, detail=str(e))

