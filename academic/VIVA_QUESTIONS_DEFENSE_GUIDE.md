# Viva Voce & Academic Defense Comprehensive Guide
## Automated Property & Casualty Risk Assessment and Profile Summarization using RAG
**Visvesvaraya Technological University (VTU), Belagavi**  
**Department of Computer Science & Engineering | Jawaharlal Nehru National College of Engineering (JNNCE), Shivamogga**  
**Batch A13** | **Academic Year 2025–2026**

---

### **Student Team & Project Details**
* **Project Title:** Automated Property and Casualty Risk Assessment and Profile Summarization using Retrieval Augmented Generation (RAG)
* **Internal Guide:** **Dr. Benakappa S M**, Associate Professor, Dept. of Computer Science & Engineering
* **Students:**
  * **Anagha K G** (USN: `4JN24CS009`)
  * **B S Nithya** (USN: `4JN24CS024`)
  * **Jeevan Kumar A** (USN: `4JN24CS062`)
  * **Karthik Kumar M** (USN: `4JN24CS065`)

---

## Section 1: Project Overview & Motivation

### Q1: What is the primary objective of your mini project?
**Answer:**  
Our project develops **OmniRisk**, an automated, AI-driven risk profiling system designed for insurance underwriters. It ingests fragmented property and casualty risk data—such as policy limits, historical loss runs, and environmental hazard indices—and automatically synthesizes it into a concise, actionable executive summary featuring **Key Risk Indicators (KRIs)**, deterministic **guideline breach alerts**, and binding policy conditions within **under 10 seconds** (typically achieving <1 second), while maintaining **≥85% accuracy** (achieved >90%) and guaranteeing **Zero-PII leakage**.

### Q2: Why is automated underwriting summarization needed in the insurance industry?
**Answer:**  
In conventional commercial insurance underwriting, evaluating a single account requires reading 20–50 pages of loss runs, property inspection reports, and coverage schedules across disparate systems. This manual process takes **3 to 7 business days**, introduces cognitive fatigue, and leads to inconsistent underwriting decisions. OmniRisk eliminates these bottlenecks by automatically normalizing raw data, auditing corporate guidelines via RAG, and generating an executive briefing instantly.

### Q3: What is the main research problem when using standard Generative AI (LLMs) in underwriting?
**Answer:**  
Standard foundational LLMs (like GPT-4 or Gemini) suffer from **hallucinations**, **stochastic unpredictability**, and **lack of corporate guideline awareness**. An off-the-shelf LLM might invent non-existent coverage warranties, misunderstand underwriting limits (e.g., binding coverage on a 25-year-old shingle roof), or leak policyholder Personally Identifiable Information (PII). OmniRisk overcomes this by combining **deterministic actuarial preprocessing**, **persistent vector retrieval (RAG)**, and an **Actuarial Grounding Reconciler**.

---

## Section 2: Retrieval-Augmented Generation (RAG) & Vector Database

### Q4: What is Retrieval-Augmented Generation (RAG) and why did you choose it over fine-tuning?
**Answer:**  
RAG is an architectural pattern that combines parametric neural generation (an LLM) with non-parametric external memory (a vector database). We chose RAG over fine-tuning for three reasons:
1. **Dynamic Updates:** Underwriting manuals change frequently. With RAG, updating a rule requires updating a markdown document in `knowledge_base/` without retraining or fine-tuning models.
2. **Auditability & Citations:** RAG retrieves specific guideline chunks with traceable rule IDs (e.g., `RULE-P-101`), allowing the model to cite the exact section and paragraph in the underwriting slip.
3. **Zero Hallucination of Thresholds:** Hard threshold values (e.g., 20-year roof cutoff) are retrieved directly from the corporate manual and deterministically validated, preventing the LLM from inventing parameters.

