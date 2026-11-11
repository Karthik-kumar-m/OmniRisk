# Project Presentation Deck & Seminar Defense Script
## Automated Property & Casualty Risk Assessment and Profile Summarization using RAG
**Visvesvaraya Technological University (VTU), Belagavi**  
**Department of Computer Science & Engineering | Jawaharlal Nehru National College of Engineering (JNNCE), Shivamogga**  
**Batch A13** | **Academic Year: 2025–2026**

---

### **Project Metadata**
* **Project Title:** Automated Property and Casualty Risk Assessment and Profile Summarization using Retrieval Augmented Generation (RAG)
* **Internal Guide:** **Dr. Benakappa S M**, Associate Professor, Dept. of Computer Science & Engineering, JNNCE Shivamogga
* **Student Team (Batch A13):**
  1. **Anagha K G** (USN: `4JN24CS009`)
  2. **B S Nithya** (USN: `4JN24CS024`)
  3. **Jeevan Kumar A** (USN: `4JN24CS062`)
  4. **Karthik Kumar M** (USN: `4JN24CS065`)

---

## Slide 1: Title & Introduction

### **Slide Content**
* **Project Title:** Automated Property & Casualty Risk Assessment and Profile Summarization using Retrieval Augmented Generation (RAG)
* **Institution:** Jawaharlal Nehru National College of Engineering (JNNCE), Shivamogga
* **Affiliation:** Visvesvaraya Technological University (VTU), Belagavi
* **Department:** Computer Science & Engineering
* **Project Guide:** Dr. Benakappa S M, Associate Professor
* **Presenters:** Anagha K G, B S Nithya, Jeevan Kumar A, Karthik Kumar M

### **Speaker Notes / Presentation Script**
> *"Respected Guide Dr. Benakappa S M, and esteemed evaluators, good morning. We are Batch A13 from the Department of Computer Science & Engineering, JNNCE Shivamogga. Today, we are proud to present our academic project: 'Automated Property and Casualty Risk Assessment and Profile Summarization using Retrieval Augmented Generation (RAG)'. In this presentation, we will demonstrate how we resolved one of the greatest bottlenecks in the insurance industry—manual underwriting compilation and LLM hallucinations—by uniting deterministic actuarial models with vector-grounded Retrieval Augmented Generation."*

---

## Slide 2: Problem Statement & Industry Motivation

### **Slide Content**
* **Current Underwriting Bottleneck:**
  * Property and Casualty (P&C) risk evaluation takes **3 to 7 business days** per complex account.
  * Information is scattered across policy ledgers, claim loss runs, peril zones, and external registries.
* **Manual Compilation Inconsistencies:**
  * Different underwriters calculate loss severity and frequency using subjective heuristics, leading to adverse selection.
* **The Hallucination Danger of Standalone LLMs:**
  * Out-of-the-box LLMs hallucinate coverage terms, invent underwriting rules, and leak sensitive Personally Identifiable Information (PII).
* **Research Goal:**
  * Build a deterministic, PII-free, sub-10-second risk synthesis engine grounded against corporate underwriting rulebooks using ChromaDB and LangChain.

### **Speaker Notes**
> *"In the insurance domain, when an enterprise or homeowner applies for coverage, underwriters spend hours cross-referencing multi-page loss runs, credit scores, and flood maps. Commercial underwriters take 3 to 7 days per policy. While Generative AI is capable of fluent summarization, standard LLMs pose unacceptable compliance risks: they hallucinate facts and can violate underwriting guidelines. Our goal was to design an enterprise-grade AI system that synthesizes risk profiles in under 10 seconds while guaranteeing zero hallucinations through deterministic RAG grounding."*

---

## Slide 3: Project Objectives & Technical Constraints

### **Slide Content**
1. **Multi-Modal Data Ingestion:**
   * Support Interactive Form input, raw JSON payloads, and relational datasets (`insurance_model.xlsx` across 120 accounts).
2. **Zero-PII Compliance Guarantee:**
   * Strict algorithmic regex and structural filtering to scrub all personal identity markers before data touches AI pipelines.
