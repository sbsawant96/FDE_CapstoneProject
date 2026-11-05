# CloudServe Automated Support Triage - Prompt Register

| Prompt ID | Name & Purpose | Stage | Serves Requirement | Model | Current Version |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `PR-01` | Intent & Urgency Classifier | Classification | FR-01, FR-02 | Cascade (Qwen 27B / GPT-OSS 120B) | v2.0 |
| `PR-02` | Grounded Response Generator | Generation | FR-03, FR-04 | Cascade (Qwen 27B / GPT-OSS 120B) | v2.0 |
| `PR-03` | Output Citation & Guardrail Interceptor | Guardrails | FR-05, NFR-03 | Local Evaluator | v1.2 |

## Prompt Change Log
- **v1.0**: Baseline single-prompt intent classification.
- **v2.0**: Re-architected with XML delimiters `<ticket_body>` and explicit few-shot counter-examples to reduce non-fluent demographic disparity from 10.0 pp down to 1.14 pp.
