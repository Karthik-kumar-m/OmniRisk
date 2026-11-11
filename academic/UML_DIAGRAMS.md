# OmniRisk System Architecture & UML Design Specifications
## Automated Property & Casualty Risk Assessment and Profile Summarization using RAG
**Visvesvaraya Technological University (VTU), Belagavi**  
**Department of Computer Science & Engineering | JNNCE Shivamogga**  
**Batch A13** | **Academic Year 2025–2026**

---

## 1. System Context & Architecture Overview

The OmniRisk system architecture integrates structured risk ingestion, deterministic actuarial preprocessing, persistent vector retrieval via LangChain and ChromaDB, and a resilient dual-engine Large Language Model (Google Gemini with Heuristic NLG fallback).

```mermaid
flowchart TD
    subgraph ClientLayer ["Client & Cockpit Presentation Layer"]
        UI["Dual-Cockpit Underwriter UI<br/>(HTML5 / CSS3 / Vanilla JS)"]
        FormMode["Interactive Form Ingestion"]
        JsonMode["Raw JSON Editor"]
        ExcelVault["120-Account Relational Vault"]
        RAGInspect["RAG Grounding & Breach Inspector"]
    end

    subgraph APILayer ["FastAPI Gateway & Routing Layer"]
        API["FastAPI High-Performance Engine"]
        EndpointSummarize["/api/summarize"]
        EndpointGuidelines["/api/guidelines & /api/guidelines/{id}"]
        EndpointDataset["/api/dataset/*"]
        EndpointBench["/api/evaluate"]
    end

    subgraph PreprocessLayer ["Actuarial Preprocessing & Guardrails"]
        PIIGuard["Zero-PII Compliance Validator"]
        ActuarialEngine["Actuarial Aggregation Engine<br/>(Frequency, Severity, Loss Ratio)"]
        KRIDetector["Deterministic KRI Classifier<br/>(Ground-Truth Engine)"]
    end

    subgraph RAGLayer ["LangChain & ChromaDB RAG Subsystem"]
        ChromaStore[("Persistent ChromaDB<br/>(Vector Store)")]
        LCRetriever["LangChain Semantic Retriever<br/>(k=4 Semantic Nearest Neighbor)"]
        RuleAuditor["Deterministic Guideline Auditor<br/>(Threshold Breach Detector)"]
        KnowledgeManuals["Corporate Manuals (.md)<br/>- Property Underwriting<br/>- Hazard & Flood<br/>- Casualty & Fleet<br/>- Financial Loss Limits"]
    end

    subgraph SynthesisLayer ["Dual-Engine GenAI Synthesis"]
        DualRouter{"API Key Active &<br/>Gemini Available?"}
        GeminiLLM["Google Gemini GenAI<br/>(gemini-3.5-flash-lite)"]
        HeuristicNLG["Actuarial Heuristic NLG Engine<br/>(100% Offline Resilience)"]
        GroundingReconciler["KRI & Grounding Reconciler<br/>(Injects Breaches & Mitigations)"]
    end

    UI --> API
    API --> EndpointSummarize
    EndpointSummarize --> PIIGuard
    PIIGuard --> ActuarialEngine
    ActuarialEngine --> KRIDetector

    KRIDetector --> LCRetriever
    KnowledgeManuals --> ChromaStore
    ChromaStore <--> LCRetriever
    LCRetriever --> RuleAuditor

    RuleAuditor --> DualRouter
    DualRouter -- "Yes" --> GeminiLLM
    DualRouter -- "Fallback / No Key" --> HeuristicNLG
    GeminiLLM --> GroundingReconciler
    HeuristicNLG --> GroundingReconciler

    GroundingReconciler --> API
    API --> RAGInspect
    API --> UI
```

---

## 2. Use Case Diagram

The Use Case model defines the functional interactions between the Underwriter / Actuarial Auditor (Primary Actor), the Corporate Risk Management System, and the OmniRisk Automated Summarizer.