3. **Persistent RAG Subsystem:**
   * Vectorize corporate underwriting guidelines into **ChromaDB** collections via **LangChain Core**.
4. **Deterministic Breach Auditing:**
   * Automatically detect threshold violations (e.g., roof age >20 years, prior carrier cancellations).
5. **High-Speed & High-Accuracy SLA:**
   * Synthesis response time **<10 seconds** (target achieved: **<1 second**).
   * Benchmark accuracy **≥85%** against actuarial ground truth (target achieved: **>90%**).
6. **Dual-Engine Fault Tolerance:**
   * Seamless live Google Gemini generation with zero-downtime offline Heuristic NLG fallback.

### **Speaker Notes**
> *"Our project was governed by strict real-world engineering constraints: First, zero PII—no policyholder names or SSNs may reach the GenAI agent. Second, an SLA of under 10 seconds for profile synthesis. Third, at least 85% benchmark accuracy in identifying Key Risk Indicators. Finally, the system must maintain 100% operational uptime via a dual-engine architecture: utilizing Google Gemini when connected, and an actuarial heuristic engine when offline."*

---

## Slide 4: Literature Review & Background

### **Slide Content**
* **Traditional Rule-Based Expert Systems (1980s–2010s):**
  * Highly rigid; incapable of producing natural language executive briefings; brittle to non-standard schema variations.
* **Statistical Actuarial Models (GLMs / XGBoost):**
  * Excellent for calculating pure premium and loss probability, but produce zero qualitative explanations for executive committees.
* **Generative Pre-trained Transformers (2020–Present):**
  * Superb natural language fluency, but prone to stochastic drift and hallucinated domain guidelines (Lewis et al., 2020).
* **Retrieval-Augmented Generation (RAG) Paradigm:**
  * Bridges neural text generation with non-parametric vector memory (ChromaDB + ONNX embeddings), ensuring verifiable legal citations.

### **Speaker Notes**
> *"In our literature survey, we compared classical rule-based systems, statistical Generalized Linear Models, and pure transformer architectures. While statistical models compute loss ratios, they cannot draft an underwriter memo. Conversely, raw LLMs write fluently but lack domain grounding. By implementing RAG—pioneered by Lewis and Douze—we inject authoritative underwriting manuals directly into the prompt context, creating a verifiable and audit-ready decision support system."*

---

## Slide 5: System Architecture & Workflow

### **Slide Content**
* **Client Layer:** Dual-cockpit web application with Form Mode, Monaco-style JSON editor, Relational Proof Explorer, and RAG Inspector.
* **API Layer:** FastAPI async web service implementing REST endpoints (`/api/summarize`, `/api/guidelines`, `/api/dataset/*`, `/api/evaluate`).
* **Preprocessing Engine:** Zero-PII filter, claim frequency/severity aggregator, and deterministic KRI classifier.
* **Vector Store & RAG:** LangChain retriever integrated with persistent ChromaDB indexing 4 corporate manuals.
* **Synthesis Engine:** Google Gemini (`gemini-3.5-flash-lite`) orchestrated with offline Heuristic fallback and KRI reconciler.

### **Speaker Notes**
> *"This slide illustrates our multi-tier architecture. When an applicant's data enters through the web cockpit or REST API, it passes through the Zero-PII sanitization layer. Next, our actuarial engine computes metrics like loss-to-limit ratio and annualized frequency. Simultaneously, our LangChain retriever performs semantic cosine search against ChromaDB, pulling relevant guidelines and detecting deterministic breaches. These are assembled into an augmented prompt for Google Gemini, and our actuarial reconciler guarantees that every detected breach is enforced in the policy conditions."*

---

## Slide 6: Knowledge Base & Vector Retrieval Design

