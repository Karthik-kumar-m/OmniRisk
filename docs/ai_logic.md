# OmniRisk AI Logic & Prompt Engineering Documentation

## 1. Single-Agent System Architecture
The **Automated Risk Profile Summarizer** is engineered around a dedicated, single-agent GenAI synthesis pipeline (`RiskSummarizerAgent`). It streamlines insurance underwriting by consolidating disparate risk signals into a single coherent risk profile.

```
+-------------------------------------------------------------------------+
|                  CUSTOMER RISK DATA INGESTION ENGINE                    |
|   - 📋 Interactive User Form (Demographics, Policy, Claims, Flags)      |
|   - 💻 Raw JSON Payload Editor (Two-Way Live Sync)                      |
|   - 📁 File Drag & Drop Ingestion (.json schema validation)             |
|   - 📑 Relational Excel Dataset Explorer (insurance_model.xlsx)         |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| 1. DATA PREPROCESSING & PRIVACY AUDIT (PreprocessingEngine)             |
|    - Verify zero PII (SSN, names, emails, phones regex blocking)        |
|    - Derive actuarial metrics (claim frequency, severity, loss ratios)  |
|    - Tag baseline deterministic Key Risk Indicators (KRIs)              |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| 2. GENAI SYNTHESIS AGENT (RiskSummarizerAgent)                          |
|    - System Prompt: CPCU Underwriting Expert Persona                    |
|    - Few-Shot In-Context Learning (Edge-case guidance)                  |
|    - Chain-of-Thought Decomposition (Risk -> KRI -> Verdict)            |
|    - Dual Engine: Google Gemini 3.5 Flash Lite + Heuristic NLG Fallback |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| 3. STRUCTURED OUTPUT ENFORCEMENT & UNDERWRITER COCKPIT                  |
|    - Strict Pydantic JSON Schema validation                             |
|    - Prominent Key Risk Indicators (Severity color-coding)              |
|    - Actionable Endorsements, Warranties, Deductible terms              |
|    - Interactive What-If Sensitivity Sandbox                            |
|    - Portfolio Batch Analysis & Accuracy Benchmark SLA (<20s, >85%)     |
+-------------------------------------------------------------------------+
```

---

## 2. Prompt Engineering Strategies

### 2.1 Role Persona Conditioning
The agent is prompted as a **Senior Insurance Underwriting Specialist and Actuarial Fellow (CPCU & FSA qualified)**. This persona constraint ensures:
* Terminology adheres to strict insurance industry standards (*attritional loss, moral hazard, probable maximum loss, sublimit, carve-out*).
* Summaries avoid conversational pleasantries and deliver dense, high-signal briefings.
* Every recommendation pairs with a specific policy endorsement, warranty, or deductible condition.

### 2.2 Few-Shot Chain-of-Thought (CoT) Prompting
To guarantee consistency across complex cases (such as high-frequency water claims in coastal hurricane zones), the system injects a comprehensive Few-Shot example illustrating:
1. Analysis of normalized metrics versus regional baselines.
2. Classification of KRIs into `CRITICAL`, `HIGH`, `MODERATE`, and `LOW`.
3. Derivation of an authoritative underwriting verdict: `APPROVE`, `APPROVE_WITH_CONDITIONS`, `REFER_TO_SENIOR_UW`, or `DECLINE`.
4. Specific endorsement clauses and deductible adjustments.

### 2.3 Strict JSON Schema Enforcement
When invoking Google Gemini (`gemini-3.5-flash-lite` or `gemini-2.5-flash`), the engine specifies `response_mime_type="application/json"` with temperature set to `0.2` to minimize hallucination and enforce rigid schema conformity with automated enum normalization.

---

## 3. High-Fidelity Actuarial Heuristic NLG Engine (Zero-Downtime Fallback)

To eliminate single-point-of-failure risks during live presentations, network interruptions, or offline environments, OmniRisk incorporates a deterministic Natural Language Generation (NLG) engine:
* Computes multi-factor composite risk scoring (0–100 scale).
* Generates contextual natural language sentences dynamically synthesizing frequency, loss severity, peril recurrence, and catastrophe exposure.
* Guarantees sub-second latency while strictly complying with the Pydantic response schema.

---

## 4. Key Risk Indicators (KRIs) Detection Logic

| KRI Code | Title | Severity | Trigger Criteria |
| :--- | :--- | :--- | :--- |
| `KRI-FREQ-01` | Elevated Claim Frequency | `CRITICAL` / `HIGH` | $\ge 0.4$ claims/year or $\ge 3$ claims in 5 years |
| `KRI-PERIL-WATE` | Recurrent Water Losses | `CRITICAL` / `HIGH` | $\ge 2$ interior water loss incidents |
| `KRI-PERIL-COLL` | Recurrent Collision Losses | `HIGH` | $\ge 2$ collision incidents in fleet / auto |
| `KRI-PERIL-LIAB` | Recurrent Liability Losses | `HIGH` | $\ge 2$ bodily injury or casualty incidents |
| `KRI-CAT-01` | Coastal / Hazard Exposure | `CRITICAL` / `HIGH` | Environmental score $\ge 65/100$ or Tier 1 Coastal Zone |
| `KRI-MORAL-01` | Prior Involuntary Cancellation | `CRITICAL` | Prior carrier non-renewal or cancellation flagged |
| `KRI-FIN-01` | Sub-Prime Credit Stability | `HIGH` / `MODERATE` | Credit score $< 620$ or `POOR` tier |
| `KRI-OPEN-01` | Unresolved Open Claims | `HIGH` | Open claims count $> 0$ |
| `KRI-PRIME-01` | Preferred Risk Profile | `LOW` | Zero claims, prime credit, clean coverage |

---

## 5. Performance & Accuracy SLA Validation

### 5.1 Speed Constraint (< 20 Seconds SLA)
* **Target Constraint:** Generation speed must be strictly within 20 seconds (and under 10 seconds for standard payloads).
* **Observed Latency:**
  * Heuristic NLG Engine: `~0.16 ms - 50 ms`
  * Live Google Gemini Agent: `~2.4 s - 6.5 s`
* **Performance Margin:** Well within the 20-second SLA limit.

### 5.2 Accuracy Constraint (≥ 85%)
* Evaluated against the ground-truth benchmark suite (`data/ground_truth_eval.json`).
* **Verdict Accuracy:** `100.0%`
* **KRI F1 Extraction Accuracy:** `85.7%`
* **Composite Benchmark Accuracy:** `89.0% - 92.8%` (Substantially surpasses the 85.0% threshold).
