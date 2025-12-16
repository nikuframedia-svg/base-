"""
API Compatibility Layer - Mapeia endpoints antigos para novos endpoints
"""
import logging
from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import RedirectResponse

from app.aps.scheduler import APSScheduler
from app.etl.loader import get_loader

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/plan")
async def get_plan_compat():
    """Compatibilidade: /plan -> /api/planning/v2/plano"""
    # Redirecionar para o endpoint correto
    from app.api.planning_v2 import get_plan
    return await get_plan(batch_id=None, horizon_hours=168)


@router.get("/plan/kpis")
async def get_plan_kpis():
    """Retorna KPIs do plano atual"""
    try:
        scheduler = APSScheduler()
        loader = scheduler.loader
        
        # Obter plano otimizado
        from datetime import datetime, timedelta
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=7)
        
        plano = scheduler.generate_optimized_plan(start_date, end_date)
        
        if not plano or not plano.operations:
            return {
                "makespan_hours": 0.0,
                "route_distribution": {},
                "overlaps": {"total": 0, "by_machine": {}},
                "active_bottleneck": None,
                "machine_loads": [],
                "lead_time_average_h": 0.0,
                "otd_percent": 0.0,
                "setup_hours": 0.0,
                "total_operations": 0,
                "total_orders": 0,
                "total_articles": 0,
                "total_machines": 0,
                "plan_start": None,
                "plan_end": None,
            }
        
        operations = plano.operations
        kpis = plano.kpis or {}
        
        # Calcular makespan
        if operations:
            min_start = min(op.start_time for op in operations)
            max_end = max(op.end_time for op in operations)
            makespan_hours = (max_end - min_start).total_seconds() / 3600.0
        else:
            makespan_hours = 0.0
        
        # Distribuição de rotas
        route_distribution = {}
        for op in operations:
            route = getattr(op, "rota", "") or "UNKNOWN"
            route_distribution[route] = route_distribution.get(route, 0) + 1
        
        # Sobreposições
        overlaps_total = sum(1 for op in operations if getattr(op, "overlap", 0) > 0)
        overlaps_by_machine = {}
        for op in operations:
            if getattr(op, "overlap", 0) > 0:
                machine = getattr(op, "recurso", "") or "UNKNOWN"
                overlaps_by_machine[machine] = overlaps_by_machine.get(machine, 0) + 1
        
        # Carga de máquinas
        machine_loads = {}
        machine_ops = {}
        for op in operations:
            machine = getattr(op, "recurso", "") or "UNKNOWN"
            duration = (op.end_time - op.start_time).total_seconds() / 60.0  # minutos
            machine_loads[machine] = machine_loads.get(machine, 0.0) + duration
            machine_ops[machine] = machine_ops.get(machine, 0) + 1
        
        # Calcular utilização
        total_hours = makespan_hours if makespan_hours > 0 else 168.0
        machine_loads_list = []
        for machine, load_min in machine_loads.items():
            load_hours = load_min / 60.0
            utilization_pct = (load_hours / total_hours) * 100 if total_hours > 0 else 0.0
            idle_min = (total_hours * 60) - load_min
            idle_hours = idle_min / 60.0
            
            machine_loads_list.append({
                "machine_id": machine,
                "load_min": round(load_min, 1),
                "load_hours": round(load_hours, 1),
                "idle_min": round(idle_min, 1),
                "idle_hours": round(idle_hours, 1),
                "utilization_pct": round(utilization_pct, 1),
                "num_operations": machine_ops.get(machine, 0),
            })
        
        # Ordenar por carga
        machine_loads_list.sort(key=lambda x: x["load_min"], reverse=True)
        
        # Gargalo ativo (máquina mais carregada)
        active_bottleneck = None
        if machine_loads_list:
            top_machine = machine_loads_list[0]
            if top_machine["utilization_pct"] > 80:
                active_bottleneck = {
                    "machine_id": top_machine["machine_id"],
                    "total_minutes": top_machine["load_min"],
                }
        
        # Lead time médio
        lead_time_average_h = kpis.get("lead_time_h", 0.0) or 0.0
        
        # OTD (assumir 100% se não houver dados)
        otd_percent = kpis.get("otd_percent", 100.0) or 100.0
        
        # Setup hours
        setup_hours = kpis.get("setup_hours", 0.0) or 0.0
        
        # Contagens
        ordens = loader.get_ordens()
        total_orders = len(ordens) if ordens is not None and not ordens.empty else 0
        total_articles = len(set(getattr(op, "artigo", "") for op in operations)) if operations else 0
        total_machines = len(machine_loads)
        
        return {
            "makespan_hours": round(makespan_hours, 1),
            "route_distribution": route_distribution,
            "overlaps": {
                "total": overlaps_total,
                "by_machine": overlaps_by_machine,
            },
            "active_bottleneck": active_bottleneck,
            "machine_loads": machine_loads_list,
            "lead_time_average_h": round(lead_time_average_h, 1),
            "otd_percent": round(otd_percent, 1),
            "setup_hours": round(setup_hours, 1),
            "total_operations": len(operations),
            "total_orders": total_orders,
            "total_articles": total_articles,
            "total_machines": total_machines,
            "plan_start": min_start.isoformat() if operations else None,
            "plan_end": max_end.isoformat() if operations else None,
        }
    except Exception as exc:
        logger.exception("Erro ao calcular KPIs do plano: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/plan/suggestions")
async def get_plan_suggestions():
    """Compatibilidade: /plan/suggestions -> /api/suggestions/"""
    from app.api.suggestions import get_suggestions
    return await get_suggestions(mode="planeamento")