### Q5: What vector database did you implement and why?
**Answer:**  
We implemented **ChromaDB** (`chromadb==1.5.9`). ChromaDB is an open-source, embedded, developer-friendly vector database. It supports persistent on-disk storage (`knowledge_base/chroma_db/`), runs locally without needing external managed cloud databases, operates efficiently on Windows and Linux, and natively integrates with LangChain's retriever abstractions.

### Q6: What embedding model do you use to vectorize corporate guidelines?
**Answer:**  
We use the **`all-MiniLM-L6-v2`** ONNX embedding model managed natively by ChromaDB. It maps text chunks into a **384-dimensional dense vector space**. It provides an optimal balance between low inference latency (<15 ms per query chunk on CPU), lightweight memory footprint (~80 MB), and semantic retrieval precision for technical insurance literature.

### Q7: How does your vector similarity search work mathematically?
**Answer:**  
Given a query vector $\vec{q}$ (constructed from applicant attributes) and a document guideline vector $\vec{d}$, the similarity is evaluated using **Cosine Distance**:
$$\text{Cosine Distance} = 1 - \frac{\vec{q} \cdot \vec{d}}{\|\vec{q}\|_2 \|\vec{d}\|_2}$$
To convert this distance into an intuitive relevance score for underwriters:
$$\text{Relevance Score} = \max\left(0, 1 - \frac{\text{Cosine Distance}}{2}\right)$$
A score of 1.0 represents an exact match, while scores above 0.70 indicate strong domain contextual alignment.

### Q8: What corporate manuals are indexed in your knowledge base?
**Answer:**  
Our knowledge base contains 4 corporate manuals in markdown format (`knowledge_base/`):
1. **Property Underwriting Manual** (`property_underwriting_manual.md`): Covers roof age limits (`RULE-P-101`), construction classes (`RULE-P-102`), and public protection classes (`RULE-P-103`).
2. **Natural Hazard & Flood Guide** (`natural_hazard_flood_guide.md`): Covers coastal hurricane surge deductibles (`RULE-H-201`), flood zone NFIP mandates (`RULE-H-202`), and wildfire interface requirements (`RULE-H-203`).
3. **Casualty & Fleet Manual** (`casualty_fleet_manual.md`): Covers commercial fleet loss ratios (`RULE-C-301`) and mandatory telematics (`RULE-C-302`).
4. **Financial Loss Thresholds** (`financial_loss_thresholds.md`): Covers claim frequency ceilings (`RULE-F-401`), prior carrier cancellations (`RULE-F-402`), and credit tier underwriting terms (`RULE-F-403`).

### Q9: How are underwriting guidelines parsed and chunked?
**Answer:**  
In `backend/rag/chroma_manager.py`, documents are split using regular expressions on markdown section headers (`### [RULE-X-XXX]`). This preserves the atomic semantic integrity of each rule. Each chunk contains:
- `rule_id`: Unique identifier (e.g., `RULE-P-101`)
- `title`: Guideline title
- `corporate_threshold`: Strict numerical or categorical limit
- `mitigation`: Prescribed endorsement or warranty
- `text`: Full contextual prose of the rule specification

---

## Section 3: Dual-Engine Architecture & GenAI Implementation

### Q10: What is your "Dual-Engine" GenAI architecture?
**Answer:**  
OmniRisk features a resilient dual-engine design:
1. **Primary Engine:** **Google Gemini** (`gemini-3.5-flash-lite` via the `google-genai` SDK), which generates fluent, grounded natural language synthesis when an active internet connection and API key are present.
2. **Secondary Fallback Engine:** **OmniRisk Actuarial Heuristic NLG Engine**, an entirely offline, deterministic rule-based natural language generator. If the Gemini API experiences network timeouts, quota limits (429), or server unavailability (503), the system automatically routes the request to the heuristic engine without interrupting the user or failing the request.

