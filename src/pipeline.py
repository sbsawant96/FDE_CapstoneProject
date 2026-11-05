from typing import Dict, Any, Optional
from pydantic import BaseModel

from src.ingest.normalizer import normalize_ticket, NormalizedTicket
from src.classify import classify_ticket, ClassificationResult
from src.retrieve import search_docs
from src.route import evaluate_routing, RoutingDecision
from src.generate import generate_grounded_response
from src.guardrails import inspect_guardrails
from src.logging_store import log_decision

class PipelineOutput(BaseModel):
    ticket_id: str
    channel: str
    action_taken: str
    outbound_message: Optional[str]
    escalation_reason: Optional[str]
    escalation_queue: Optional[str]
    intent: str
    confidence: float
    decision_id: str

def process_ticket(raw_ticket: Dict[str, Any]) -> PipelineOutput:
    """End-to-end pipeline orchestrator executing triage, retrieval, routing, and guardrails."""
    
    # 1. Normalization (FR-01)
    ticket: NormalizedTicket = normalize_ticket(raw_ticket)
    query_text = ticket.processed_text or ticket.raw_body
    
    # 2. Intent & Urgency Classification (FR-02)
    classification: ClassificationResult = classify_ticket(query_text)
    
    # 3. Dense Retrieval from Chroma (FR-03)
    retrieved_chunks = search_docs(query_text, top_k=5)
    
    # 4. Deterministic Routing Gate (FR-04)
    routing: RoutingDecision = evaluate_routing(ticket, classification, retrieved_chunks)
    
    # If routed to human, record decision and terminate early
    if routing.requires_human:
        dec_id = log_decision(
            ticket_id=ticket.ticket_id,
            stage="routing",
            prediction=classification.intent,
            confidence=classification.confidence,
            threshold=routing.threshold_applied,
            action_taken=routing.action,
            reason=routing.reason,
            sources_used=[c.get("doc_id") for c in retrieved_chunks],
            guardrails={"passed": True, "violations": []},
            requirement_ids=["FR-02", "FR-04", "FR-07"]
        )
        return PipelineOutput(
            ticket_id=ticket.ticket_id,
            channel=ticket.channel,
            action_taken="escalated_to_human",
            outbound_message=None,
            escalation_reason=routing.reason,
            escalation_queue=routing.escalation_queue,
            intent=classification.intent,
            confidence=classification.confidence,
            decision_id=dec_id
        )

    # 5. Grounded Response Generation (FR-05)
    gen_result = generate_grounded_response(query_text, retrieved_chunks)
    candidate_text = gen_result["response_text"]
    cited_docs = gen_result["cited_docs"]
    
    # 6. Pre-Outbound Guardrail Enforcement (FR-06)
    guard_result = inspect_guardrails(candidate_text, cited_docs)
    
    if not guard_result["passed"]:
        reason_msg = f"Guardrail violations detected: {', '.join(guard_result['violations'])}"
        dec_id = log_decision(
            ticket_id=ticket.ticket_id,
            stage="guardrails",
            prediction=classification.intent,
            confidence=classification.confidence,
            threshold=routing.threshold_applied,
            action_taken="block_and_escalate",
            reason=reason_msg,
            sources_used=cited_docs,
            guardrails=guard_result,
            prompt_version=gen_result["prompt_version"],
            requirement_ids=["FR-05", "FR-06", "FR-07"]
        )
        return PipelineOutput(
            ticket_id=ticket.ticket_id,
            channel=ticket.channel,
            action_taken="escalated_to_human",
            outbound_message=None,
            escalation_reason=reason_msg,
            escalation_queue="guardrail_review_queue",
            intent=classification.intent,
            confidence=classification.confidence,
            decision_id=dec_id
        )

    # 7. Safe Outbound Transmission & Audit Logging (FR-07)
    dec_id = log_decision(
        ticket_id=ticket.ticket_id,
        stage="outbound_delivery",
        prediction=classification.intent,
        confidence=classification.confidence,
        threshold=routing.threshold_applied,
        action_taken="auto_responded",
        reason="Passed all confidence gates, grounding checks, and outbound safety guardrails.",
        sources_used=cited_docs,
        guardrails=guard_result,
        prompt_version=gen_result["prompt_version"],
        requirement_ids=["FR-01", "FR-02", "FR-03", "FR-04", "FR-05", "FR-06", "FR-07"]
    )
    
    return PipelineOutput(
        ticket_id=ticket.ticket_id,
        channel=ticket.channel,
        action_taken="auto_responded",
        outbound_message=candidate_text,
        escalation_reason=None,
        escalation_queue=None,
        intent=classification.intent,
        confidence=classification.confidence,
        decision_id=dec_id
    )

if __name__ == "__main__":
    print("Testing End-to-End Orchestrator Pipeline...\n")
    
    sample_safe = {
        "ticket_id": "TICK-E2E-001",
        "channel": "chat",
        "customer_id": "CUST-E2E-1",
        "body": "How do I configure SAML SSO and verify assertion consumer service URL?",
        "labels": {"must_not_auto_respond": False}
    }
    out_safe = process_ticket(sample_safe)
    print("[Scenario A - Safe Ticket]")
    print(f"Action: {out_safe.action_taken} | Intent: {out_safe.intent} | Confidence: {out_safe.confidence:.2f}")
    preview = out_safe.outbound_message[:120] if out_safe.outbound_message else 'None'
    print(f"Outbound Message Preview: {preview}...")
    print(f"Audit Decision ID: {out_safe.decision_id}\n")
    
    sample_restricted = {
        "ticket_id": "TICK-E2E-002",
        "channel": "email",
        "customer_id": "CUST-E2E-2",
        "body": "My account was compromised and billing was charged without my permission. Issue immediate refund.",
        "labels": {"must_not_auto_respond": True}
    }
    out_restricted = process_ticket(sample_restricted)
    print("[Scenario B - Restricted Safety Ticket]")
    print(f"Action: {out_restricted.action_taken} | Queue: {out_restricted.escalation_queue}")
    print(f"Reason: {out_restricted.escalation_reason}")
    print(f"Audit Decision ID: {out_restricted.decision_id}")
