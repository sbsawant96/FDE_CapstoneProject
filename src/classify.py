import json
import re
from typing import Dict, Any
from pydantic import BaseModel, Field
from src.utils_llm import call_groq_cached

PROMPT_VERSION = "PR-CLS-v1.0"

class ClassificationResult(BaseModel):
    intent: str
    urgency: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str

SYSTEM_PROMPT = """You are an expert customer support triage classifier for CloudServe.
Analyze the customer's query and extract:
1. Intent: Exactly one of ['account_access', 'billing_inquiry', 'technical_issue', 'feature_request', 'security_concern', 'general_inquiry'].
2. Urgency: Exactly one of ['low', 'medium', 'high', 'critical'].
3. Confidence: A calibrated float between 0.0 and 1.0 representing how confident you are in this classification.
4. Reasoning: A concise 1-sentence explanation of why this was chosen.

Respond strictly in valid JSON matching this schema:
{
  "intent": "<intent>",
  "urgency": "<urgency>",
  "confidence": <float>,
  "reasoning": "<string>"
}"""

def classify_ticket(ticket_text: str) -> ClassificationResult:
    """Classifies inbound ticket text into intent, urgency, and confidence (FR-02)."""
    prompt = f"{SYSTEM_PROMPT}\n\nCustomer Inquiry:\n\"{ticket_text}\"\n\nJSON Output:"
    
    raw = call_groq_cached(prompt=prompt, temperature=0.0) or ""
    raw_response = raw.strip()

    match = re.search(r"\{.*\}", raw_response, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(0))
            return ClassificationResult(
                intent=str(data.get("intent", "general_inquiry")),
                urgency=str(data.get("urgency", "medium")),
                confidence=float(data.get("confidence", 0.5)),
                reasoning=str(data.get("reasoning", "Standard classification"))
            )
        except Exception:
            pass

    return ClassificationResult(
        intent="general_inquiry",
        urgency="medium",
        confidence=0.50,
        reasoning="Classifier fallback triggered due to unstructured response."
    )

if __name__ == "__main__":
    print("Testing Intent Classifier with fallback...")
    res = classify_ticket("I need help resetting my 2FA token, it is locked out.")
    print(f"Intent: {res.intent} | Urgency: {res.urgency} | Conf: {res.confidence}")
