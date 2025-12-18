"""
════════════════════════════════════════════════════════════════════════════════════════════════════
REPORTING API - REST Endpoints for Reports and Analytics
════════════════════════════════════════════════════════════════════════════════════════════════════

Endpoints for reporting operations:
- GET /reporting/planning - Get planning report
- GET /reporting/inventory - Get inventory report
- GET /reporting/quality - Get quality report
- GET /reporting/maintenance - Get maintenance report
- GET /reporting/rd - Get R&D report
- POST /reporting/export - Export report
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

try:
    from .planning_report import generate_planning_report
    from .inventory_report import generate_inventory_report
    from .quality_report import generate_quality_report
    HAS_REPORTING = True
except ImportError:
    HAS_REPORTING = False

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reporting", tags=["Reporting"])


# ═══════════════════════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class ExportRequest(BaseModel):
    """Request to export report."""
    report_type: str = Field(..., description="Report type")
    format: str = Field("json", description="Export format (json, csv, pdf)")
    time_range: Optional[Dict[str, str]] = None


@router.get("/status")
async def get_reporting_status():
    """Get status of reporting module."""
    return {
        "available": HAS_REPORTING,
        "version": "1.0.0",
        "features": [
            "planning_reports",
            "inventory_reports",
            "quality_reports",
            "maintenance_reports",
            "rd_reports",
            "export"
        ]
    }


@router.get("/planning")
async def get_planning_report(
    time_range: Optional[str] = Query(None, description="Time range"),
    format: str = Query("json", description="Report format")
):
    """Get planning report."""
    if not HAS_REPORTING:
        raise HTTPException(status_code=501, detail="Reporting not available")
    
    try:
        report = generate_planning_report(time_range, format)
        return {"report": report, "status": "success"}
    except Exception as e:
        logger.error(f"Error generating planning report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/inventory")
async def get_inventory_report(
    time_range: Optional[str] = Query(None, description="Time range"),
    format: str = Query("json", description="Report format")
):
    """Get inventory report."""
    if not HAS_REPORTING:
        raise HTTPException(status_code=501, detail="Reporting not available")
    
    try:
        report = generate_inventory_report(time_range, format)
        return {"report": report, "status": "success"}
    except Exception as e:
        logger.error(f"Error generating inventory report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quality")
async def get_quality_report(
    time_range: Optional[str] = Query(None, description="Time range"),
    format: str = Query("json", description="Report format")
):
    """Get quality report."""
    if not HAS_REPORTING:
        raise HTTPException(status_code=501, detail="Reporting not available")
    
    try:
        report = generate_quality_report(time_range, format)
        return {"report": report, "status": "success"}
    except Exception as e:
        logger.error(f"Error generating quality report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/maintenance")
async def get_maintenance_report(
    time_range: Optional[str] = Query(None, description="Time range"),
    format: str = Query("json", description="Report format")
):
    """Get maintenance report."""
    return {
        "message": "Maintenance reporting not yet implemented",
        "status": "not_implemented"
    }


@router.get("/rd")
async def get_rd_report(
    time_range: Optional[str] = Query(None, description="Time range"),
    format: str = Query("json", description="Report format")
):
    """Get R&D report."""
    return {
        "message": "R&D reporting available via /api/rd/report/summary",
        "status": "redirect",
        "redirect": "/api/rd/report/summary"
    }


@router.post("/export")
async def export_report(request: ExportRequest):
    """Export report."""
    if not HAS_REPORTING:
        raise HTTPException(status_code=501, detail="Reporting not available")
    
    try:
        # Placeholder for export functionality
        return {
            "message": f"Export {request.report_type} as {request.format}",
            "status": "not_implemented"
        }
    except Exception as e:
        logger.error(f"Error exporting report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


