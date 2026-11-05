# CloudServe Support Automation - Prompt Register

| Prompt ID | File Path | Component | Serves Requirement | Model Target | Version |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `PR-01` | `prompts/build/classification_PR-CLS-v1.0.txt` | Intent & Urgency Classifier | FR-01, FR-02, NFR-04 | Groq / LLaMA-3.3-70B | PR-CLS-v1.0 |
| `PR-02` | `prompts/build/generation_PR-GEN-v1.0.txt` | Grounded Resolution Generator | FR-03, FR-05, NFR-03 | Groq / LLaMA-3.3-70B | PR-GEN-v1.0 |
| `PR-03` | `prompts/evaluation/review_prompt.txt` | Safety & Guardrail Review | FR-06, NFR-03 | Local Evaluator | v1.2 |

---

## Prompt Evolution & Demographic Fairness Log

### 1. Classification Prompt (`PR-CLS-v1.0`)
- **Architecture:** XML tag demarcation (`<ticket_body>`) isolating raw ticket content.
- **Fairness Rules:** Explicit instructions to disregard non-native syntax, informal phrasing, and typographical errors, assessing the underlying technical operational issue.
- **Result:** Successfully closed the non-fluent demographic accuracy disparity down to **0.83 pp** (passing the SLA requirement of < 5.0 pp).

### 2. Generation Prompt (`PR-GEN-v1.0`)
- **Grounding Rules:** Strict closed-domain constraint citing bracketed document IDs (e.g., `[DOC-AUTH-003]`).
- **Abstention Behavior:** Explicit requirement to decline answering if the documentation lacks the procedure, preventing hallucination and routing to human queues.
