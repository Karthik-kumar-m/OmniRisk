"""Automated unit and integration test suite for OmniRisk."""

import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from backend.schemas import InputRiskPayload
from backend.preprocessing import PreprocessingEngine
from backend.agent import RiskSummarizerAgent
from backend.evaluator import AccuracyEvaluator
from backend.main import app

client = TestClient(app)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def test_pii_sanitization_rejects_ssn():
    """Verify that any payload containing PII is strictly rejected."""
    with open(DATA_DIR / "scenario_1_preferred.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Inject forbidden email or SSN pattern
    data["customer_id"] = "SSN: 123-45-6789"
    with pytest.raises(ValueError):
        payload = InputRiskPayload(**data)
        PreprocessingEngine.sanitize_and_audit(payload)


def test_preprocessing_and_normalization():
    """Verify actuarial derived calculations."""
    with open(DATA_DIR / "scenario_3_high_hazard.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    payload = InputRiskPayload(**data)
    normalized = PreprocessingEngine.normalize(payload)

    # 3 claims in 5 years -> 0.6 claims/year
    assert normalized.claim_frequency_annual == 0.6
    assert normalized.total_claims_count == 3
    assert "Water" in normalized.recurrent_perils
    assert any(k.code == "KRI-PERIL-WATE" for k in normalized.deterministic_kris)
    assert any(k.code == "KRI-CAT-01" for k in normalized.deterministic_kris)


def test_agent_synthesis_schema_compliance():
    """Verify agent output matches UnderwritingSynthesisReport structure."""
    with open(DATA_DIR / "scenario_1_preferred.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    payload = InputRiskPayload(**data)
    agent = RiskSummarizerAgent()
    report = agent.synthesize(payload)

    assert report.customer_id == "SYNTH-1092-US"
    assert report.verdict == "APPROVE"
    assert report.risk_tier == "TIER_1_PREFERRED"
    assert len(report.executive_summary) > 50
    assert report.processing_time_ms < 10000.0  # Speed constraint < 10s


def test_accuracy_benchmark_target_met():
    """Verify that benchmark accuracy meets or exceeds the 85% requirement."""
    evaluator = AccuracyEvaluator()
    res = evaluator.run_benchmark()
    assert res["composite_accuracy_pct"] >= 85.0
    assert res["accuracy_target_met"] is True
    assert res["speed_target_met"] is True
    assert res["average_latency_ms"] < 10000.0


def test_api_endpoints():
    """Verify FastAPI endpoints."""
    # Health check
    res_health = client.get("/api/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"

    # Scenarios list
    res_scenarios = client.get("/api/scenarios")
    assert res_scenarios.status_code == 200
    scenarios = res_scenarios.json()
    assert len(scenarios) >= 4

    # Summarize endpoint
    with open(DATA_DIR / "scenario_2_moderate.json", "r", encoding="utf-8") as f:
        payload_data = json.load(f)
    res_summarize = client.post("/api/summarize", json=payload_data)
    assert res_summarize.status_code == 200
    data = res_summarize.json()
    assert "verdict" in data
    assert "key_risk_indicators" in data
    assert "executive_summary" in data

    # Evaluate endpoint
    res_eval = client.post("/api/evaluate")
    assert res_eval.status_code == 200
    eval_data = res_eval.json()
    assert eval_data["composite_accuracy_pct"] >= 85.0
