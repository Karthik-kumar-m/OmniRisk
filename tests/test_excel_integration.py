"""Automated test suite for insurance_model.xlsx integration."""

import pytest
from fastapi.testclient import TestClient
from backend.excel_loader import ExcelDatasetService
from backend.agent import RiskSummarizerAgent
from backend.main import app

client = TestClient(app)


def test_excel_service_loading():
    """Verify that ExcelDatasetService loads all sheets from insurance_model.xlsx."""
    service = ExcelDatasetService("insurance_model.xlsx")
    assert service.is_loaded is True
    summary = service.get_dataset_summary()
    assert summary["total_customers"] == 120
    assert summary["total_policies"] == 140
    assert summary["total_claims"] == 220
    assert summary["total_payments"] == 1013
    assert summary["total_loss_incurred_usd"] > 10000000


def test_pii_anonymization_in_payload():
    """Verify that generated payloads contain NO personal names or contact PII."""
    service = ExcelDatasetService("insurance_model.xlsx")
    # CUST1000 has FirstName 'Karan', LastName 'Bhat' in the raw Excel sheet
    payload = service.build_input_risk_payload("CUST1000")
    json_str = payload.model_dump_json().lower()

    # Assert names are nowhere in the output payload
    assert "karan" not in json_str
    assert "bhat" not in json_str
    assert "first_name" not in json_str
    assert "last_name" not in json_str
    assert payload.customer_id == "CUST1000-EXCEL"


def test_high_claim_customer_synthesis():
    """Verify that heavy loss customers (e.g., CUST1050 with 9 claims) trigger critical KRIs."""
    service = ExcelDatasetService("insurance_model.xlsx")
    payload = service.build_input_risk_payload("CUST1050")
    assert payload.claim_history.total_claims_count == 9

    agent = RiskSummarizerAgent()
    report = agent.synthesize(payload)

    assert report.verdict in ["DECLINE", "REFER_TO_SENIOR_UW"]
    assert len(report.key_risk_indicators) >= 3
    assert any("FREQ" in kri.code or "PERIL" in kri.code for kri in report.key_risk_indicators)
    assert report.processing_time_ms < 20000.0


def test_clean_customer_synthesis():
    """Verify that 0-claim preferred customers trigger an APPROVED verdict."""
    service = ExcelDatasetService("insurance_model.xlsx")
    clean_list = service.list_customers("CLEAN", limit=5)
    assert len(clean_list) > 0

    cid = clean_list[0]["customer_id"]
    payload = service.build_input_risk_payload(cid)
    assert payload.claim_history.total_claims_count == 0

    agent = RiskSummarizerAgent()
    report = agent.synthesize(payload)

    assert report.verdict == "APPROVE"
    assert report.risk_tier == "TIER_1_PREFERRED"


def test_excel_api_endpoints():
    """Verify all REST API endpoints for the Excel dataset."""
    # Summary
    res_sum = client.get("/api/dataset/summary")
    assert res_sum.status_code == 200
    assert res_sum.json()["total_customers"] == 120

    # Customers list
    res_custs = client.get("/api/dataset/customers?filter_type=HIGH_CLAIMS&limit=5")
    assert res_custs.status_code == 200
    custs = res_custs.json()
    assert len(custs) > 0
    assert custs[0]["claim_count"] >= 2

    # Single customer payload
    res_one = client.get(f"/api/dataset/customer/{custs[0]['customer_id']}")
    assert res_one.status_code == 200
    payload = res_one.json()
    assert "demographics" in payload
    assert "claim_history" in payload

    # Batch evaluate
    res_batch = client.post("/api/dataset/batch-evaluate?limit=5")
    assert res_batch.status_code == 200
    batch = res_batch.json()
    assert batch["portfolio_size_evaluated"] == 5
    assert "verdict_distribution" in batch