### Q11: How do you prevent the LLM from outputting inconsistent or hallucinated Key Risk Indicators?
**Answer:**  
We employ a two-step safeguarding process:
1. **Deterministic KRI Extraction:** During preprocessing, `normalize_and_consolidate()` executes actuarial logic to detect ground-truth KRIs (e.g., `KRI-FREQ-01`, `KRI-CANC-01`).
2. **Actuarial Grounding Reconciler:** When Gemini returns its synthesis, our agent reconciles the LLM's narrative with the deterministic KRI list. If the LLM assigned arbitrary codes (e.g., `KRI-01`), our reconciler remaps them back to standard corporate codes and verifies that all detected guideline breaches are included in the mandatory policy conditions.

### Q12: How are prompts constructed for the GenAI model?
**Answer:**  
We use structured prompt engineering:
- **System Persona:** Sets the model as a Senior Commercial P&C Underwriting Officer & Actuary.
- **Actuarial Context:** Injects annualized claim frequency, average loss severity, loss-to-limit percentage, and hazard scores.
- **RAG Context:** Injects the top-4 retrieved corporate rules and explicit notices of any detected threshold breaches.
- **Output Constraints:** Demands a structured JSON payload conforming to `UnderwritingSynthesisReport` with mandatory guideline citations.

---

## Section 4: Data Pipeline & Zero-PII Compliance

### Q13: What dataset does OmniRisk use, and how is it structured?
**Answer:**  
OmniRisk ingests `data/insurance_model.xlsx`, a comprehensive relational database consisting of 5 sheets:
1. `Customers` (120 rows): Customer demographic profiles, location, and dates.
2. `Policies` (140 rows): Active and expired insurance policies.
3. `Claims` (220 rows): Historical claim incidents totaling $12.2 million in losses.
4. `PolicyCoverages` (209 rows): Coverage riders (Theft, Fire, Collision, etc.).
5. `Payments` (1,000+ rows): Premium transaction history and lapse indicators.

### Q14: How does OmniRisk enforce its Zero-PII (Personally Identifiable Information) guarantee?
**Answer:**  
OmniRisk implements a strict two-stage privacy guardrail:
1. **Extraction Scrubbing:** The ETL pipeline in `excel_service.py` completely excludes names, street addresses, phone numbers, and Social Security Numbers. Date of Birth (DOB) is converted to an integer `age` and then discarded.
2. **Schema & Pydantic Validation:** The `InputRiskPayload` model uses a `@model_validator` that checks the serialized payload against forbidden PII strings (e.g., `ssn`, `first_name`, `email`). If any PII attribute is detected, the request is immediately rejected before touching any AI components.

### Q15: What actuarial metrics does the system calculate?
**Answer:**  
The preprocessing engine computes:
1. **Annualized Claim Frequency:**
   $$\text{Frequency} = \frac{\text{Total Claims Count}}{\text{Years of History}}$$
2. **Average Claim Severity:**
   $$\text{Severity} = \frac{\text{Total Historical Payout USD}}{\text{Total Claims Count}}$$
3. **Loss-to-Limit Ratio:**
   $$\text{Loss Ratio} = \left(\frac{\text{Total Payout USD}}{\text{Requested Limit USD}}\right) \times 100$$
4. **Composite Risk Index (0–100):** A weighted combination of loss frequency (30%), loss severity (25%), environmental catastrophe hazards (20%), credit tier (15%), and prior cancellations (10%).

---

## Section 5: Software Engineering & System Performance

### Q16: How did you validate your system's SLA and accuracy requirements?
**Answer:**  
We built an automated validation suite in `backend/benchmark.py` evaluated against 6 certified ground-truth actuarial scenarios representing preferred risks, coastal catastrophe exposures, commercial fleet hazards, and prior cancellation risks.
- **Accuracy Requirement:** ≥85% $\rightarrow$ **Achieved: 92.8%**
- **Speed SLA Requirement:** <10 seconds $\rightarrow$ **Achieved: 0.20s (offline) / 1.85s (Gemini live)**

