"""Data schemas for the Automated Risk Profile Summarizer (OmniRisk).

Includes input payload validation, normalized actuarial representations,
and structured GenAI synthesis outputs.
"""

from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, model_validator


class IncidentRecord(BaseModel):
    year: int = Field(..., description="Year the loss incident occurred", ge=2000, le=2030)
    peril: str = Field(..., description="Type of peril, e.g., Water, Wind/Hail, Fire, Collision, Liability, Theft")
    payout_usd: float = Field(..., description="Paid + reserved amount in USD", ge=0.0)
    at_fault: bool = Field(False, description="Whether policyholder was at fault")
    description: str = Field(..., description="Brief factual description of the incident")


class CustomerDemographics(BaseModel):
    age: Optional[int] = Field(None, description="Age of policyholder (synthetic individual)", ge=18, le=100)
    years_in_business: Optional[int] = Field(None, description="Years operating (synthetic commercial)", ge=0, le=150)
    credit_score: int = Field(..., description="FICO/Commercial credit index", ge=300, le=850)
    credit_tier: Literal["EXCELLENT", "GOOD", "FAIR", "POOR"] = Field(...)
    geographic_risk_zone: str = Field(
        ...,
        description="Hazard rating zone, e.g., TIER_1_COASTAL, TIER_2_INLAND, WILDFIRE_URBAN_INTERFACE, METRO_SUBURBAN"
    )
    annual_revenue_usd: Optional[float] = Field(None, ge=0.0)


class PolicyRequest(BaseModel):
    line_of_business: Literal[
        "PROPERTY_HOMEOWNERS",
        "COMMERCIAL_PROPERTY",
        "COMMERCIAL_AUTO",
        "CYBER_LIABILITY"
    ] = Field(...)
    requested_limit_usd: float = Field(..., ge=1000.0)
    deductible_usd: float = Field(..., ge=0.0)
    asset_age_years: int = Field(0, ge=0)
    asset_category_or_construction: str = Field(..., description="e.g. Masonry Non-Combustible, Frame, Fleet Class 6")
    protection_class_or_security: str = Field(..., description="Fire Protection Class (1-10) or ISO Security Class")


class ClaimHistory(BaseModel):
    years_of_history: int = Field(5, ge=1, le=10)
    total_claims_count: int = Field(..., ge=0)
    total_payout_amount_usd: float = Field(..., ge=0.0)
    open_claims_count: int = Field(0, ge=0)
    incidents: List[IncidentRecord] = Field(default_factory=list)


class ExternalRiskFactors(BaseModel):
    prior_carrier_cancellation: bool = Field(False)
    gap_in_coverage_months: int = Field(0, ge=0)
    environmental_hazard_score: float = Field(..., ge=0.0, le=100.0, description="Composite flood/wind/wildfire score 0-100")
    crime_hazard_score: float = Field(..., ge=0.0, le=100.0, description="Regional crime/theft index 0-100")
    safety_compliance_certified: bool = Field(True)
    special_hazards: List[str] = Field(default_factory=list)


class InputRiskPayload(BaseModel):
    """Raw structured risk JSON payload ingested by OmniRisk."""
    customer_id: str = Field(..., description="Anonymized ID, e.g. SYNTH-9821-US")
    entity_type: Literal["INDIVIDUAL", "COMMERCIAL"]
    demographics: CustomerDemographics
    policy_request: PolicyRequest
    claim_history: ClaimHistory
    external_risk_factors: ExternalRiskFactors

    @model_validator(mode="after")
    def verify_no_pii_strings(self):
        # Strict rule: Ensure no obvious PII fields exist
        forbidden_keywords = ["ssn", "social_security", "first_name", "last_name", "full_name", "phone", "email"]
        raw_dump = self.model_dump_json().lower()
        for kw in forbidden_keywords:
            if f'"{kw}"' in raw_dump:
                raise ValueError(f"PII field violation detected: '{kw}' is prohibited.")
        return self


class KeyRiskIndicator(BaseModel):
    """Key Risk Indicator (KRI) highlighted for underwriting review."""
    code: str = Field(..., description="Identifier, e.g. KRI-FREQ-01")
    title: str = Field(..., description="Short title of the risk indicator")
    severity: Literal["CRITICAL", "HIGH", "MODERATE", "LOW"] = Field(...)
    category: Literal[
        "CLAIM_FREQUENCY",
        "CATASTROPHE_HAZARD",
        "FINANCIAL_STABILITY",
        "OPERATIONAL_SAFETY",
        "COVERAGE_EXPOSURE"
    ] = Field(...)
    quantitative_finding: str = Field(..., description="Concrete quantitative evidence backing this KRI")
    impact_analysis: str = Field(..., description="Actuarial/underwriting impact on expected loss")
    recommended_action: str = Field(..., description="Endorsement, surcharge, warranty, or underwriting exclusion")


class NormalizedRiskProfile(BaseModel):
    """Normalized, aggregated representation produced by preprocessing engine."""
    customer_id: str
    entity_type: str
    line_of_business: str
    claim_frequency_annual: float
    claim_severity_avg_usd: float
    loss_to_limit_ratio_pct: float
    credit_tier: str
    credit_score: int
    hazard_composite_score: float
    total_claims_count: int
    total_payout_amount_usd: float
    open_claims_count: int
    recurrent_perils: List[str]
    has_prior_cancellation: bool
    coverage_gap_months: int
    preliminary_risk_score: float = Field(..., ge=0.0, le=100.0, description="Overall quantitative risk index (0=Safe, 100=Severe)")
    deterministic_kris: List[KeyRiskIndicator] = Field(default_factory=list)
    sanitization_audit: str = Field("PASSED: 100% Synthetic / Anonymized")


class UnderwritingSynthesisReport(BaseModel):
    """Complete synthesized output generated by the GenAI Agent."""
    customer_id: str
    line_of_business: str
    verdict: Literal["APPROVE", "APPROVE_WITH_CONDITIONS", "REFER_TO_SENIOR_UW", "DECLINE"]
    verdict_explanation: str
    confidence_score_pct: float
    risk_tier: Literal["TIER_1_PREFERRED", "TIER_2_STANDARD", "TIER_3_SUBSTANDARD", "TIER_4_DECLINABLE"]
    executive_summary: str = Field(..., description="Concise, synthesized narrative for underwriter decisioning")
    key_risk_indicators: List[KeyRiskIndicator]
    loss_expectancy_insights: str
    recommended_conditions: List[str]
    suggested_deductible_adjustment_usd: Optional[float] = None
    actuarial_metrics: Dict[str, Any]
    processing_time_ms: float
    ai_generation_engine: str
