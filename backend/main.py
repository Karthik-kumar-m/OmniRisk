"""FastAPI Application Server for OmniRisk: Automated Risk Profile Summarizer."""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()
from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.schemas import (
    InputRiskPayload,
    UnderwritingSynthesisReport,
)
from backend.agent import RiskSummarizerAgent, GEMINI_AVAILABLE
from backend.evaluator import AccuracyEvaluator
from backend.excel_loader import ExcelDatasetService

app = FastAPI(
    title="OmniRisk: Automated Risk Profile Summarizer",
    description="Enterprise GenAI application for insurance underwriting risk synthesis and Key Risk Indicator (KRI) extraction.",
    version="1.0.0"
)

# Enable CORS for flexible integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path("data")
FRONTEND_DIR = Path("frontend")

agent = RiskSummarizerAgent()
evaluator = AccuracyEvaluator()
excel_service = ExcelDatasetService("insurance_model.xlsx")


SCENARIOS_META = [
    {
        "id": "scenario_1_preferred",
        "file": "scenario_1_preferred.json",
        "name": "Scenario 1: Preferred Low-Risk Homeowner",
        "description": "Zero loss history, FICO 795, prime masonry construction in low-hazard inland zone.",
        "badge": "LOW RISK",
        "badge_color": "emerald"
    },
    {
        "id": "scenario_2_moderate",
        "file": "scenario_2_moderate.json",
        "name": "Scenario 2: Commercial Auto Van Fleet",
        "description": "7 years operating, 2 minor attritional claims ($18.2k), telematics tracking enabled.",
        "badge": "MODERATE RISK",
        "badge_color": "blue"
    },
    {
        "id": "scenario_3_high_hazard",
        "file": "scenario_3_high_hazard.json",
        "name": "Scenario 3: Coastal Property with Recurrent Water Loss",
        "description": "Tier 1 Coastal hurricane zone, 2 repeat water damage claims, environmental hazard 84.5/100.",
        "badge": "HIGH HAZARD",
        "badge_color": "amber"
    },
    {
        "id": "scenario_4_anomaly_refer",
        "file": "scenario_4_anomaly_refer.json",
        "name": "Scenario 4: High Anomaly Commercial Risk with Cancellation",
        "description": "Prior carrier cancellation, 4 claims ($215k), 1 active open claim, poor credit, safety citations.",
        "badge": "CRITICAL ANOMALY",
        "badge_color": "rose"
    }
]


@app.get("/api/health")
async def health_check():
    """Health status, GenAI model availability, and Excel dataset readiness."""
    has_gemini_key = bool(os.getenv("GEMINI_API_KEY"))
    model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    active_engine = f"Google Gemini ({model_name})" if has_gemini_key and GEMINI_AVAILABLE else "OmniRisk Actuarial Heuristic NLG Engine"
    return {
        "status": "healthy",
        "service": "OmniRisk Summarizer",
        "gemini_sdk_installed": GEMINI_AVAILABLE,
        "gemini_api_key_configured": has_gemini_key,
        "active_engine": active_engine,
        "speed_sla_seconds": 10.0,
        "accuracy_target_pct": 85.0,
        "excel_dataset_loaded": excel_service.is_loaded,
        "excel_total_customers": len(excel_service.customers_df) if excel_service.is_loaded else 0,
        "rag_vector_db_ready": bool(agent.chroma_manager),
        "indexed_guidelines_count": len(agent.chroma_manager.get_all_guidelines()),
    }


@app.get("/api/guidelines")
async def list_guidelines():
    """Returns all indexed corporate underwriting guidelines in the Vector Store."""
    all_g = agent.chroma_manager.get_all_guidelines()
    return {
        "total_guidelines": len(all_g),
        "collection_name": agent.chroma_manager.COLLECTION_NAME,
        "guidelines": all_g
    }


@app.get("/api/guidelines/{rule_id}")
async def get_guideline_by_id(rule_id: str):
    """Retrieves full text and metadata for a specific corporate guideline rule."""
    all_g = agent.chroma_manager.get_all_guidelines()
    match = next((g for g in all_g if g["rule_id"].upper() == rule_id.upper()), None)
    if not match:
        raise HTTPException(status_code=404, detail=f"Rule '{rule_id}' not found in corporate guidelines.")
    return match


