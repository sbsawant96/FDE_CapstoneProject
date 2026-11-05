import json
import sqlite3
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "storage", "decisions.db")

def log_decision(
    ticket_id: str,
    stage: str,
    prediction: Optional[str],
    confidence: float,
    threshold: float,
    action_taken: str,
    reason: str,
    sources_used: Optional[list] = None,
    guardrails: Optional[dict] = None,
    prompt_version: str = "PR-GEN-v1.0",
    requirement_ids: Optional[list] = None
) -> str:
    """Writes an immutable decision record to storage/decisions.db (FR-07)."""
    
    decision_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO decisions (
            decision_id, created_at, ticket_id, stage, prediction,
            confidence, threshold, action_taken, reason, sources_used,
            guardrails, prompt_version, requirement_ids
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        decision_id,
        timestamp,
        ticket_id,
        stage,
        prediction,
        confidence,
        threshold,
        action_taken,
        reason,
        json.dumps(sources_used or []),
        json.dumps(guardrails or {}),
        prompt_version,
        json.dumps(requirement_ids or ["FR-04", "FR-07"])
    ))
    
    conn.commit()
    conn.close()
    return decision_id

if __name__ == "__main__":
    print("Testing Decision Logging Store...")
    dec_id = log_decision(
        ticket_id="TICK-TEST-999",
        stage="routing",
        prediction="technical_issue",
        confidence=0.92,
        threshold=0.80,
        action_taken="auto_respond",
        reason="Confidence score exceeded operational threshold with clean guardrails.",
        sources_used=["DOC-AUTH-003"],
        guardrails={"passed": True, "violations": []},
        requirement_ids=["FR-02", "FR-04"]
    )
    print(f"Successfully logged decision: {dec_id}")
