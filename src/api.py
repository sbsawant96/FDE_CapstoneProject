from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from src.pipeline import process_ticket, PipelineOutput

app = FastAPI(
    title="CloudServe Support Automation Triage API",
    version="1.0.0",
    description="Automated tier-1 ticket triage, retrieval-augmented response generation, and guardrail verification."
)

class TicketRequest(BaseModel):
    ticket_id: str
    text: str
    channel: Optional[str] = "web"
    customer_tier: Optional[str] = "standard"
    language_fluency: Optional[str] = "fluent"

class TicketResponse(BaseModel):
    ticket_id: str
    action_taken: str
    outbound_message: Optional[str]
    intent: Optional[str]
    urgency: Optional[str]
    confidence: Optional[float]
    escalation_reason: Optional[str]
    sources_used: List[Dict[str, Any]] = []

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "support-triage-pipeline"}

@app.post("/triage", response_model=TicketResponse)
def triage_ticket(ticket: TicketRequest):
    try:
        raw_ticket = ticket.dict()
        result: PipelineOutput = process_ticket(raw_ticket)
        return TicketResponse(
            ticket_id=ticket.ticket_id,
            action_taken=result.action_taken,
            outbound_message=result.outbound_message,
            intent=result.intent,
            urgency=result.urgency,
            confidence=result.confidence,
            escalation_reason=result.escalation_reason,
            sources_used=result.sources_used
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
