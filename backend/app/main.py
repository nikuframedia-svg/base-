from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

from app.api import bottlenecks, chat, compat, etl, insight, insights, inventory, planning, planning_chat, planning_v2, suggestions, technical_queries, whatif
from app.etl.loader import get_loader, run_startup_etl

# Import all missing routers
try:
    from duplios.api_duplios import router as duplios_router
    HAS_DUPLIOS = True
except ImportError:
    HAS_DUPLIOS = False
    duplios_router = None

try:
    from duplios.api_pdm import router as pdm_router
    HAS_PDM = True
except ImportError:
    HAS_PDM = False
    pdm_router = None

try:
    from duplios.api_compliance import router as compliance_router
    HAS_COMPLIANCE = True
except ImportError:
    HAS_COMPLIANCE = False
    compliance_router = None

try:
    from duplios.api_trust_index import router as trust_index_router
    HAS_TRUST_INDEX = True
except ImportError:
    HAS_TRUST_INDEX = False
    trust_index_router = None

try:
    from duplios.api_gap_filling import router as gap_filling_router
    HAS_GAP_FILLING = True
except ImportError:
    HAS_GAP_FILLING = False
    gap_filling_router = None

try:
    from rd.api import router as rd_router
    HAS_RD = True
except ImportError:
    HAS_RD = False
    rd_router = None

try:
    from digital_twin.api_shi_dt import router as shi_dt_router
    HAS_SHI_DT = True
except ImportError:
    HAS_SHI_DT = False
    shi_dt_router = None

try:
    from digital_twin.api_iot import router as iot_router
    HAS_IOT = True
except ImportError:
    HAS_IOT = False
    iot_router = None

try:
    from digital_twin.api_xai_dt import router as xai_dt_router
    HAS_XAI_DT = True
except ImportError:
    HAS_XAI_DT = False
    xai_dt_router = None

try:
    from digital_twin.api_xai_dt_product import router as xai_dt_product_router
    HAS_XAI_DT_PRODUCT = True
except ImportError:
    HAS_XAI_DT_PRODUCT = False
    xai_dt_product_router = None

try:
    from maintenance.api import router as maintenance_router
    HAS_MAINTENANCE = True
except ImportError:
    HAS_MAINTENANCE = False
    maintenance_router = None

try:
    from quality.api_prevention_guard import router as prevention_guard_router
    HAS_PREVENTION_GUARD = True
except ImportError:
    HAS_PREVENTION_GUARD = False
    prevention_guard_router = None

try:
    from shopfloor.api_work_instructions import router as work_instructions_router
    HAS_WORK_INSTRUCTIONS = True
except ImportError:
    HAS_WORK_INSTRUCTIONS = False
    work_instructions_router = None

try:
    from smart_inventory.api_mrp_complete import router as mrp_complete_router
    HAS_MRP_COMPLETE = True
except ImportError:
    HAS_MRP_COMPLETE = False
    mrp_complete_router = None

try:
    from optimization.api_optimization import router as optimization_router
    HAS_OPTIMIZATION = True
except ImportError:
    HAS_OPTIMIZATION = False
    optimization_router = None

try:
    from simulation.zdm.api_zdm import router as zdm_router
    HAS_ZDM = True
except ImportError:
    HAS_ZDM = False
    zdm_router = None

try:
    from scheduling.api import router as scheduling_router
    HAS_SCHEDULING = True
except ImportError:
    HAS_SCHEDULING = False
    scheduling_router = None

try:
    from ops_ingestion.api import router as ops_ingestion_router
    HAS_OPS_INGESTION = True
except ImportError:
    HAS_OPS_INGESTION = False
    ops_ingestion_router = None

try:
    from causal.api import router as causal_router
    HAS_CAUSAL = True
except ImportError:
    HAS_CAUSAL = False
    causal_router = None

try:
    from evaluation.api import router as evaluation_router
    HAS_EVALUATION = True
except ImportError:
    HAS_EVALUATION = False
    evaluation_router = None

try:
    from reporting.api import router as reporting_router
    HAS_REPORTING = True
except ImportError:
    HAS_REPORTING = False
    reporting_router = None

try:
    from workforce_analytics.api import router as workforce_router
    HAS_WORKFORCE = True
except ImportError:
    HAS_WORKFORCE = False
    workforce_router = None


load_dotenv()

