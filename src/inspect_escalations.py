import sqlite3
import os
import json
from collections import Counter

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "storage", "decisions.db")

def inspect_escalations():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT action_taken FROM decisions")
    actions = [r[0] for r in cursor.fetchall()]
    print(f"Action Types Recorded in DB: {actions}")

    cursor.execute("SELECT DISTINCT stage FROM decisions")
    stages = [r[0] for r in cursor.fetchall()]
    print(f"Pipeline Stages Recorded : {stages}\n")

    # Fetch all records
    cursor.execute("""
        SELECT decision_id, created_at, ticket_id, stage, prediction, 
               confidence, threshold, action_taken, reason, guardrails
        FROM decisions
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No decision records found.")
        return

    cols = ["decision_id", "created_at", "ticket_id", "stage", "prediction", 
            "confidence", "threshold", "action_taken", "reason", "guardrails"]
    records = [dict(zip(cols, r)) for r in rows]
    total_records = len(records)

    # Filter out auto-responded actions to capture all escalation variants
    escalated = [
        r for r in records
        if r["action_taken"] and r["action_taken"].lower() not in ("auto_responded", "auto_respond", "resolved", "pass")
    ]

    print("=" * 65)
    print("        AUDIT REPORT: TICKET ESCALATIONS BREAKDOWN")
    print("=" * 65)
    print(f"Total Logged Decision Rows : {total_records}")
    print(f"Total Escalated Events     : {len(escalated)}")
    print("-" * 65)

    # 1. Action Taken Distribution
    action_counts = Counter(r["action_taken"] for r in records).most_common()
    print("\n[Distribution of All Actions]")
    for act, count in action_counts:
        pct = (count / total_records) * 100
        print(f" - {str(act):<25} : {count:4d} ({pct:4.1f}%)")

    # 2. Primary Escalation Reasons
    reasons = [r["reason"] or "Unspecified" for r in escalated]
    reason_counts = Counter(reasons).most_common(8)
    print("\n[Top Escalation Drivers / Reasons]")
    for rank, (reason, count) in enumerate(reason_counts, 1):
        pct = (count / len(escalated)) * 100 if escalated else 0
        print(f" {rank:2d}. [{count:3d} | {pct:4.1f}%] - {reason[:85]}")

    # 3. Guardrails Triggered
    guardrails = [r["guardrails"] for r in escalated if r["guardrails"] and r["guardrails"] != "none"]
    if guardrails:
        print("\n[Guardrail Triggers Causing Escalation]")
        for g, count in Counter(guardrails).most_common(5):
            print(f" - {g}: {count} occurrences")

    # 4. Predictions / Intents Leading to Escalation
    preds = [r["prediction"] or "Unknown" for r in escalated]
    print("\n[Escalated Predictions / Intents]")
    for pred, count in Counter(preds).most_common(6):
        pct = (count / len(escalated)) * 100 if escalated else 0
        print(f" - {str(pred):<25} : {count:3d} ({pct:4.1f}%)")

    # 5. Low Confidence vs. Policy Guardrail Breakdown
    low_conf_count = sum(1 for r in escalated if r["confidence"] is not None and r["threshold"] is not None and r["confidence"] < r["threshold"])
    print("\n[Escalation Mechanism Breakdown]")
    print(f" - Sub-threshold Confidence (< Threshold) : {low_conf_count} ({low_conf_count/len(escalated)*100:.1f}%)" if escalated else "")

    # 6. Sample Escalated Rows
    print("\n[Representative Escalated Events (Top 3)]")
    for i, r in enumerate(escalated[:3], 1):
        print(f" Event {i} -> Ticket: {r['ticket_id']} | Stage: {r['stage']}")
        print(f"            Action: {r['action_taken']} | Conf: {r['confidence']} | Thresh: {r['threshold']}")
        print(f"            Reason: {r['reason']}")

if __name__ == "__main__":
    inspect_escalations()
