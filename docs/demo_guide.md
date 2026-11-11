# OmniRisk 3-Minute Demo Walkthrough & Presentation Script

This guide provides a structured presentation script for pitching **OmniRisk: The Automated Risk Profile Summarizer** during evaluation, directly addressing each rubric criteria.

---

## 🏆 Evaluation Rubric Alignment (100 Points)

| Rubric Dimension | Max Pts | OmniRisk Demonstration Focus |
| :--- | :---: | :--- |
| **Relevance** | 30 | Directly solves underwriter data fragmentation; 100% PII-free synthetic & Excel dataset ingestion. |
| **Innovation & Creativity** | 15 | Prominent KRI severity breakdown, What-If Sensitivity Sandbox, 3-tab Ingestion Cockpit (Form, JSON, Upload), and Portfolio Batch Analysis. |
| **Feasibility & Scalability** | 15 | Asynchronous FastAPI architecture, sub-second to <7s execution (<20s SLA), dual-engine fallback (Gemini LLM + Heuristic NLG). |
| **Use of AI/GenAI/ML** | 20 | Few-Shot CoT prompting, actuarial ratio normalization, automated ground-truth benchmark (89%+ composite accuracy). |
| **Presentation Quality** | 20 | Sleek modern InsurTech cockpit, 1-click scenario loading, live visual feedback, and verifiable relational proof. |

---

## ⏱️ 3-Minute Live Demo Script

### Minute 0:00 - 0:45: The Problem & Solution Overview
* **Speaker:** *"Good morning, respected judges. In insurance underwriting, evaluating a new commercial or personal risk requires cross-referencing dozens of fragmented records—loss runs, credit scores, catastrophe hazard indices, and prior carrier cancellations. Underwriters spend up to 60% of their day manually stitching this fragmented data together.*
* *Today, we present **OmniRisk: The Automated Risk Profile Summarizer**. OmniRisk ingests fragmented synthetic JSON payloads, normalizes actuarial metrics, enforces strict Zero-PII guardrails, and uses a specialized GenAI underwriter agent to generate an executive briefing highlighting **Key Risk Indicators (KRIs)** in seconds."*

---

### Minute 0:45 - 1:30: Multi-Channel Ingestion & Interactive Form
* **Speaker:** *"OmniRisk provides 3 flexible ingestion modes in the cockpit:*
  1. **📋 Interactive User Form:** Allows underwriters to type or adjust policyholder parameters directly (demographics, credit score, deductibles, historical claims, and peril chips).
  2. **💻 Raw JSON Editor:** Real-time two-way sync with the form.
  3. **📁 Drag & Drop File Upload:** Instant ingestion of structured JSON files.
* **Action:** Adjust the Credit Score slider to 550 and check *Prior Carrier Cancellation*.
* **Action:** Click **"⚡ Synthesize Risk Profile & KRIs"**.
* *Speaker:* *"Notice the instant synthesis. In seconds, the GenAI agent derives claim frequency and loss ratios, isolates 5 critical KRIs, and issues an authoritative **REFER TO SENIOR UNDERWRITER** verdict."*

---

### Minute 1:30 - 2:15: Relational Excel Dataset Explorer (`insurance_model.xlsx`)
* **Action:** Look at the top **Excel Dataset Explorer** card.
* *Speaker:* *"Beyond synthetic presets, OmniRisk integrates directly with `insurance_model.xlsx`—a multi-table relational dataset containing 120 customers, 140 policies, 220 claims, and 209 coverages.*
* *Underwriters can filter by High Loss (≥2 Claims), Lapsed Policies, or Clean Preferred.*
* **Action:** Select customer **CUST1050 (9 Claims, $660k Losses)** and click **"⚡ Load & Synthesize"**.
* *Speaker:* *"OmniRisk automatically strips all PII (names and personal identifiers), aggregates 9 distinct historical claims, and prompts Gemini to formulate mandatory risk mitigation conditions before binding."*

---

### Minute 2:15 - 2:45: Innovation Sandbox & Portfolio Batch
* **Action:** Scroll down to the **Underwriter "What-If" Sensitivity Sandbox**.
  * Increase the Deductible to $10,000 and lower the Environmental Hazard slider. Click **"Apply Simulated Parameters & Re-Evaluate"**.
  * *Speaker:* *"Underwriters frequently negotiate mitigations with brokers. Our What-If Sandbox lets underwriters simulate rate and deductible changes dynamically."*
* **Action:** Click the top header button **"📈 Portfolio Batch"**.
  * *Speaker:* *"Underwriting leads can also evaluate the top 25 accounts across the entire book in one batch, receiving an instant verdict distribution and risk breakdown."*

---

### Minute 2:45 - 3:00: SLA Verification & Technical Metrics
* **Action:** Click **"📊 Accuracy Benchmark"**.
* *Speaker:* *"Our solution meets and exceeds the challenge constraints:
  1. **Speed SLA:** Latency is **sub-second to ~6s**, well below the 20-second constraint.
  2. **Accuracy SLA:** As shown in our automated evaluation suite, our extraction accuracy is **89.0% - 92.8%**, surpassing the 85% requirement.
  3. **Privacy Compliance:** Ingests purely synthetic data with active PII rejection regex.
  4. **Dual Engine Reliability:** If the cloud LLM experiences network demand spikes, our deterministic Actuarial Heuristic NLG Engine guarantees zero downtime.*
* *Thank you. We are ready for your questions!"*