app = FastAPI(title="ProdPlan 4.0 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core Planning & Production
app.include_router(planning.router, prefix="/api/planning", tags=["Planning"])
app.include_router(planning_v2.router, prefix="/api/planning/v2", tags=["Planning V2"])
app.include_router(planning_chat.router, prefix="/api/planning/chat", tags=["Planning Chat"])
app.include_router(technical_queries.router, prefix="/api/technical", tags=["Technical Queries"])
app.include_router(bottlenecks.router, prefix="/api/bottlenecks", tags=["Bottlenecks"])
app.include_router(inventory.router, prefix="/api/inventory", tags=["Inventory"])
app.include_router(whatif.router, prefix="/api/whatif", tags=["What-If"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(suggestions.router, prefix="/api/suggestions", tags=["Suggestions"])
app.include_router(insight.router, prefix="/api/insight", tags=["Insight"])
app.include_router(insights.router, prefix="/api/insights", tags=["Insights"])
app.include_router(etl.router, prefix="/api", tags=["ETL"])
app.include_router(compat.router, tags=["Compatibility"])

# Duplios - Digital Product Passports
if HAS_DUPLIOS and duplios_router:
    app.include_router(duplios_router, prefix="/api", tags=["Duplios - DPP"])

if HAS_PDM and pdm_router:
    app.include_router(pdm_router, prefix="/api", tags=["Duplios - PDM"])

if HAS_COMPLIANCE and compliance_router:
    app.include_router(compliance_router, prefix="/api", tags=["Duplios - Compliance"])

if HAS_TRUST_INDEX and trust_index_router:
    app.include_router(trust_index_router, prefix="/api", tags=["Duplios - Trust Index"])

if HAS_GAP_FILLING and gap_filling_router:
    app.include_router(gap_filling_router, prefix="/api", tags=["Duplios - Gap Filling"])

# R&D - Research & Development
if HAS_RD and rd_router:
    app.include_router(rd_router, prefix="/api", tags=["R&D"])

# Digital Twin
if HAS_SHI_DT and shi_dt_router:
    app.include_router(shi_dt_router, prefix="/api", tags=["Digital Twin - SHI-DT"])

if HAS_IOT and iot_router:
    app.include_router(iot_router, prefix="/api", tags=["Digital Twin - IoT"])

if HAS_XAI_DT and xai_dt_router:
    app.include_router(xai_dt_router, prefix="/api", tags=["Digital Twin - XAI-DT"])

if HAS_XAI_DT_PRODUCT and xai_dt_product_router:
    app.include_router(xai_dt_product_router, prefix="/api", tags=["Digital Twin - XAI-DT Product"])

# Maintenance & PredictiveCare
if HAS_MAINTENANCE and maintenance_router:
    app.include_router(maintenance_router, prefix="/api", tags=["Maintenance"])

# Quality & Prevention Guard
if HAS_PREVENTION_GUARD and prevention_guard_router:
    app.include_router(prevention_guard_router, prefix="/api", tags=["Quality - Prevention Guard"])

# Shopfloor & Work Instructions
if HAS_WORK_INSTRUCTIONS and work_instructions_router:
    app.include_router(work_instructions_router, prefix="/api", tags=["Shopfloor - Work Instructions"])

# Smart Inventory - MRP Complete
if HAS_MRP_COMPLETE and mrp_complete_router:
    app.include_router(mrp_complete_router, prefix="/api", tags=["Smart Inventory - MRP"])

# Optimization
if HAS_OPTIMIZATION and optimization_router:
    app.include_router(optimization_router, prefix="/api", tags=["Optimization"])

# ZDM - Zero Disruption Manufacturing
if HAS_ZDM and zdm_router:
    app.include_router(zdm_router, prefix="/api", tags=["ZDM"])

# Scheduling
if HAS_SCHEDULING and scheduling_router:
    app.include_router(scheduling_router, prefix="/api", tags=["Scheduling"])

# Ops Ingestion
if HAS_OPS_INGESTION and ops_ingestion_router:
    app.include_router(ops_ingestion_router, prefix="/api", tags=["Ops Ingestion"])

# Causal Analysis
if HAS_CAUSAL and causal_router:
    app.include_router(causal_router, prefix="/api", tags=["Causal Analysis"])

# Evaluation
if HAS_EVALUATION and evaluation_router:
    app.include_router(evaluation_router, prefix="/api", tags=["Evaluation"])

# Reporting
if HAS_REPORTING and reporting_router:
    app.include_router(reporting_router, prefix="/api", tags=["Reporting"])

# Workforce Analytics
if HAS_WORKFORCE and workforce_router:
    app.include_router(workforce_router, prefix="/api", tags=["Workforce Analytics"])


@app.on_event("startup")
async def startup_event():
    try:
        summary = run_startup_etl()
        if summary:
            get_loader().status.setdefault("startup_summary", summary)
    except Exception as exc:  # pylint: disable=broad-except
        get_loader().status.setdefault("startup_error", str(exc))


@app.get("/")
async def root():
    """Root endpoint to avoid 404 errors."""
    return {
        "message": "ProdPlan 4.0 API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


@app.get("/api/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