@app.get("/api/scenarios")
async def list_scenarios() -> List[Dict[str, Any]]:
    """Returns available synthetic risk test scenarios."""
    return SCENARIOS_META


@app.get("/api/scenarios/{scenario_id}")
async def get_scenario_payload(scenario_id: str) -> Dict[str, Any]:
    """Retrieves full JSON payload for a scenario."""
    meta = next((s for s in SCENARIOS_META if s["id"] == scenario_id), None)
    if not meta:
        raise HTTPException(status_code=404, detail="Scenario not found")

    file_path = DATA_DIR / meta["file"]
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Scenario file '{meta['file']}' not found on disk")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.post("/api/summarize", response_model=UnderwritingSynthesisReport)
async def summarize_risk_profile(payload: InputRiskPayload) -> UnderwritingSynthesisReport:
    """Ingests fragmented synthetic JSON risk payload and synthesizes an actionable underwriting summary."""
    try:
        report = agent.synthesize(payload)
        return report
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Synthesis failed: {e}")


@app.post("/api/evaluate")
async def evaluate_accuracy() -> Dict[str, Any]:
    """Runs the benchmark suite against ground truth to verify accuracy >85% and speed <10s."""
    try:
        results = evaluator.run_benchmark()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Benchmark execution failed: {e}")


# ==========================================
# EXCEL DATASET ENDPOINTS (insurance_model.xlsx)
# ==========================================

@app.get("/api/dataset/summary")
async def get_excel_summary() -> Dict[str, Any]:
    """Returns high-level statistics and metadata for the loaded Excel dataset."""
    if not excel_service.is_loaded:
        raise HTTPException(status_code=503, detail="insurance_model.xlsx is not loaded.")
    return excel_service.get_dataset_summary()


@app.get("/api/dataset/customers")
async def list_excel_customers(
    filter_type: str = Query("ALL", pattern="^(ALL|HIGH_CLAIMS|LAPSED|CLEAN)$"),
    search: Optional[str] = Query(None),
    limit: int = Query(120, ge=1, le=200)
) -> List[Dict[str, Any]]:
    """Lists customers from the Excel dataset with aggregated claim and policy metrics."""
    if not excel_service.is_loaded:
        raise HTTPException(status_code=503, detail="insurance_model.xlsx is not loaded.")
    return excel_service.list_customers(filter_type=filter_type, search=search, limit=limit)


@app.get("/api/dataset/customer/{customer_id}")
async def get_excel_customer_payload(customer_id: str) -> Dict[str, Any]:
    """Transforms relational records for a customer into a 100% PII-free InputRiskPayload."""
    if not excel_service.is_loaded:
        raise HTTPException(status_code=503, detail="insurance_model.xlsx is not loaded.")
    try:
        payload = excel_service.build_input_risk_payload(customer_id)
        return payload.model_dump()
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to transform customer: {e}")


@app.get("/api/dataset/customer/{customer_id}/proof")
async def get_excel_customer_proof(customer_id: str) -> Dict[str, Any]:
    """Returns verifiable relational proof records across all sheets for a specific customer."""
    if not excel_service.is_loaded:
        raise HTTPException(status_code=503, detail="insurance_model.xlsx is not loaded.")
    try:
        return excel_service.get_customer_proof(customer_id)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve customer proof: {e}")


@app.post("/api/dataset/batch-evaluate")
async def batch_evaluate_excel_portfolio(limit: int = Query(20, ge=1, le=100)) -> Dict[str, Any]:
    """Runs underwriting synthesis on top portfolio customers from the Excel file."""
    if not excel_service.is_loaded:
        raise HTTPException(status_code=503, detail="insurance_model.xlsx is not loaded.")
    try:
        return excel_service.batch_evaluate_portfolio(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch evaluation failed: {e}")


# Serve UI static assets
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory="frontend"), name="static")

    @app.get("/")
    async def serve_index():
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"message": "OmniRisk API is running. Frontend index.html not found."}
