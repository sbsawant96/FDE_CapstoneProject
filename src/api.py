from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from src.pipeline import process_ticket, PipelineOutput

app = FastAPI(
    title="CloudServe Support Automation Triage API",
    version="1.0.0",
    description="Automated tier-1 ticket triage, retrieval-augmented answer generation, and guardrails."
)

class TicketRequest(BaseModel):
    ticket_id: str
    text: str
    channel: Optional[str] = "web"
    customer_tier: Optional[str] = "standard"
    language_fluency: Optional[str] = "fluent"

class TicketResponse(BaseModel):
    ticket_id: str
    channel: str
    action_taken: str
    outbound_message: Optional[str]
    escalation_reason: Optional[str]
    escalation_queue: Optional[str]
    intent: str
    confidence: float
    decision_id: str

@app.get("/")
def root():
    return {
        "service": "CloudServe Support Automation API",
        "status": "online",
        "docs_url": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/triage", response_model=TicketResponse)
def triage_ticket(ticket: TicketRequest):
    try:
        raw_ticket = {
            "ticket_id": ticket.ticket_id,
            "id": ticket.ticket_id,
            "text": ticket.text,
            "body": ticket.text,
            "channel": ticket.channel,
            "customer_tier": ticket.customer_tier,
            "language_fluency": ticket.language_fluency
        }
        
        result: PipelineOutput = process_ticket(raw_ticket)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
