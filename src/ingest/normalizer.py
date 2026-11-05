from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class NormalizedTicket(BaseModel):
    ticket_id: str
    channel: str
    customer_id: str
    customer_tier: str
    customer_region: str
    language_fluency: str
    subject: str = ""
    raw_body: str
    processed_text: str
    expected_doc_ids: Optional[List[str]] = Field(default_factory=list)
    must_not_auto_respond: bool = False

def normalize_ticket(raw: Dict[str, Any]) -> NormalizedTicket:
    """Normalizes raw channel payloads into a single internal representation (Criterion A2)."""
    subject = (raw.get("subject") or "").strip()
    body = (raw.get("body") or "").strip()
    channel = raw.get("channel", "email").lower()
    
    if subject:
        processed_text = f"Subject: {subject}\n\nContent: {body}"
    else:
        processed_text = body

    labels = raw.get("labels", {})
    return NormalizedTicket(
        ticket_id=raw.get("ticket_id", "UNKNOWN"),
        channel=channel,
        customer_id=raw.get("customer_id", "UNKNOWN"),
        customer_tier=raw.get("customer_tier", "standard"),
        customer_region=raw.get("customer_region", "unknown"),
        language_fluency=raw.get("language_fluency", "fluent"),
        subject=subject,
        raw_body=body,
        processed_text=processed_text,
        expected_doc_ids=labels.get("expected_doc_ids", []),
        must_not_auto_respond=labels.get("must_not_auto_respond", False),
    )
