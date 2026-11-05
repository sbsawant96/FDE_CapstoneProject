from typing import List, Dict, Any
from src.utils_llm import call_groq_cached

PROMPT_VERSION = "PR-GEN-v1.0"

SYSTEM_PROMPT = """You are CloudServe's automated support assistant.
Your task is to answer the customer's inquiry clearly, professionally, and concisely.

STRICT CONSTRAINTS:
1. Use ONLY the factual information provided in the Reference Documentation below.
2. If the reference documentation does not contain the answer, explicitly state that you cannot verify the procedure and recommend agent assistance.
3. Every procedural recommendation or factual claim MUST cite the source document ID in brackets (e.g. [DOC-AUTH-003]).
4. NEVER invent URLs, pricing, API keys, or guarantees.
5. Keep the tone helpful, direct, and empathetic."""

def generate_grounded_response(ticket_body: str, docs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generates an answer strictly grounded in retrieved documentation chunks (FR-05)."""
    
    docs_context = ""
    for idx, d in enumerate(docs, 1):
        docs_context += f"--- Document [{d.get('doc_id')}] : {d.get('title')} ---\n"
        docs_context += f"{d.get('content')}\n\n"
        
    user_prompt = f"""Reference Documentation:
{docs_context}

Customer Ticket:
\"{ticket_body}\"

Generate the response following all constraints:"""

    raw_response = call_groq_cached(
        prompt=f"{SYSTEM_PROMPT}\n\n{user_prompt}",
        temperature=0.0
    ).strip()
    
    # Extract cited doc_ids present in the generated text
    cited_docs = [d.get("doc_id") for d in docs if d.get("doc_id") in raw_response]
    
    return {
        "response_text": raw_response,
        "prompt_version": PROMPT_VERSION,
        "cited_docs": cited_docs
    }

if __name__ == "__main__":
    sample_ticket = "How do I ensure new users are automatically provisioned when using SAML SSO?"
    sample_docs = [{
        "doc_id": "DOC-AUTH-003",
        "title": "Single sign-on configuration with SAML providers",
        "content": "Enable just-in-time provisioning if new users should be created on first login, and set a default role for provisioned users."
    }]
    
    print("Testing Grounded Generation...")
    output = generate_grounded_response(sample_ticket, sample_docs)
    print("\n--- Generated Response ---")
    print(output["response_text"])
    print(f"\nPrompt Version: {output['prompt_version']}")
    print(f"Cited Documents: {output['cited_docs']}")
