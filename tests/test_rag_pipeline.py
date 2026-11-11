"""Automated test suite for ChromaDB Vector Database & LangChain RAG Subsystem."""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from backend.schemas import InputRiskPayload
from backend.rag.chroma_manager import ChromaGuidelineManager
from backend.rag.langchain_retriever import LangChainGuidelineRetriever
from backend.rag.langchain_agent import LangChainRAGAgent
from backend.agent import RiskSummarizerAgent
from backend.preprocessing import PreprocessingEngine
from backend.main import app

client = TestClient(app)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def test_knowledge_base_manuals_exist():
    """Verify that domain guideline manuals are present and non-empty."""
    kb_dir = Path(__file__).resolve().parent.parent / "knowledge_base"
    assert kb_dir.exists(), "knowledge_base directory must exist"
    manuals = list(kb_dir.glob("*.md"))
    assert len(manuals) >= 4, f"Expected at least 4 guideline manuals, found {len(manuals)}"


def test_chroma_guideline_manager_indexing():
    """Verify ChromaDB manager loads and indexes corporate rules."""
    mgr = ChromaGuidelineManager()
    guidelines = mgr.get_all_guidelines()
    assert len(guidelines) >= 10, f"Expected >= 10 rules, found {len(guidelines)}"

    rule_ids = {g["rule_id"] for g in guidelines}
    assert "RULE-P-101" in rule_ids  # Roof age
    assert "RULE-H-201" in rule_ids  # Coastal hurricane
    assert "RULE-F-401" in rule_ids  # Frequency ceiling
    assert "RULE-F-402" in rule_ids  # Prior cancellation


def test_semantic_search_retrieves_relevant_rules():
    """Verify semantic vector search returns relevant rules for hazard queries."""
    mgr = ChromaGuidelineManager()
    hits = mgr.search("coastal hurricane storm surge percentage deductible", top_k=3)
    assert len(hits) > 0
    hit_ids = [h["rule_id"] for h in hits]
    assert "RULE-H-201" in hit_ids or "RULE-H-202" in hit_ids


def test_roof_age_guideline_breach_detection():
    """Verify that an older roof (22 years) triggers RULE-P-101 breach."""
    import json
    with open(DATA_DIR / "scenario_3_high_hazard.json", "r", encoding="utf-8") as f:
        payload_data = json.load(f)

    # Inject roof/asset age = 24
    payload_data["policy_request"]["asset_age_years"] = 24
    payload = InputRiskPayload(**payload_data)
    normalized = PreprocessingEngine.normalize(payload)

    mgr = ChromaGuidelineManager()
    retriever = LangChainGuidelineRetriever(mgr)
    retrieved, breaches = retriever.retrieve_guidelines_for_profile(payload, normalized)

    breach_ids = {b.rule_id for b in breaches}
    assert "RULE-P-101" in breach_ids
    assert "RULE-H-201" in breach_ids  # Coastal zone breach


def test_prior_cancellation_breach_detection():
    """Verify that prior cancellation triggers RULE-F-402 breach."""
    import json
    with open(DATA_DIR / "scenario_4_anomaly_refer.json", "r", encoding="utf-8") as f:
        payload_data = json.load(f)

    payload = InputRiskPayload(**payload_data)
    normalized = PreprocessingEngine.normalize(payload)

    mgr = ChromaGuidelineManager()
    retriever = LangChainGuidelineRetriever(mgr)
    _, breaches = retriever.retrieve_guidelines_for_profile(payload, normalized)

    breach_ids = {b.rule_id for b in breaches}
    assert "RULE-F-402" in breach_ids  # Involuntary cancellation
    assert "RULE-F-401" in breach_ids  # High frequency


def test_agent_synthesis_includes_rag_citations():
    """Verify that agent synthesis returns grounded guideline breaches and citations."""
    import json
    with open(DATA_DIR / "scenario_3_high_hazard.json", "r", encoding="utf-8") as f:
        payload_data = json.load(f)

    payload = InputRiskPayload(**payload_data)
    agent = RiskSummarizerAgent()
    report = agent.synthesize(payload)

    assert report.rag_grounding_verified is True
    assert len(report.retrieved_guidelines) > 0
    assert len(report.guideline_breaches) > 0

    # Verify that conditions cite corporate rules
    assert any("RULE-" in c for c in report.recommended_conditions)


def test_guidelines_api_endpoints():
    """Verify REST API endpoints for inspecting vector knowledge base."""
    # List all guidelines
    res_list = client.get("/api/guidelines")
    assert res_list.status_code == 200
    data = res_list.json()
    assert data["total_guidelines"] >= 10
    assert len(data["guidelines"]) >= 10

    # Get specific guideline
    res_rule = client.get("/api/guidelines/RULE-P-101")
    assert res_rule.status_code == 200
    rule_data = res_rule.json()
    assert rule_data["rule_id"] == "RULE-P-101"
    assert "Roof Age" in rule_data["title"]
