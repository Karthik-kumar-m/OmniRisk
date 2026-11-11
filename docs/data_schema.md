# OmniRisk Data Schema Documentation

## 1. Overview & Privacy Principles
The **OmniRisk Automated Risk Profile Summarizer** operates under a strict **Zero-PII (Personally Identifiable Information) Policy**. The system is designed specifically to ingest fragmented, synthetic, or anonymized customer risk payloads. It performs pre-ingestion regex sanitization to block any unintentional transmission of SSNs, personal names, phone numbers, or email addresses.

---

## 2. Ingestion Payload Schema (`InputRiskPayload`)

The input payload is submitted as a structured JSON object containing four discrete modules:

```json
{
  "customer_id": "SYNTH-8492-US",
  "entity_type": "INDIVIDUAL",
  "demographics": { ... },
  "policy_request": { ... },
  "claim_history": { ... },
  "external_risk_factors": { ... }
}
```

### Module Specifications

### 2.1 Root Metadata
| Field | Type | Description | Example / Constraints |
| :--- | :--- | :--- | :--- |
| `customer_id` | `string` | Anonymized synthetic identifier | `"SYNTH-1092-US"` |
| `entity_type` | `enum` | Legal entity classification | `"INDIVIDUAL"` or `"COMMERCIAL"` |

### 2.2 `demographics`
| Field | Type | Description | Constraints |
| :--- | :--- | :--- | :--- |
| `age` | `integer` (optional) | Synthetic policyholder age | Applicable for `INDIVIDUAL` (18-100) |
| `years_in_business`| `integer` (optional) | Commercial operational tenure | Applicable for `COMMERCIAL` (0-150) |
| `credit_score` | `integer` | Actuarial/FICO credit score | Range: `300` to `850` |
| `credit_tier` | `enum` | Categorical credit bracket | `"EXCELLENT"`, `"GOOD"`, `"FAIR"`, `"POOR"` |
| `geographic_risk_zone`| `string` | Hazard exposure micro-zone | e.g. `"TIER_1_COASTAL"`, `"TIER_2_INLAND"` |
| `annual_revenue_usd`| `float` (optional) | Commercial top-line revenue | In USD |

### 2.3 `policy_request`
| Field | Type | Description | Constraints |
| :--- | :--- | :--- | :--- |
| `line_of_business` | `enum` | Underwriting line | `"PROPERTY_HOMEOWNERS"`, `"COMMERCIAL_PROPERTY"`, `"COMMERCIAL_AUTO"`, `"CYBER_LIABILITY"` |
| `requested_limit_usd`| `float` | Requested policy limit | $\ge 1,000$ USD |
| `deductible_usd` | `float` | Proposed base deductible | $\ge 0$ USD |
| `asset_age_years` | `integer` | Age of insured structure/vehicle | $\ge 0$ |
| `asset_category_or_construction`| `string`| Construction or vehicle class | e.g. `"Masonry Non-Combustible"` |
| `protection_class_or_security`| `string`| Fire/security protection level| ISO Class 1-10 or security specification |

### 2.4 `claim_history`
| Field | Type | Description | Constraints |
| :--- | :--- | :--- | :--- |
| `years_of_history` | `integer` | Experience review window | Default: `5` years |
| `total_claims_count` | `integer` | Aggregate claim count | $\ge 0$ |
| `total_payout_amount_usd`| `float` | Aggregate incurred losses | Paid + reserved in USD |
| `open_claims_count` | `integer` | Pending unsettled claims | $\ge 0$ |
| `incidents` | `array[object]`| Detailed incident loss runs | List of Incident objects |

#### Incident Object Fields:
* `year` (`integer`): Calendar year of loss.
* `peril` (`string`): Cause of loss (e.g. `Water`, `Wind/Hail`, `Fire`, `Collision`, `Liability`, `Theft`).
* `payout_usd` (`float`): Incurred loss amount.
* `at_fault` (`boolean`): Whether policyholder was liable.
* `description` (`string`): Concise factual narrative of incident.

### 2.5 `external_risk_factors`
| Field | Type | Description | Constraints |
| :--- | :--- | :--- | :--- |
| `prior_carrier_cancellation` | `boolean` | Cancellation or non-renewal history | Flag for moral hazard |
| `gap_in_coverage_months` | `integer` | Lapse duration between policies | $\ge 0$ |
| `environmental_hazard_score` | `float` | Flood/wildfire/storm vulnerability | Range: `0.0` to `100.0` |
| `crime_hazard_score` | `float` | Regional theft/vandalism index | Range: `0.0` to `100.0` |
| `safety_compliance_certified`| `boolean` | Regulatory/safety audit status | True/False |
| `special_hazards` | `array[string]`| Identified operational perils | e.g. `["COASTAL_HURRICANE_ZONE"]` |

---

## 3. Derived Actuarial Normalization Formulas

During preprocessing, the system computes normalized metrics:

1. **Claim Frequency Annual:**
   $$\text{Claim Frequency} = \frac{\text{total\_claims\_count}}{\text{years\_of\_history}}$$

2. **Average Loss Severity:**
   $$\text{Average Severity} = \frac{\text{total\_payout\_amount\_usd}}{\max(1, \text{total\_claims\_count})}$$

3. **Loss-to-Limit Ratio:**
   $$\text{Loss-to-Limit (\%)} = \left(\frac{\text{total\_payout\_amount\_usd}}{\text{requested\_limit\_usd}}\right) \times 100$$

4. **Composite Hazard Index:**
   $$\text{Composite Hazard} = (0.6 \times \text{environmental\_hazard\_score}) + (0.4 \times \text{crime\_hazard\_score})$$

---

## 4. Synthesis Output Schema (`UnderwritingSynthesisReport`)

```json
{
  "customer_id": "SYNTH-8492-US",
  "line_of_business": "PROPERTY_HOMEOWNERS",
  "verdict": "APPROVE_WITH_CONDITIONS",
  "verdict_explanation": "Detailed actuarial justification...",
  "confidence_score_pct": 91.0,
  "risk_tier": "TIER_3_SUBSTANDARD",
  "executive_summary": "Concise natural language synthesis for underwriter...",
  "key_risk_indicators": [
    {
      "code": "KRI-PERIL-WATE",
      "title": "Recurrent Water Losses",
      "severity": "CRITICAL",
      "category": "CLAIM_FREQUENCY",
      "quantitative_finding": "2 claims totaling $56.4k in 3 years",
      "impact_analysis": "Systemic plumbing vulnerability...",
      "recommended_action": "Mandatory shut-off valve endorsement"
    }
  ],
  "loss_expectancy_insights": "Projected annual expected loss...",
  "recommended_conditions": ["Condition 1", "Condition 2"],
  "suggested_deductible_adjustment_usd": 2500.0,
  "actuarial_metrics": { ... },
  "processing_time_ms": 145.2,
  "ai_generation_engine": "OmniRisk Actuarial Heuristic NLG Engine"
}
```

---

## 5. Relational Excel Dataset Integration (`insurance_model.xlsx`)

OmniRisk natively ingests multi-table relational data from `insurance_model.xlsx` comprising 120 customers, 140 policies, 220 claims, 1,013 payments, products, and coverages.

### Cross-Table Mapping & Anonymization Engine (`backend/excel_loader.py`):
1. **PII Suppression:** `FirstName` and `LastName` from the `Customers` sheet are discarded. Policyholder age is computed dynamically from `DOB`, and locations are mapped to state/city risk zones.
2. **Loss Experience Consolidation:** Claims from the `Claims` sheet are aggregated per customer ID, capturing loss frequency, total dollar payout, open claims count, and specific incident perils.
3. **Moral Hazard Detection:** Policies with `Status == 'Lapsed'` are detected to flag coverage gaps and involuntary cancellations (`KRI-MORAL-01`).
4. **Standardization:** Relational rows are transformed into compliant `InputRiskPayload` instances and served via `GET /api/dataset/customer/{customer_id}`.
5. **Speed SLA Compliance:** End-to-end transformation and AI synthesis executes within **< 10 seconds** (typically 0.2s - 2.0s).

---

## 6. Verifiable Relational Proof Schema (`GET /api/dataset/customer/{customer_id}/proof`)

To guarantee zero hardcoded assumptions and verifiable lineage for all 120 customers, the API exposes the exact underlying records:

```json
{
  "customer_id": "CUST1082",
  "demographics_proof": {
    "customer_id": "CUST1082",
    "dob": "1984-07-15",
    "calculated_age": 42,
    "city": "Mumbai",
    "state": "WB",
    "pii_compliance": "First and last names scrubbed; identity anonymized per competition rules"
  },
  "policies": [
    {
      "policy_id": "POL3000",
      "product_id": "PR12",
      "product_name": "Motor Own Damage",
      "status": "Lapsed",
      "sum_insured_usd": 200000.0,
      "annual_premium_usd": 13331.0,
      "term_months": 36
    }
  ],
  "coverages": [
    { "policy_id": "POL3000", "coverage_id": "COV16", "coverage_name": "Theft", "coverage_sum": 10000.0 }
  ],
  "claims": [
    {
      "claim_id": "CL7204",
      "policy_id": "POL3000",
      "claim_amount_usd": 39318.61,
      "claim_status": "Open",
      "island_severity_class": "Medium (10k-50k)"
    }
  ],
  "payments": [
    { "payment_id": "PAY5000", "policy_id": "POL3000", "premium_amount_usd": 4443.67, "payment_method": "NetBanking" }
  ],
  "wide_summary": {
    "region": "North",
    "total_paid_to_date": 13331.01,
    "total_claims_amount": 89854.51,
    "num_claims": 2
  },
  "audit_trail": {
    "source_file": "insurance_model.xlsx",
    "verifiable": true
  }
}
```

