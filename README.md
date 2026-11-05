# CloudServe Support Automation System (Capstone Project)

Automated customer support ticket triage, retrieval-augmented answer generation, and safety guardrail auditing built for CloudServe Solutions.

## Architecture
- **Stage 1 (Classification)**: Cascaded LLM intent/urgency classification with confidence scoring.
- **Stage 2 (Retrieval)**: Local ChromaDB vector store searching 29 documentation articles with MiniLM-L6-v2 embeddings.
- **Stage 3 (Generation)**: Context-grounded response generation citing official documentation.
- **Stage 4 (Guardrails & Logging)**: PII scanning, citation validation, and SQLite transactional audit logging (`decisions.db`).

## Quickstart (Clean Checkout)

```bash
# 1. Initialize environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt

# 2. Environment Configuration
cp .env.example .env
# Edit .env and supply your GROQ_API_KEY