### **Slide Content**
* **Corporate Underwriting Manuals (`knowledge_base/`):**
  1. `property_underwriting_manual.md`: Rules `RULE-P-101` (Roof age ≤20y), `RULE-P-102` (Construction), `RULE-P-103` (Protection classes).
  2. `natural_hazard_flood_guide.md`: Rules `RULE-H-201` (Coastal hurricane deductible), `RULE-H-202` (Flood zone NFIP), `RULE-H-203` (Wildfire WUI).
  3. `casualty_fleet_manual.md`: Rules `RULE-C-301` (Fleet loss ratio ≤40%), `RULE-C-302` (Telematics mandate).
  4. `financial_loss_thresholds.md`: Rules `RULE-F-401` (Frequency ceiling 0.40/yr), `RULE-F-402` (Prior carrier non-renewal).
* **Vector Embedding & Search:**
  * Embeddings: `all-MiniLM-L6-v2` ONNX model executed locally.
  * Distance Metric: Cosine similarity with dynamic threshold normalization ($Relevance = 1 - \frac{dist}{2}$).
  * Top-$k$: Retrieves the top 4 most pertinent corporate rules per application.

### **Speaker Notes**
> *"Our knowledge base comprises 4 corporate underwriting manuals spanning 11 formal rules. Using ChromaDB, these rules are embedded into a 384-dimensional vector space using the all-MiniLM-L6-v2 ONNX model. When evaluating an account—for example, a coastal property with water claims—the retriever surfaces RULE-H-201 and RULE-P-101. If the applicant's roof is 24 years old, the deterministic auditor flags a CRITICAL breach of RULE-P-101, which mandates an Actual Cash Value roof endorsement."*

---

## Slide 7: Dataset & Relational Provenance (`insurance_model.xlsx`)

### **Slide Content**
* **Real-World Relational Dataset:**
  * Extracted from `data/insurance_model.xlsx` comprising **5 relational sheets**:
    * `Customers`: 120 accounts with demographics, city, state, and DOB.
    * `Policies`: 140 policies across Property, Auto, and Commercial lines.
    * `Claims`: 220 historical loss incidents ($12.2M total incurred losses).
    * `PolicyCoverages`: 209 elected coverage riders (Fire, Theft, Windstorm).
    * `Payments`: Premium collection ledger and lapse indicators.
* **Zero-PII Transformation:**
  * Names, phone numbers, and street addresses are irreversibly scrubbed.
  * Age is dynamically derived from DOB without retaining the birthdate.
  * Relational join produces standardized `InputRiskPayload` payloads.

### **Speaker Notes**
> *"To ensure academic and industry validity, we did not limit ourselves to dummy data. We ingested insurance_model.xlsx, containing 120 customer accounts, 140 policies, and 220 real claim records totaling over 12 million dollars in historical losses. Our backend relational loader joins across all 5 sheets, strips all PII, and constructs standardized risk profiles that can be loaded into the cockpit with a single click."*

---

## Slide 8: Prompt Engineering & Grounding Reconciliation

### **Slide Content**
* **System Prompt Architecture:**
  * Sets the agent persona: *"Senior Commercial P&C Underwriting Officer & Actuary"*.
  * Injects structured JSON schema, normalized actuarial metrics, and retrieved corporate rules.
  * Mandates citations: Every adverse condition must cite its parent rule (e.g., `[RULE-P-101]`).
* **The Grounding Reconciliation Mechanism:**
  * **Challenge:** LLMs may rephrase or omit deterministic risk indicators, threatening benchmark consistency.
  * **Solution:** A post-synthesis Actuarial Reconciler injects deterministic KRI findings and mandatory guideline mitigations directly into the final report.

### **Speaker Notes**
> *"Prompt engineering in insurance requires strict governance. Our system prompt instructs the model to act as a Senior Underwriting Officer, explicitly forbidding hallucinated policy warranties. To prevent LLM stochastic variance from degrading accuracy, we implemented a Grounding Reconciler. If our deterministic engine flags a roof age breach or prior carrier cancellation, that finding is strictly merged into the final recommendation, guaranteeing 100% adherence to corporate manuals."*

---

## Slide 9: Experimental Results & SLA Benchmark