```mermaid
flowchart LR
    Underwriter((Insurance Underwriter))
    AdminAuditor((Risk Auditor / Actuary))

    subgraph OmniRiskSystem ["OmniRisk Boundary"]
        UC1(["UC-01: Ingest Structured Risk Payload (Form/JSON/File)"])
        UC2(["UC-02: Sanitize & Scrub PII"])
        UC3(["UC-03: Compute Actuarial Metrics (Freq, Severity, Loss Ratio)"])
        UC4(["UC-04: Query Corporate Underwriting Guidelines (RAG)"])
        UC5(["UC-05: Audit Hard Guideline Threshold Breaches"])
        UC6(["UC-06: Synthesize Natural Language Executive Summary"])
        UC7(["UC-07: Extract Key Risk Indicators (KRIs)"])
        UC8(["UC-08: Formulate Binding Verdict & Policy Conditions"])
        UC9(["UC-09: Run Underwriter What-If Sensitivity Sandbox"])
        UC10(["UC-10: Browse Relational Excel Provenance (120 Accounts)"])
        UC11(["UC-11: Validate System Accuracy Benchmark (≥85% SLA)"])
        UC12(["UC-12: Export Formal Underwriting Slip (JSON/Markdown)"])
    end

    Underwriter --> UC1
    Underwriter --> UC6
    Underwriter --> UC7
    Underwriter --> UC8
    Underwriter --> UC9
    Underwriter --> UC10
    Underwriter --> UC12

    AdminAuditor --> UC4
    AdminAuditor --> UC5
    AdminAuditor --> UC11
    AdminAuditor --> UC10

    UC1 -.->|include| UC2
    UC1 -.->|include| UC3
    UC6 -.->|include| UC4
    UC6 -.->|include| UC5
    UC6 -.->|include| UC7
    UC8 -.->|include| UC5
```

---

## 3. Class Diagram

The Class Diagram highlights the domain entities, Pydantic data schemas, RAG vector database management classes, and the GenAI synthesis engine.

```mermaid
classDiagram
    class CustomerDemographics {
        +Optional[int] age
        +Optional[int] years_in_business
        +int credit_score
        +str credit_tier
        +str geographic_risk_zone
        +Optional[float] annual_revenue_usd
    }

    class PolicyRequest {
        +str line_of_business
        +float requested_limit_usd
        +float deductible_usd
        +int asset_age_years
        +str asset_category_or_construction
        +str protection_class_or_security
    }

    class ClaimIncident {
        +int year
        +str peril
        +float payout_usd
        +bool at_fault
        +str description
    }

    class ClaimHistory {
        +int years_of_history
        +int total_claims_count
        +float total_payout_amount_usd
        +int open_claims_count
        +List~ClaimIncident~ incidents
    }

    class ExternalRiskFactors {
        +bool prior_carrier_cancellation
        +int gap_in_coverage_months
        +float environmental_hazard_score
        +List~str~ special_hazard_designations
    }

    class InputRiskPayload {
        +str customer_id
        +str entity_type
        +CustomerDemographics demographics
        +PolicyRequest policy_request
        +ClaimHistory claim_history
        +ExternalRiskFactors external_risk_factors
        +verify_no_pii_strings()
    }

    class KeyRiskIndicator {
        +str code
        +str title
        +str severity
        +str category
        +str quantitative_finding
        +str impact_analysis
        +str recommended_action
    }

    class GuidelineBreach {
        +str rule_id
        +str title
        +str manual_source
        +str corporate_threshold
        +str applicant_observed
        +str severity
        +str actionable_mitigation
    }

    class RetrievedGuideline {
        +str rule_id
        +str manual
        +str title
        +str excerpt
        +float relevance_score
    }

    class UnderwritingSynthesisReport {
        +str customer_id
        +str line_of_business
        +str risk_tier
        +str verdict
        +str verdict_explanation
        +int confidence_score_pct
        +str executive_summary
        +List~KeyRiskIndicator~ key_risk_indicators
        +Dict actuarial_metrics
        +List~str~ recommended_conditions
        +Optional[float] suggested_deductible_adjustment_usd
        +int processing_time_ms
        +str engine_used
        +List~GuidelineBreach~ guideline_breaches
        +List~RetrievedGuideline~ retrieved_guidelines
        +bool rag_grounding_verified
    }

    class ChromaGuidelineManager {
        -Path knowledge_base_dir
        -Path persist_dir
        -Client chroma_client
        -Collection collection
        -List guidelines_cache
        +initialize_knowledge_base()
        +get_all_guidelines() List
        +query_guidelines(query_text, top_k) List
    }

    class LangChainGuidelineRetriever {
        -ChromaGuidelineManager chroma_manager
        +retrieve_relevant_guidelines(payload, top_k) List~RetrievedGuideline~
        +audit_guideline_breaches(payload) List~GuidelineBreach~
    }

    class LangChainRAGAgent {
        -LangChainGuidelineRetriever retriever
        +synthesize_rag_context(payload) Dict
        +format_guidelines_for_prompt(retrieved, breaches) str
    }

    class OmniRiskSummarizerAgent {
        -ChromaGuidelineManager chroma_manager
        -LangChainRAGAgent rag_agent
        +summarize_risk_profile(payload) UnderwritingSynthesisReport
        -_call_gemini_with_rag(payload, normalized, rag_context) UnderwritingSynthesisReport
        -_heuristic_synthesis_with_rag(payload, normalized, rag_context) UnderwritingSynthesisReport
    }

    InputRiskPayload *-- CustomerDemographics
    InputRiskPayload *-- PolicyRequest
    InputRiskPayload *-- ClaimHistory
    InputRiskPayload *-- ExternalRiskFactors
    ClaimHistory *-- ClaimIncident

    OmniRiskSummarizerAgent --> ChromaGuidelineManager
    OmniRiskSummarizerAgent --> LangChainRAGAgent
    LangChainRAGAgent --> LangChainGuidelineRetriever
    LangChainGuidelineRetriever --> ChromaGuidelineManager

    OmniRiskSummarizerAgent ..> UnderwritingSynthesisReport : produces
    UnderwritingSynthesisReport *-- KeyRiskIndicator
    UnderwritingSynthesisReport *-- GuidelineBreach
    UnderwritingSynthesisReport *-- RetrievedGuideline
```

