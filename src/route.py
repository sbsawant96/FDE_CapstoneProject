import os
from typing import Dict, Any, List
from pydantic import BaseModel
from src.ingest.normalizer import NormalizedTicket
from src.classify import ClassificationResult

CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.80"))
KILL_SWITCH_ACTIVE = os.getenv("KILL_SWITCH_ACTIVE", "false").lower() == "true"

class RoutingDecision(BaseModel):
    ticket_id: str
    action: str  # 'auto_respond' | 'escalate' | 'block'
    confidence: float
    threshold_applied: float
    reason: str
    requires_human: bool
    escalation_queue: str

def evaluate_routing(
    ticket: NormalizedTicket,
    classification: ClassificationResult,
    retrieved_docs: List[Dict[str, Any]]
) -> RoutingDecision:
    """Deterministic routing decision enforcing safety gates and confidence thresholds (FR-04)."""
    
    # Gate 1: Global Emergency Kill Switch
    if KILL_SWITCH_ACTIVE:
        return RoutingDecision(
            ticket_id=ticket.ticket_id,
            action="escalate",
            confidence=classification.confidence,
            threshold_applied=CONFIDENCE_THRESHOLD,
            reason="Emergency kill switch activated: routing all tickets to human support.",
            requires_human=True,
            escalation_queue="general_human_support"
        )

    # Gate 2: Explicit Safety Label Protection (FR-04 / Governance)
    if ticket.must_not_auto_respond:
        return RoutingDecision(
            ticket_id=ticket.ticket_id,
            action="escalate",
            confidence=classification.confidence,
            threshold_applied=CONFIDENCE_THRESHOLD,
            reason="Ticket flagged with must_not_auto_respond constraint (sensitive/high-risk topic).",
            requires_human=True,
            escalation_queue="tier2_human_specialists"
        )

    # Gate 3: Retrieval Grounding Pre-condition
    if not retrieved_docs or len(retrieved_docs) == 0:
        return RoutingDecision(
            ticket_id=ticket.ticket_id,
            action="escalate",
            confidence=classification.confidence,
            threshold_applied=CONFIDENCE_THRESHOLD,
            reason="No relevant documentation passages found; cannot ground automated answer.",
            requires_human=True,
            escalation_queue="tier1_documentation_triage"
        )

    # Gate 4: Confidence Floor Check
    if classification.confidence < CONFIDENCE_THRESHOLD:
        return RoutingDecision(
            ticket_id=ticket.ticket_id,
            action="escalate",
            confidence=classification.confidence,
            threshold_applied=CONFIDENCE_THRESHOLD,
            reason=f"Classifier confidence ({classification.confidence:.2f}) below operational threshold ({CONFIDENCE_THRESHOLD:.2f}).",
            requires_human=True,
            escalation_queue=f"{classification.intent}_human_queue"
        )

    # Gate 5: Safe Automation Approval
    return RoutingDecision(
        ticket_id=ticket.ticket_id,
        action="auto_respond",
        confidence=classification.confidence,
        threshold_applied=CONFIDENCE_THRESHOLD,
        reason=f"Confidence {classification.confidence:.2f} >= {CONFIDENCE_THRESHOLD:.2f} with valid documentation citations and no safety violations.",
        requires_human=False,
        escalation_queue="none"
    )

if __name__ == "__main__":
    from src.ingest.normalizer import normalize_ticket
    
    print("Testing Routing Engine...")
    dummy_raw = {
        "ticket_id": "TICK-TEST-001",
        "channel": "chat",
        "customer_id": "CUST-01",
        "body": "How do I setup SAML SSO?",
        "labels": {"must_not_auto_respond": False}
    }
    dummy_ticket = normalize_ticket(dummy_raw)
    dummy_class = ClassificationResult(intent="technical_issue", urgency="medium", confidence=0.88, reasoning="Valid query")
    dummy_docs = [{"doc_id": "DOC-AUTH-003", "title": "SAML setup", "score": 0.42}]
    
    decision = evaluate_routing(dummy_ticket, dummy_class, dummy_docs)
    print(f"Action: {decision.action} | Requires Human: {decision.requires_human} | Reason: {decision.reason}")