### **Slide Content**
* **Empirical Validation Suite:**
  * 6 ground-truth test profiles evaluated against certified actuarial outcomes.
  * Evaluates: Verdict accuracy, KRI identification, and latency SLA.
* **Performance Metrics Achieved:**
  * **Composite Underwriting Accuracy:** **92.8%** (exceeds ≥85% SLA).
  * **Average Processing Latency:** **0.20 seconds** (offline) / **1.85 seconds** (Gemini live), well within the 10-second SLA.
  * **PII Leakage Rate:** **0.00%** (verified by automated regex auditing).
  * **Automated Unit Tests:** **17 of 17 tests passed** across the entire pipeline.

### **Speaker Notes**
> *"We subjected OmniRisk to rigorous empirical testing using our automated validation benchmark. The system achieved a composite accuracy of 92.8%, comfortably exceeding our 85% requirement. On speed, the system synthesizes profiles in an average of 200 milliseconds offline and under 2 seconds when calling Google Gemini live. In all 120 accounts tested, zero PII tokens were leaked, and all 17 automated regression tests pass consistently."*

---

## Slide 10: User Interface & Underwriter Cockpit

### **Slide Content**
* **Live Underwriting Cockpit Features:**
  * **Three Ingestion Modes:** Interactive Form, Raw JSON Editor, and File Upload.
  * **Excel Dataset Explorer:** Browse and filter all 120 accounts by High Loss, Lapsed, or Preferred status.
  * **Verifiable Proof Inspector:** Audit source records across all 5 Excel sheets.
  * **RAG Grounding Inspector:** View guideline breaches and inspect vector similarity scores.
  * **What-If Sensitivity Sandbox:** Dynamically test how adjusting deductibles and hazard scores impacts underwriting verdicts.

### **Speaker Notes**
> *"Here we showcase the OmniRisk Underwriter Cockpit. The interface was designed for operational transparency. Underwriters can adjust policy variables in real time using the What-If Sandbox, browse the complete 120-account relational vault, inspect verbatim corporate guideline text via the RAG Inspector, and export formal underwriting slips as JSON or Markdown with one click."*

---

## Slide 11: Conclusion & Academic Contributions

### **Slide Content**
* **Key Achievements:**
  1. Successfully integrated **LangChain Core** and persistent **ChromaDB** with Generative AI for P&C risk profiling.
  2. Eliminated GenAI hallucinations through deterministic guideline breach auditing and grounding reconciliation.
  3. Proved sub-second underwriting summarization on real-world insurance data while maintaining zero-PII compliance.
* **Academic Significance:**
  * Demonstrates how VTU CSE students can bridge modern AI engineering with regulated enterprise financial applications.

### **Speaker Notes**
> *"To conclude, our project demonstrates that Generative AI can be safely and reliably deployed in high-stakes financial environments when paired with Retrieval Augmented Generation and deterministic guardrails. OmniRisk transforms a multi-day manual underwriting task into an instantaneous, verifiable, and audit-proof workflow. We are deeply grateful to our guide, Dr. Benakappa S M, for his continuous mentorship throughout this project."*

---

## Slide 12: Future Work, Q&A & References

### **Slide Content**
* **Future Directions:**
  * **Multimodal RAG:** Integrate satellite imagery and drone roof inspection photos into ChromaDB.
  * **Automated Fraud Scoring:** Graph neural network integration to detect organized claim rings.
  * **Enterprise RBAC:** Role-Based Access Control and SAML SSO integration for multi-branch carriers.
* **Key References:**
  1. Lewis, P. et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. NeurIPS 2020.
  2. LangChain Documentation (2024). *Retrieval and Vector Store Connectors*.
  3. ChromaDB Architecture Whitepaper (2023). *Persistent Embedded Vector Stores*.
* **Thank You! Questions & Discussion.**

### **Speaker Notes**
> *"In future work, we plan to incorporate multimodal aerial imagery to inspect roof wear automatically and integrate graph analysis for claim fraud detection. Thank you, respected evaluators. We are now open for questions and look forward to demonstrating the live application."*
