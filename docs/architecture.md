# System Architecture Specification

## Pipeline Flow Overview

\\\
[ Inbound Channels ]
  (Email | Chat | Docs Comment | Forum)
                 ¦
                 ?
     [ src/ingest.py (A2) ] ------------? NormalizedTicket Schema
                 ¦
                 ?
     [ src/classify.py ] --------------? Intent, Urgency, Confidence Score
                 ¦
                 ?
     [ src/retrieve.py ] --------------? Chroma Vector Store (Top-K Chunks)
                 ¦
                 ?
     [ src/route.py ] -----------------? Confidence Threshold Check (0.80)
           ¦          ¦                  & Safety Flags Check
     [PASS]           [FAIL / ESCALATE]
       ¦                      ¦
       ?                      ?
[ src/generate.py ]      [ Human Agent Queue ]
       ¦                      ¦
       ?                      ¦
[ src/guardrails.py ]         ¦
  (PII, Grounding, Tone)      ¦
       ¦                      ¦
  [PASS] --? Outbound Message ¦
       ¦                      ¦
       ?                      ?
--------------------------------------------
   [ src/logging_store.py ] --? storage/decisions.db (100% Coverage)
--------------------------------------------
\\\

## Component Responsibilities

1. **\src/ingest.py\**: Channel-specific adapters producing unified metadata[cite: 3].
2. **\src/classify.py\**: Zero/few-shot intent tagging with probabilistic calibration[cite: 1, 3].
3. **\src/retrieve.py\**: Embedded vector similarity search over documentation passages[cite: 3].
4. **\src/route.py\**: Deterministic gate enforcing safety boundaries and confidence floors[cite: 2, 3].
5. **\src/generate.py\**: Citation-backed answer drafting with prompt versioning[cite: 2, 3].
6. **\src/guardrails.py\**: Pre-transmission blockers (PII, hallucination, instruction integrity)[cite: 2].
7. **\src/logging_store.py\**: Immutable record-keeping for forensic analysis and compliance[cite: 2, 3].
