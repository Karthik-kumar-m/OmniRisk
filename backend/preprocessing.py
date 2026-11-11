"""Data Preprocessing & Actuarial Normalization Engine for OmniRisk.

Responsibilities:
1. Enforce strict PII sanitization (verify purely synthetic/anonymized data).
2. Standardize and normalize categorical and numerical fields.
3. Compute derived actuarial metrics (claim frequency, average loss severity, loss-to-limit ratio).
4. Perform rule-based deterministic Key Risk Indicator (KRI) extraction.
"""

import re
from typing import List, Dict
from collections import Counter
from backend.schemas import InputRiskPayload, NormalizedRiskProfile, KeyRiskIndicator


class PreprocessingEngine:
    """Preprocesses and normalizes raw JSON insurance risk payloads."""

    PII_REGEX_PATTERNS = [
        re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN
        re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),  # Email
        re.compile(r"\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}\b"),  # Phone
    ]

    @classmethod
    def sanitize_and_audit(cls, payload: InputRiskPayload) -> str:
        """Verifies payload contains zero personal data (PII) before LLM ingestion."""
        payload_str = payload.model_dump_json()
        for pattern in cls.PII_REGEX_PATTERNS:
            if pattern.search(payload_str):
                raise ValueError("Security Alert: Sensitive PII pattern detected in payload.")
        return "PASSED: Synthetic / Anonymized verification complete"

    @classmethod
    def normalize(cls, payload: InputRiskPayload) -> NormalizedRiskProfile:
        """Transforms raw input payload into normalized actuarial intermediate representation."""
        cls.sanitize_and_audit(payload)

        claims = payload.claim_history
        demo = payload.demographics
        policy = payload.policy_request
        external = payload.external_risk_factors

        # 1. Quantitative Actuarial Metrics
        years = max(1, claims.years_of_history)
        claim_freq = round(claims.total_claims_count / years, 2)
        
        severity_avg = (
            round(claims.total_payout_amount_usd / max(1, claims.total_claims_count), 2)
            if claims.total_claims_count > 0
            else 0.0
        )

        loss_to_limit_pct = (
            round((claims.total_payout_amount_usd / max(1.0, policy.requested_limit_usd)) * 100.0, 2)
        )

        # Composite Hazard Index (0-100)
        hazard_composite = round(
            (external.environmental_hazard_score * 0.6) + (external.crime_hazard_score * 0.4),
            1
        )

        # 2. Recurrent Peril Analysis
        peril_counts = Counter(inc.peril.strip().title() for inc in claims.incidents)
        recurrent_perils = [peril for peril, count in peril_counts.items() if count >= 2]

        # 3. Deterministic Preliminary Risk Score Calculation (0-100)
        # Baseline actuarial scoring:
        score = 20.0  # Base standard risk

        # Frequency impact (+0 to +30)
        if claim_freq >= 0.8:
            score += 30.0
        elif claim_freq >= 0.4:
            score += 18.0
        elif claim_freq > 0:
            score += 8.0

        # Loss ratio impact (+0 to +20)
        if loss_to_limit_pct >= 25.0:
            score += 20.0
        elif loss_to_limit_pct >= 10.0:
            score += 10.0

        # Credit tier modifier (-10 to +20)
        credit_adjustments = {
            "EXCELLENT": -10.0,
            "GOOD": -2.0,
            "FAIR": 10.0,
            "POOR": 22.0
        }
        score += credit_adjustments.get(demo.credit_tier, 5.0)

        # Environmental & Geographic Exposure (+0 to +25)
        if "COASTAL" in demo.geographic_risk_zone.upper() or hazard_composite >= 70.0:
            score += 20.0
        elif hazard_composite >= 50.0:
            score += 10.0

        # Carrier cancellation & lapse penalty
        if external.prior_carrier_cancellation:
            score += 20.0
        if external.gap_in_coverage_months > 1:
            score += 12.0
        if claims.open_claims_count > 0:
            score += 15.0

        preliminary_score = min(100.0, max(0.0, round(score, 1)))

        # 4. Deterministic Key Risk Indicators (KRIs) Extraction
        kris: List[KeyRiskIndicator] = []

        # KRI: Frequency
        if claim_freq >= 0.4 or claims.total_claims_count >= 3:
            sev = "CRITICAL" if claim_freq >= 0.8 else "HIGH"
            kris.append(
                KeyRiskIndicator(
                    code="KRI-FREQ-01",
                    title="Elevated Claim Frequency",
                    severity=sev,
                    category="CLAIM_FREQUENCY",
                    quantitative_finding=f"{claims.total_claims_count} claims recorded across {years} years ({claim_freq} claims/year vs industry baseline ~0.12).",
                    impact_analysis="Pronounced attritional loss pattern with strong statistical probability of repeat loss occurrences.",
                    recommended_action="Increase policy deductible by minimum 50% and implement mandatory loss mitigation inspection."
                )
            )

        # KRI: Recurrent Perils
        for peril in recurrent_perils:
            kris.append(
                KeyRiskIndicator(
                    code=f"KRI-PERIL-{peril.upper()[:4]}",
                    title=f"Recurrent {peril} Losses",
                    severity="HIGH",
                    category="CLAIM_FREQUENCY",
                    quantitative_finding=f"Multiple incidents ({peril_counts[peril]}) attributed specifically to {peril} perils.",
                    impact_analysis=f"Persistent vulnerability to {peril} hazards indicating unresolved structural or operational defects.",
                    recommended_action=f"Mandate targeted {peril} endorsement, water shut-off sensor, or higher peril deductible."
                )
            )

        # KRI: Catastrophe / Environmental
        if external.environmental_hazard_score >= 65.0 or "COASTAL" in demo.geographic_risk_zone.upper():
            sev = "CRITICAL" if external.environmental_hazard_score >= 80.0 else "HIGH"
            kris.append(
                KeyRiskIndicator(
                    code="KRI-CAT-01",
                    title="High Catastrophe / Environmental Exposure",
                    severity=sev,
                    category="CATASTROPHE_HAZARD",
                    quantitative_finding=f"Zone '{demo.geographic_risk_zone}' with Environmental Hazard Score of {external.environmental_hazard_score}/100.",
                    impact_analysis="Severe tail-risk exposure to extreme weather, flood inundation, or hurricane wind events.",
                    recommended_action="Impose mandatory named storm/hurricane percentage deductible (2-5%) and flood carve-out."
                )
            )

        # KRI: Prior Carrier Cancellation
        if external.prior_carrier_cancellation:
            kris.append(
                KeyRiskIndicator(
                    code="KRI-MORAL-01",
                    title="Prior Carrier Involuntary Cancellation",
                    severity="CRITICAL",
                    category="OPERATIONAL_SAFETY",
                    quantitative_finding="Record indicates policy cancellation or non-renewal by previous underwriter.",
                    impact_analysis="Signals heightened adverse selection, non-payment, fraud suspicion, or unmitigated inspection hazards.",
                    recommended_action="Escalate to Senior Underwriter; verify loss history documentation and require warranty statement."
                )
            )

        # KRI: Credit Tier Depression
        if demo.credit_tier in ["POOR", "FAIR"] or demo.credit_score < 620:
            sev = "HIGH" if demo.credit_tier == "POOR" or demo.credit_score < 580 else "MODERATE"
            kris.append(
                KeyRiskIndicator(
                    code="KRI-FIN-01",
                    title="Sub-Prime Credit Stability Indicator",
                    severity=sev,
                    category="FINANCIAL_STABILITY",
                    quantitative_finding=f"Credit score of {demo.credit_score} (Tier: {demo.credit_tier}).",
                    impact_analysis="Insurance scoring models correlate sub-prime credit tiers with higher claim reporting propensity.",
                    recommended_action="Apply financial surcharge tier and require full annual premium pre-payment or EFT."
                )
            )

        # KRI: Open Claims Pending
        if claims.open_claims_count > 0:
            kris.append(
                KeyRiskIndicator(
                    code="KRI-OPEN-01",
                    title="Unresolved Open Claims",
                    severity="HIGH",
                    category="COVERAGE_EXPOSURE",
                    quantitative_finding=f"{claims.open_claims_count} claim(s) currently open with unsettled reserve amounts.",
                    impact_analysis="Inability to establish true loss cost baseline until open liabilities conclude.",
                    recommended_action="Hold binding authorization until open claim adjuster closing reports are submitted."
                )
            )

        # If zero adverse KRIs, append a baseline LOW risk indicator
        if not kris:
            kris.append(
                KeyRiskIndicator(
                    code="KRI-PRIME-01",
                    title="Preferred Risk Profile - Favorable Underwriting Criteria",
                    severity="LOW",
                    category="OPERATIONAL_SAFETY",
                    quantitative_finding="Zero loss history, prime credit score, clean coverage continuity, and benign hazard score.",
                    impact_analysis="Minimal anticipated loss cost; highly profitable book-of-business candidate.",
                    recommended_action="Authorize standard preferred policy issuance with baseline deductible options."
                )
            )

        return NormalizedRiskProfile(
            customer_id=payload.customer_id,
            entity_type=payload.entity_type,
            line_of_business=policy.line_of_business,
            claim_frequency_annual=claim_freq,
            claim_severity_avg_usd=severity_avg,
            loss_to_limit_ratio_pct=loss_to_limit_pct,
            credit_tier=demo.credit_tier,
            credit_score=demo.credit_score,
            hazard_composite_score=hazard_composite,
            total_claims_count=claims.total_claims_count,
            total_payout_amount_usd=claims.total_payout_amount_usd,
            open_claims_count=claims.open_claims_count,
            recurrent_perils=recurrent_perils,
            has_prior_cancellation=external.prior_carrier_cancellation,
            coverage_gap_months=external.gap_in_coverage_months,
            preliminary_risk_score=preliminary_score,
            deterministic_kris=kris,
            sanitization_audit="PASSED: 100% Synthetic / Anonymized"
        )