---

## 4. Sequence Diagram: End-to-End Underwriting Risk Synthesis

This sequence diagram depicts the chronological message exchange from UI payload submission to vector search, rule breach auditing, and GenAI grounding.

```mermaid
sequenceDiagram
    autonumber
    actor UW as Underwriter / Browser
    participant API as FastAPI Router (/api/summarize)
    participant Pre as Preprocessor & Actuarial Engine
    participant RAG as LangChain RAG Subsystem
    participant VDB as ChromaDB Vector Store
    participant LLM as Google Gemini / Heuristic NLG
    participant Rec as Grounding Reconciler

    UW->>API: POST /api/summarize (InputRiskPayload JSON)
    activate API
    API->>API: Verify Zero-PII Regex & Schema Validation

    API->>Pre: normalize_and_consolidate(payload)
    activate Pre
    Pre->>Pre: Compute claim_freq, avg_severity, loss_ratio
    Pre->>Pre: Detect deterministic KRIs (Ground Truth)
    Pre-->>API: NormalizedRiskProfile
    deactivate Pre

    API->>RAG: synthesize_rag_context(payload)
    activate RAG
    RAG->>RAG: Construct semantic query from LOB, Perils, GeoZone
    RAG->>VDB: similarity_search_with_relevance_scores(query, top_k=4)
    activate VDB
    VDB-->>RAG: Matched Guideline Chunks & Cosine Distances
    deactivate VDB
    RAG->>RAG: audit_guideline_breaches(payload)
    Note over RAG: Audits roof age, prior cancellation,<br/>flood zone NFIP, fleet loss ratios
    RAG-->>API: rag_context (Retrieved Chunks + Detected Breaches)
    deactivate RAG

    API->>LLM: generate_summary(prompt + rag_context)
    activate LLM
    Note over LLM: LLM conditions output on<br/>corporate underwriting manuals
    LLM-->>API: Raw Synthesis Output (Verdict, Narrative, Conditions)
    deactivate LLM

    API->>Rec: reconcile_grounding(llm_out, deterministic_kris, breaches)
    activate Rec
    Rec->>Rec: Guarantee mandatory breach mitigations in policy conditions
    Rec->>Rec: Harmonize KRI codes to preserve ≥85% accuracy
    Rec-->>API: Final UnderwritingSynthesisReport
    deactivate Rec

    API-->>UW: 200 OK (JSON Payload + Processing Latency)
    deactivate API
    UW->>UW: Render Verdict Card, KRIs, RAG Inspector, & Conditions
```

