# CloudServe Support Automation Capstone — Project Effort Log

**Project Name:** CloudServe Automated Support Triage & Resolution System  
**Track:** Forward Deployed AI Engineering  
**Total Documented Effort:** 54 Hours  
**Audit Period:** Stages 1 through 5  

---

## 1. Effort Summary by Project Stage

| Stage ID | Stage Name / Domain | Total Hours | Core Milestone Deliverables |
| :--- | :--- | :--- | :--- |
| **Stage 1** | Discovery & Problem Framing | 8.5 hrs | Interview transcript analysis, baseline volume metrics, cohort disparity discovery. |
| **Stage 2** | System Architecture & PRD v1.0 | 9.0 hrs | Functional requirements (FR-01 to FR-07), NFR definitions, component dataflow design. |
| **Stage 3** | Prompt Engineering & In-System Evaluation | 11.5 hrs | Intent/urgency prompt calibration, demographic fairness XML isolation, prompt register. |
| **Stage 4** | System Implementation & Integration | 14.5 hrs | Modular pipeline build, ChromaDB vector store, SQLite audit store, FastAPI endpoints. |
| **Stage 5** | Benchmark Evaluation & Governance Audit | 10.5 hrs | Unattended harness execution, 500-ticket evaluation, fairness audit, PRD v2.0 revision. |
| **Total** | **End-to-End Capstone Execution** | **54.0 hrs** | **Full production triage system passing all NFR benchmarks.** |

---

## 2. Granular Activity Log & Task Breakdown

### Stage 1: Discovery & Problem Framing (8.5 Hours)
* **Session 1.1 (3.0 hrs):** Analyzed qualitative stakeholder interview transcripts (Support Director, Operations Lead, Reliability Lead, Compliance). Identified core operational bottlenecks: 42% baseline FCR, manual triage latency, and lack of guardrails.
* **Session 1.2 (3.5 hrs):** Conducted exploratory data analysis on 500 historical support tickets (data/development_tickets.json). Quantified intent distributions, channel volume splits, and identified the 10.0 pp baseline accuracy penalty on non-fluent customer phrasing.
* **Session 1.3 (2.0 hrs):** Synthesized findings into Stage1_Discovery_Workbook.md. Defined quantifiable baseline KPIs, customer tier escalation rules, and technical risk boundaries.

---

### Stage 2: System Architecture & Requirements Engineering (9.0 Hours)
* **Session 2.1 (4.0 hrs):** Authored Product Requirements Document (PRD v1.0). Formalized functional requirements FR-01 through FR-07 and non-functional requirements NFR-01 through NFR-05.
* **Session 2.2 (3.5 hrs):** Formulated architectural blueprints: modular cascade pipeline, local vector retrieval strategy using ChromaDB, deterministic routing gate rules, and 13-field immutable SQLite audit schema.
* **Session 2.3 (1.5 hrs):** Constructed traceability matrix mapping each PRD requirement to its responsible Python module, evaluation metric, and verification test.

---

### Stage 3: Prompt Engineering & Demographic Calibration (11.5 Hours)
* **Session 3.1 (3.5 hrs):** Implemented baseline prompts for classification (PR-CLS-v1.0) and grounded generation (PR-GEN-v1.0). Identified failure modes: schema drift in JSON outputs and high hallucination rates on open generation.
* **Session 3.2 (4.5 hrs):** Conducted systematic prompt tuning for demographic subgroup fairness. Added XML boundary tags (<ticket_body>) and semantic invariance instructions to prevent grammar/spelling bias. Reduced fluency disparity from 10.0 pp down to 0.83 pp.
* **Session 3.3 (3.5 hrs):** Hardened generation prompt with closed-domain constraints and mandatory bracketed citations ([DOC-xxx]). Established version-controlled prompts/ directory and prompts/README.md register.

---

### Stage 4: Implementation & Integration (14.5 Hours)
* **Session 4.1 (4.0 hrs):** Implemented ingestion normalizer (src/ingest/normalizer.py), classification engine (src/classify.py), and dense retrieval engine (src/retrieve.py) using sentence-transformers/all-MiniLM-L6-v2.
* **Session 4.2 (4.5 hrs):** Built deterministic routing logic (src/route.py), grounded generator (src/generate.py), and pre-outbound regex guardrails (src/guardrails.py) for PII detection and citation validation.
* **Session 4.3 (3.0 hrs):** Engineered SQLite audit logging store (src/logging_store.py) with WAL mode, persisting all 13 mandatory transactional fields to storage/decisions.db.
* **Session 4.4 (3.0 hrs):** Developed FastAPI service (src/api.py) exposing /health and /triage endpoints with Pydantic validation. Configured pytest smoke tests and .github/workflows/ci.yml.

---

### Stage 5: Evaluation & Fairness Auditing (10.5 Hours)
* **Session 5.1 (3.5 hrs):** Built unattended evaluation harness (evaluation/harness.py) supporting CLI arguments (--input, --output) and computing confusion matrices, FCR, escalation rates, and p95 latency.
* **Session 5.2 (3.0 hrs):** Executed full 500-ticket benchmark run against ground truth. Verified that all target SLAs cleared contractual thresholds (FCR: 80.2%, p95 latency: 0.098s, fluency disparity: 0.83 pp).
* **Session 5.3 (2.0 hrs):** Audited failure cases, false-positive guardrail intercepts, and calibrated confidence thresholds ($	au = 0.75$).
* **Session 5.4 (2.0 hrs):** Authored PRD v2.0 revision log and consolidated findings into Stage5_Evaluation_Workbook.md and evaluation_report.md.