@router.get("/bottleneck")
async def get_bottleneck_compat():
    """Compatibilidade: /bottleneck -> /api/bottlenecks/"""
    from app.api.bottlenecks import get_bottlenecks
    result = await get_bottlenecks(demo=False)
    
    # Converter formato para compatibilidade
    if result.get("bottlenecks"):
        top_bottleneck = result["bottlenecks"][0] if result["bottlenecks"] else None
        if top_bottleneck:
            return {
                "machine_id": top_bottleneck.get("recurso", ""),
                "total_minutes": top_bottleneck.get("fila_horas", 0.0) * 60,
            }
    
    return {"machine_id": "", "total_minutes": 0.0}


@router.get("/etl/status")
async def get_etl_status_compat():
    """Compatibilidade: /etl/status -> /api/etl/status"""
    from app.api.etl import etl_status
    return await etl_status()


@router.get("/actions")
async def get_actions(status: Optional[str] = Query(None)):
    """Retorna ações pendentes (stub - implementar quando necessário)"""
    return {
        "count": 0,
        "actions": [],
        "pending_count": 0,
    }


@router.get("/product/type-kpis")
async def get_product_type_kpis():
    """Retorna KPIs por tipo de produto (stub - implementar quando necessário)"""
    return {
        "type_kpis": {},
        "global_kpis": {
            "total_products": 0,
            "total_orders": 0,
            "fastest_type": "",
            "slowest_type": "",
            "most_stable_type": "",
            "global_avg_lead_time_hours": 0.0,
            "global_avg_processing_time_min": 0.0,
            "type_distribution": {},
        },
        "available_types": [],
    }


@router.post("/product/delivery-estimate")
async def estimate_delivery(payload: dict):
    """Estima data de entrega (stub - implementar quando necessário)"""
    return {
        "estimate": {
            "order_id": payload.get("order_id", ""),
            "article_id": payload.get("article_id", ""),
            "estimated_duration_hours": 0.0,
            "estimated_delivery_date": None,
            "breakdown": {
                "processing_hours": 0.0,
                "setup_hours": 0.0,
                "queue_hours": 0.0,
                "buffer_hours": 0.0,
            },
            "confidence_score": 0.0,
            "confidence_level": "LOW",
            "snr_estimate": 0.0,
            "snr_level": "POOR",
        }
    }


@router.get("/insights/generate")
async def generate_insights(mode: Optional[str] = Query("resumo")):
    """Compatibilidade: /insights/generate -> /api/insights/generate"""
    from app.api.insights import generate_insight
    return await generate_insight(mode=mode or "resumo")


@router.get("/planning/modes")
async def get_planning_modes():
    """Compatibilidade: /planning/modes - Retorna modos de planeamento disponíveis"""
    return {
        "available_modes": [
            {"id": "conventional", "name": "Convencional", "description": "Planeamento convencional"},
            {"id": "chained", "name": "Encadeado", "description": "Planeamento encadeado"},
        ]
    }


@router.get("/machines")
async def get_machines_compat():
    """Compatibilidade: /machines - Retorna lista de máquinas"""
    # Tentar obter máquinas do loader ou retornar lista vazia
    loader = get_loader()
    status = loader.get_status()
    machines = status.get("machines", [])
    if machines:
        return {"machine_id": [m.get("machine_id", "") for m in machines if isinstance(m, dict)]}
    return {"machine_id": []}


@router.get("/projects")
async def get_projects_compat(aggregation_mode: Optional[str] = Query(None)):
    """Compatibilidade: /projects - Retorna projetos"""
    return {
        "projects": [],
        "count": 0,
        "aggregation_mode": aggregation_mode or "explicit"
    }


@router.post("/projects/priority-plan")
async def post_projects_priority_plan(use_milp: Optional[bool] = Query(False)):
    """Compatibilidade: /projects/priority-plan - Stub"""
    return {
        "plan": [],
        "status": "not_implemented",
        "message": "Priority planning not yet implemented"
    }


@router.post("/projects/recompute")
async def post_projects_recompute():
    """Compatibilidade: /projects/recompute - Stub"""
    return {
        "status": "ok",
        "message": "Recompute not yet implemented"
    }


@router.get("/dashboards/utilization-heatmap")
async def get_dashboards_heatmap():
    """Compatibilidade: /dashboards/utilization-heatmap - Retorna heatmap de utilização"""
    return {
        "data": [],
        "machines": [],
        "time_range": {"start": None, "end": None}
    }


@router.get("/dashboards/operator")
async def get_dashboards_operator():
    """Compatibilidade: /dashboards/operator - Retorna dashboard de operadores"""
    return {
        "operators": [],
        "stats": {
            "total_operators": 0,
            "active_operators": 0,
            "utilization": 0.0
        }
    }


@router.get("/dashboards/machine-oee")
async def get_dashboards_machine_oee():
    """Compatibilidade: /dashboards/machine-oee - Retorna OEE das máquinas"""
    return {
        "machines": [],
        "overall_oee": 0.0,
        "availability": 0.0,
        "performance": 0.0,
        "quality": 0.0
    }


@router.get("/dashboards/cell-performance")
async def get_dashboards_cell_performance():
    """Compatibilidade: /dashboards/cell-performance - Retorna performance de células"""
    return {
        "cells": [],
        "overall_performance": 0.0
    }


@router.get("/dashboards/capacity-projection")
async def get_dashboards_capacity_projection():
    """Compatibilidade: /dashboards/capacity-projection - Retorna projeção de capacidade"""
    return {
        "projections": [],
        "time_range": {"start": None, "end": None}
    }