---

## 5. Data Flow Diagram (DFD)

### Level 0: Context Diagram
```mermaid
flowchart LR
    Underwriter[Underwriter / Web Cockpit]
    ExcelSource[(insurance_model.xlsx)]
    KnowledgeBase[(Corporate Manuals)]
    GeminiAPI[Google Gemini API]
    
    System((OmniRisk System Boundary))

    Underwriter -- "1. Ingest Risk Payload / Form / What-If" --> System
    ExcelSource -- "2. Relational Insurance Records" --> System
    KnowledgeBase -- "3. Markdown Underwriting Guidelines" --> System
    System -- "4. Prompt with RAG Grounding" --> GeminiAPI
    GeminiAPI -- "5. Synthesized Analysis" --> System
    System -- "6. Verdict, KRIs, Breaches, Executive Summary" --> Underwriter
```

### Level 1: Detailed Data Flow Diagram
```mermaid
flowchart TD
    D1[(Raw JSON / Form)] --> P1[1.0 Ingestion & PII Scrubbing]
    P1 --> D2[Sanitized Risk Payload]

    D2 --> P2[2.0 Actuarial Preprocessing]
    P2 --> D3[Normalized Actuarial Metrics]
    P2 --> D4[Deterministic KRI Flags]

    D2 --> P3[3.0 Semantic Context Construction]
    P3 --> D5[Semantic Query String]

    D5 --> P4[4.0 ChromaDB LangChain Retrieval]
    D6[(Corporate Manuals Vector Store)] <--> P4
    P4 --> D7[Top-k Retrieved Guidelines]

    D2 --> P5[5.0 Guideline Threshold Auditing]
    D6 -.-> P5
    P5 --> D8[Detected Guideline Breaches]

    D2 & D3 & D4 & D7 & D8 --> P6[6.0 Prompt Engineering & Assembly]
    P6 --> D9[Augmented Underwriting Prompt]

    D9 --> P7[7.0 GenAI & Heuristic Synthesis]
    P7 --> D10[Candidate Synthesis Report]

    D10 & D4 & D8 --> P8[8.0 Actuarial Reconciler & Grounding Validator]
    P8 --> D11[Final Underwriting Synthesis Slip]

    D11 --> P9[9.0 UI Cockpit Rendering & Export]
```

---

## 6. Component Architecture Diagram

```mermaid
graph TD
    subgraph UI_Module ["Frontend Component Architecture"]
        View1["Interactive Form Component"]
        View2["Monaco/Textarea JSON Editor"]
        View3["Relational Excel 120-Vault"]
        View4["KRI Showcase Board"]
        View5["RAG Grounding & Breach Inspector"]
        View6["What-If Sensitivity Sandbox"]
    end

    subgraph Service_Module ["FastAPI Backend Services"]
        App["main.py (FastAPI Gateway)"]
        ExcelSvc["excel_service.py (Polars/Pandas Relational Loader)"]
        AgentSvc["agent.py (Dual-Engine Orchestrator)"]
        BenchSvc["benchmark.py (85%+ Accuracy Evaluator)"]
    end

    subgraph RAG_Module ["RAG Vector Engine Subsystem"]
        ChromaMgr["chroma_manager.py (Persistent Store)"]
        LCRetrieverClass["langchain_retriever.py (Semantic Nearest Neighbor)"]
        LCAgentClass["langchain_agent.py (Context Formatter)"]
    end

    subgraph Storage_Module ["Storage & Physical Data Layer"]
        ExcelFile["data/insurance_model.xlsx"]
        ChromaDir["knowledge_base/chroma_db/"]
        Manuals["knowledge_base/*.md"]
    end

    View1 & View2 & View3 & View4 & View5 & View6 --> App
    App --> ExcelSvc
    App --> AgentSvc
    App --> BenchSvc

    ExcelSvc --> ExcelFile
    AgentSvc --> RAG_Module
    ChromaMgr --> ChromaDir
    ChromaMgr --> Manuals
```
