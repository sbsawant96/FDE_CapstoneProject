# CloudServe Solutions — Stage 1 Discovery Workbook

## 1. People & Operational Roles

| Role / Stakeholder | Core Operational Need | Implicit / Hidden Tension | Stance on Automation |
| :--- | :--- | :--- | :--- |
| **Marcus Vance** (VP Customer Support) | Cut Tier 1 operational costs and lower ticket queues. | Aggressive deflection target (wants 70%+ automation) ignores the 17.4% strict guardrail boundary. | Demands maximum volume deflection. |
| **Daniel Brooks** (Head of Engineering) | System reliability, auditability, and deterministic bounds. | Skeptical of LLM non-determinism, API latency on chat, and unmonitored production drift. | Demands 100% decision logging, p95 < 3s, and strict evaluation gates. |
| **Ines Gomez** (Director of Product) | Protect customer trust, NPS, and brand equity. | Fears incorrect automated answers will churn Enterprise/Business accounts (49.4% of volume). | Prioritizes zero hallucination and human escalation over raw speed. |
| **Support Engineers / Agents** | Reduce repetitive manual lookups for trivial documentation. | Skeptical of AI routing dumping complex multi-faceted edge cases into general queues without context. | Needs high-confidence routing and structured handover notes. |

---

## 2. Empirical Volume & Channel Breakdown (500 Tickets)

| Channel | Ticket Count | Percentage | Operational Latency Constraint | Ingestion Characteristics |
| :--- | :--- | :--- | :--- | :--- |
| **Email** | 212 | 42.4% | Async SLA (< 5 minutes first response) | Structured with subject lines and multi-line body text. |
| **Chat** | 155 | 31.0% | Synchronous (p95 latency < 3 seconds) | Short, rapid queries; highly latency-sensitive. |
| **Docs Comment** | 78 | 15.6% | Async | Direct documentation feedback or contextual bug/clarification requests. |
| **Forum** | 55 | 11.0% | Public / Community | Unstructured phrasing, informal language, community-facing. |
| **Total** | **500** | **100.0%** | — | Mean length: 24.6 words; Median: 25.0 words. |

---

## 3. Pain Points & Stakeholder Contradictions

1. **Volume Deflection vs. Safety Envelope:**
   * *The Tension:* Marcus targets 70% automatic resolution. However, dataset analysis reveals that while 71.4% (357 tickets) are answerable from docs, 17.4% (87 tickets) are marked must_not_auto_respond: true (e.g., billing disputes, account takeovers, edge security issues).
   * *Reconciliation:* An unconstrained 70% deflection will inevitably trigger safety failures. Automation must be capped to tickets that are strictly documented AND clear of must_not_auto_respond flags.
2. **Synchronous Chat Latency vs. LLM Chain Overhead:**
   * *The Tension:* Chat accounts for 31.0% of tickets where customers expect immediate replies. Combining intent classification, dense retrieval, reranking, generation, and guardrails inside 3.0 seconds is a hard engineering boundary.
   * *Reconciliation:* Intent classification and guardrail checks must be streamlined with local heuristics, cached embeddings, and fast LLM inference (openai/gpt-oss-20b).
3. **Language Fairness vs. Dense Retrieval Degeneracy:**
   * *The Tension:* 24.0% (120 tickets) come from non-fluent English speakers. Dense embeddings match poorly when grammar and phrasing diverge from official documentation.
   * *Reconciliation:* Must implement query preprocessing / keyword expansion and track sub-segment accuracy to keep performance delta below 5 percentage points.

---

## 4. Data Quality & Documentation Coverage

* **Answerability Ratio:** 71.4% (357 tickets) map directly to data/documentation.json.
* **Knowledge Gaps:** 28.6% of tickets cannot be answered from documentation. Attempting to answer these automatically guarantees hallucination.
* **Pre-classification State:** 100% of tickets lack explicit category tags (category: None), requiring automated intent classification in Stage 2.
* **Text Brevity:** Ticket bodies are concise (average 24.6 words), meaning classification must extract intent from limited token contexts without rambling prompt templates.

---

## 5. Success Metrics Alignment (Evaluation Pyramid)

| Tier | Metric | Baseline | Target | Primary Safeguard |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1: Business Outcomes** | First Contact Resolution (FCR) | 42% | = 60% | Auto-close only verified documented answers |
| | Mean Time to First Reply | 8–12 hrs | < 5 min | Automated processing queue |
| | Escalation Rate | 58% | = 30% | Deterministic routing on low confidence |
| **Tier 2: Technical Performance** | Classification Precision | — | = 85% | Multi-class intent validation |
| | Hallucination Rate | — | = 5% | Strict source grounding check |
| | Citation Accuracy | — | = 95% | Sentence-level claim verification |
| | Latency (p95) | — | < 3.0s | Profiling end-to-end pipeline |
| **Tier 3: Governance Conditions** | PII In Outbound Text | — | 0 occurrences | Regex + NER guardrail blocking output |
| | Cross-Group Disparity | — | < 5% delta | Fairness slicing (Fluent vs Non-Fluent) |
| | Decision Log Coverage | — | 100% | SQLite logging across every stage |

---

## 6. Risk Assessment Matrix

| Risk ID | Description | Likelihood | Impact | Built-in Architectural Mitigation | Owner |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **R-01** | Hallucinated or confident incorrect answers | High | High | Grounding guardrail checks claims against retrieved chunks; blocks if similarity < threshold. | ML Engineer |
| **R-02** | Customer PII leaked in responses | Low | Critical | Outbound PII scanner blocks transmission if email, API keys, or phone numbers are detected. | Security / Gov |
| **R-03** | Prompt injection via ticket content | Medium | High | System prompts use strict role delimiters and treat user input strictly as inert data. | ML Engineer |
| **R-04** | Disproportionate failure on non-fluent users | High | Medium | Sub-group evaluation harness checks accuracy gap; fallback to human review on low confidence. | Quality Lead |
| **R-05** | Stale documentation causes wrong procedures | Medium | Medium | Metadata tracking on doc chunks with version logging in decisions.db. | Docs Lead |
| **R-06** | Upstream Groq API downtime or rate-limits | Medium | High | Exponential retry backoff, disk caching (.llm_cache), and automatic queue fallback to human agent. | Platform Eng |
| **R-07** | Kill Switch Activation Requirement | Low | Critical | Global configuration flag toggles system into 100% passthrough escalation mode in < 1 second. | Support Lead |

---

## 7. Problem Statement & Operational Boundary

CloudServe Solutions processes hundreds of support tickets daily across four distinct channels (Email, Chat, Docs Comments, Forum), resulting in prolonged response times (8–12 hour baseline) and high agent burnout. While 71.4% of inbound inquiries correspond to existing documentation, 17.4% represent high-risk scenarios (account security, billing disputes, complex bugs) that must never be answered autonomously. 

The objective of this project is to implement an automated triage, retrieval-augmented response, and deterministic routing system that increases First Contact Resolution from 42% to = 60% and lowers first response times to under 5 minutes, while maintaining zero PII leakage, an end-to-end p95 latency under 3 seconds for chat, and a strict hallucination rate below 5%. Any inquiry failing the 0.80 confidence threshold or triggering safety guardrails will be deterministically routed to human support with full diagnostic audit logs.
