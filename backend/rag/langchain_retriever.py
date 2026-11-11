"""LangChain Retriever Abstraction for OmniRisk Corporate Guidelines.

Constructs multi-attribute risk queries from normalized applicant profiles,
executes semantic retrieval via ChromaDB, and identifies candidate policy breaches.
"""

from typing import List, Dict, Any, Tuple
from backend.schemas import InputRiskPayload, NormalizedRiskProfile, GuidelineBreach, RetrievedGuideline
from backend.rag.chroma_manager import ChromaGuidelineManager

try:
    from langchain_core.documents import Document
    from langchain_core.retrievers import BaseRetriever
    LANGCHAIN_CORE_AVAILABLE = True
except ImportError:
    LANGCHAIN_CORE_AVAILABLE = False


class LangChainGuidelineRetriever:
    """Orchestrates LangChain semantic retrieval and corporate rule compliance checks."""

    def __init__(self, chroma_manager: ChromaGuidelineManager):
        self.chroma_manager = chroma_manager

    def retrieve_guidelines_for_profile(
        self,
        payload: InputRiskPayload,
        normalized: NormalizedRiskProfile
    ) -> Tuple[List[RetrievedGuideline], List[GuidelineBreach]]:
        """Extracts candidate queries, executes vector search, and identifies guideline breaches."""
        queries = self._build_semantic_queries(payload, normalized)

        # Retrieve top hits across all generated queries
        retrieved_map: Dict[str, RetrievedGuideline] = {}
        for q in queries:
            hits = self.chroma_manager.search(q, top_k=2)
            for h in hits:
                r_id = h["rule_id"]
                if r_id not in retrieved_map or h["relevance_score"] > retrieved_map[r_id].relevance_score:
                    retrieved_map[r_id] = RetrievedGuideline(
                        rule_id=r_id,
                        manual=h["manual_source"],
                        title=h["title"],
                        excerpt=h["excerpt"],
                        relevance_score=h["relevance_score"]
                    )

        retrieved_list = sorted(list(retrieved_map.values()), key=lambda x: x.relevance_score, reverse=True)[:5]

        # Audit profile against retrieved corporate guidelines to isolate explicit breaches
        breaches = self._audit_guideline_breaches(payload, normalized)

        return retrieved_list, breaches

    def _build_semantic_queries(
        self,
        payload: InputRiskPayload,
        normalized: NormalizedRiskProfile
    ) -> List[str]:
        """Constructs targeted semantic queries based on applicant attributes."""
        queries = []

        # 1. Geographic & Hazard Exposure Query
        geo = payload.demographics.geographic_risk_zone or ""
        env = payload.external_risk_factors.environmental_hazard_score
        if "COASTAL" in geo.upper() or env >= 60.0:
            queries.append(f"coastal hurricane storm surge percentage deductible flood carve-out {geo}")
        if "WILDFIRE" in geo.upper() or env >= 70.0:
            queries.append("wildfire urban interface defensible brush clearance ember mesh")

        # 2. Asset & Property Scope Query
        line = str(getattr(payload.policy_request.line_of_business, "value", payload.policy_request.line_of_business))
        asset_age = payload.policy_request.asset_age_years
        if "PROPERTY" in line or "HOMEOWNERS" in line:
            queries.append(f"roof age limitation maximum permissible replacement cost ACV inspection {asset_age} years")
            queries.append("building construction class masonry non-combustible automatic fire sprinkler")
        elif "AUTO" in line or "FLEET" in line:
            queries.append("commercial auto fleet loss ratio ceiling 40% GPS telematics safety program")

        # 3. Claims & Loss History Query
        freq = normalized.claim_frequency_annual
        if freq > 0.3 or normalized.total_claims_count >= 2:
            queries.append(f"historical claim frequency ceiling 0.40 claims per year loss ratio {normalized.total_claims_count} claims")
        if normalized.recurrent_perils:
            queries.append(f"recurrent loss causes repeat water collision peril deductible increase")

        # 4. Underwriting Flags & Moral Hazard
        if payload.external_risk_factors.prior_carrier_cancellation:
            queries.append("prior carrier non-renewal involuntary cancellation moral hazard 36 months")
        if payload.demographics.credit_score and payload.demographics.credit_score < 620:
            queries.append(f"credit score financial stability poor tier 100% upfront annual premium {payload.demographics.credit_score}")

        # Fallback query if profile is pristine
        if not queries:
            queries.append("standard underwriting preferred tier eligibility baseline terms")

        return queries

    def _audit_guideline_breaches(
        self,
        payload: InputRiskPayload,
        normalized: NormalizedRiskProfile
    ) -> List[GuidelineBreach]:
        """Performs rigorous deterministic verification against all corporate rules."""
        breaches: List[GuidelineBreach] = []

        # RULE-P-101: Roof Age Limit (Threshold: 20 Years)
        asset_age = payload.policy_request.asset_age_years
        lob = str(getattr(payload.policy_request.line_of_business, "value", payload.policy_request.line_of_business))
        if ("PROPERTY" in lob or "HOMEOWNERS" in lob) and asset_age >= 20:
            breaches.append(GuidelineBreach(
                rule_id="RULE-P-101",
                title="Roof Age Limitation Exceeded",
                manual_source="Commercial Property Underwriting Guidelines Manual",
                corporate_threshold="Maximum permissible roof age is 20 years for standard RCV coverage",
                applicant_observed=f"Insured roof/asset age is {asset_age} years",
                severity="HIGH" if asset_age < 25 else "CRITICAL",
                actionable_mitigation="Mandate Form CP-04-18 (Roof Actual Cash Value Carve-Out) or licensed engineer inspection."
            ))

        # RULE-H-201: Tier 1 Coastal Zone (Threshold: Hurricane % Deductible)
        geo = payload.demographics.geographic_risk_zone or ""
        if "COASTAL" in geo.upper() or "TIER_1" in geo.upper():
            breaches.append(GuidelineBreach(
                rule_id="RULE-H-201",
                title="Coastal Hurricane Exposure Zone",
                manual_source="Natural Hazard, Flood, and Catastrophe Underwriting Guidelines",
                corporate_threshold="Tier 1 Coastal assets barred from standard baseline all-peril deductibles",
                applicant_observed=f"Property located in {geo}",
                severity="CRITICAL",
                actionable_mitigation="Form CP-10-38 (Mandatory Named Hurricane Percentage Deductible 2%–5%) and flood exclusion."
            ))

        # RULE-F-401: Claim Frequency Ceiling (Threshold: 0.40 Claims/Year)
        if normalized.claim_frequency_annual > 0.40 or normalized.total_claims_count >= 3:
            breaches.append(GuidelineBreach(
                rule_id="RULE-F-401",
                title="Claim Frequency Ceiling Exceeded",
                manual_source="Financial Stability, Moral Hazard, and Loss Threshold Guidelines",
                corporate_threshold="Annual claim frequency must not exceed 0.40 claims/year (max 2 claims in 5 years)",
                applicant_observed=f"Observed frequency: {normalized.claim_frequency_annual} claims/yr ({normalized.total_claims_count} claims in 5 years)",
                severity="CRITICAL" if normalized.claim_frequency_annual >= 0.6 else "HIGH",
                actionable_mitigation="Increase policy deductible by at least 50% across affected perils and mandate loss mitigation audit."
            ))

        # RULE-F-402: Prior Carrier Involuntary Cancellation (Threshold: 0 Cancellations)
        if payload.external_risk_factors.prior_carrier_cancellation:
            breaches.append(GuidelineBreach(
                rule_id="RULE-F-402",
                title="Involuntary Carrier Cancellation / Non-Renewal",
                manual_source="Financial Stability, Moral Hazard, and Loss Threshold Guidelines",
                corporate_threshold="Zero prior carrier involuntary non-renewals permitted within preceding 36 months",
                applicant_observed="Applicant flagged for prior carrier involuntary non-renewal / cancellation",
                severity="CRITICAL",
                actionable_mitigation="Binding authority revoked; escalate to Senior Vice President review with loss warranty statement."
            ))

        # RULE-F-403: Sub-Prime Credit Stability (Threshold: Score >= 580)
        score = payload.demographics.credit_score
        if score and score < 580:
            breaches.append(GuidelineBreach(
                rule_id="RULE-F-403",
                title="Sub-Prime Credit Solvency Standard",
                manual_source="Financial Stability, Moral Hazard, and Loss Threshold Guidelines",
                corporate_threshold="Minimum acceptable credit score is 580; installment billing barred for scores < 580",
                applicant_observed=f"Credit score is {score} (POOR / Sub-Prime)",
                severity="HIGH",
                actionable_mitigation="Require 100% upfront annual premium prepayment via EFT escrow (no installment billing)."
            ))

        # RULE-C-301: Commercial Fleet Loss Ratio (Threshold: 40%)
        if "AUTO" in lob or "FLEET" in lob:
            loss_ratio = normalized.loss_to_limit_ratio_pct
            if loss_ratio > 40.0 or normalized.total_claims_count >= 3:
                breaches.append(GuidelineBreach(
                    rule_id="RULE-C-301",
                    title="Fleet Loss Ratio Ceiling Exceeded",
                    manual_source="Commercial Automobile & Casualty Fleet Underwriting Guidelines",
                    corporate_threshold="Maximum permissible 5-year cumulative fleet loss ratio is 40%",
                    applicant_observed=f"Fleet loss ratio is {loss_ratio}% ({normalized.total_claims_count} claims totaling ${normalized.total_payout_amount_usd:,.0f})",
                    severity="CRITICAL",
                    actionable_mitigation="Referral to Senior Underwriting VP, minimum $5,000 collision deductible, and mandatory safety audit."
                ))

        return breaches