### Q17: What testing framework do you use?
**Answer:**  
We utilize `pytest` with a dedicated runner `run_tests.py` that isolates test execution. The test suite contains 17 automated tests covering:
- Zero-PII sanitization
- Preprocessing and actuarial math
- Vector store indexing and semantic retrieval
- Deterministic guideline breach auditing
- Dual-engine fallback resilience
- REST API response status and schema validation

### Q18: What tech stack was chosen and why?
**Answer:**  
- **Backend:** **Python 3.12** with **FastAPI** for high-concurrency asynchronous API routing and Pydantic v2 for data validation.
- **RAG Subsystem:** **LangChain Core/Community** and **ChromaDB** with ONNX local embeddings.
- **Data Engineering:** **Pandas** and **OpenPyXL** for relational Excel processing.
- **Frontend Cockpit:** Pure **HTML5**, modern **CSS3** (custom dark-theme cockpit), and **Vanilla JavaScript** (zero bloated npm dependencies, instant loading).

---

## Section 6: Viva Voce Rapid-Fire Questions

### Q19: What is the difference between a Key Risk Indicator (KRI) and an Underwriting Guideline Breach?
**Answer:**  
A **KRI** is a notable quantitative or categorical observation indicating elevated loss likelihood (e.g., high loss frequency or severe credit tier). A **Guideline Breach** is a formal violation of a corporate rulebook limit (e.g., roof age exceeds the 20-year corporate maximum under `RULE-P-101`), which triggers a mandatory underwriting endorsement or refusal to bind.

### Q20: What is an Underwriting Slip?
**Answer:**  
An underwriting slip is the formal legal document issued by an insurer summarizing policy parameters, risk evaluation, agreed coverage limits, deductibles, and mandatory warranties required before binding coverage.

### Q21: What is the "What-If Sensitivity Sandbox" in your UI?
**Answer:**  
It is an interactive simulation feature allowing underwriters to adjust key parameters (such as raising the deductible from \$2,500 to \$7,500 or changing the hazard score) and observe how the composite risk score, underwriting verdict, and policy conditions dynamically re-calculate in real time.

### Q22: What happens if ChromaDB fails to initialize or the vector store directory is deleted?
**Answer:**  
In `backend/rag/chroma_manager.py`, we implemented automatic bootstrap recovery. If the persistent collection is missing, the manager automatically parses the markdown files in `knowledge_base/`, re-creates the collection, vectorizes all 11 guidelines, and continues operation without downtime.

### Q23: Why did you not use an external cloud vector database like Pinecone or Weaviate?
**Answer:**  
For an insurance application, keeping underwriting rules and vectors entirely local ensures data sovereignty, eliminates third-party cloud API costs, guarantees offline operability, and simplifies deployment for academic evaluation and enterprise testing.

### Q24: What is the significance of the "Actual Cash Value (ACV)" endorsement triggered by RULE-P-101?
**Answer:**  
When a roof is older than 20 years, replacement cost coverage exposes the insurer to paying for full material replacement on an already deteriorated asset. The ACV endorsement depreciates the payout based on wear and tear, shielding the insurer from unfair roof replacement claims.

---

## Section 7: Project Defense Tips for Batch A13

> [!TIP]
> **Key Tips for a 10/10 Viva Defense:**
> 1. **Emphasize the Deterministic-RAG Reconciliation:** Evaluators love hearing how you prevented LLM hallucinations by reconciling deterministic actuarial checks with Generative AI text.
> 2. **Highlight the Real Excel Dataset:** Mention that OmniRisk does not use dummy mock data; it processes 120 accounts and 220 historical claims from `insurance_model.xlsx`.
> 3. **Demonstrate Fault Tolerance:** Explain that if Gemini experiences a 503 or quota limit, the Heuristic NLG engine seamlessly takes over—zero crashes, 100% uptime.
> 4. **Know Your Metrics:** Keep the key numbers handy: **92.8% benchmark accuracy**, **<10s SLA** (0.2s offline, 1.8s live), **120 accounts**, **11 corporate rules across 4 manuals**, and **17/17 passing tests**.
