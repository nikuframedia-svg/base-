"""
════════════════════════════════════════════════════════════════════════════════════════════════════
CAUSAL ANALYSIS API - REST Endpoints for Causal Analysis
════════════════════════════════════════════════════════════════════════════════════════════════════

Endpoints for causal analysis operations:
- POST /causal/build-graph - Build causal graph
- POST /causal/estimate-effect - Estimate causal effect
- GET /causal/root-causes - Get root causes
- GET /causal/complexity-dashboard - Get complexity dashboard
- POST /causal/collect-data - Collect data for causal analysis
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

try:
    from .causal_graph_builder import build_causal_graph
    from .causal_effect_estimator import estimate_causal_effect
    from .complexity_dashboard_engine import get_complexity_dashboard
    from .data_collector import collect_causal_data
    HAS_CAUSAL = True
except ImportError:
    HAS_CAUSAL = False

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/causal", tags=["Causal Analysis"])


# ═══════════════════════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class BuildGraphRequest(BaseModel):
    """Request to build causal graph."""
    variables: List[str] = Field(..., description="List of variables to include")
    domain_knowledge: Optional[Dict[str, Any]] = None


class CausalEffectRequest(BaseModel):
    """Request to estimate causal effect."""
    treatment: str = Field(..., description="Treatment variable")
    outcome: str = Field(..., description="Outcome variable")
    confounders: Optional[List[str]] = None


@router.get("/status")
async def get_causal_status():
    """Get status of causal analysis module."""
    return {
        "available": HAS_CAUSAL,
        "version": "1.0.0",
        "features": [
            "causal_graph_building",
            "causal_effect_estimation",
            "root_cause_analysis",
            "complexity_dashboard",
            "data_collection"
        ]
    }


@router.post("/build-graph")
async def build_graph(request: BuildGraphRequest):
    """Build causal graph from variables."""
    if not HAS_CAUSAL:
        raise HTTPException(status_code=501, detail="Causal analysis not available")
    
    try:
        graph = build_causal_graph(request.variables, request.domain_knowledge)
        return {"graph": graph, "status": "success"}
    except Exception as e:
        logger.error(f"Error building causal graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/estimate-effect")
async def estimate_effect(request: CausalEffectRequest):
    """Estimate causal effect."""
    if not HAS_CAUSAL:
        raise HTTPException(status_code=501, detail="Causal analysis not available")
    
    try:
        effect = estimate_causal_effect(
            request.treatment,
            request.outcome,
            request.confounders or []
        )
        return {"effect": effect, "status": "success"}
    except Exception as e:
        logger.error(f"Error estimating causal effect: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/root-causes")
async def get_root_causes(outcome: str = Query(..., description="Outcome variable")):
    """Get root causes for an outcome."""
    if not HAS_CAUSAL:
        raise HTTPException(status_code=501, detail="Causal analysis not available")
    
    try:
        # Placeholder - implement based on actual root cause analysis
        return {"root_causes": [], "outcome": outcome, "status": "success"}
    except Exception as e:
        logger.error(f"Error getting root causes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/complexity-dashboard")
async def get_complexity_dashboard():
    """Get complexity dashboard."""
    if not HAS_CAUSAL:
        raise HTTPException(status_code=501, detail="Causal analysis not available")
    
    try:
        dashboard = get_complexity_dashboard()
        return {"dashboard": dashboard, "status": "success"}
    except Exception as e:
        logger.error(f"Error getting complexity dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collect-data")
async def collect_data(
    variables: List[str] = Body(..., description="Variables to collect"),
    time_range: Optional[Dict[str, str]] = None
):
    """Collect data for causal analysis."""
    if not HAS_CAUSAL:
        raise HTTPException(status_code=501, detail="Causal analysis not available")
    
    try:
        data = collect_causal_data(variables, time_range)
        return {"data": data, "status": "success"}
    except Exception as e:
        logger.error(f"Error collecting data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

