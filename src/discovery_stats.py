import json
import os
from collections import Counter
from statistics import mean, median

data_path = os.path.join(os.path.dirname(__file__), "..", "data", "development_tickets.json")

with open(data_path, "r", encoding="utf-8") as f:
    tickets = json.load(f)

total = len(tickets)
channels = Counter(t.get("channel") for t in tickets)
tiers = Counter(t.get("customer_tier") for t in tickets)
categories = Counter(t.get("category") for t in tickets)
languages = Counter(t.get("language_fluency") for t in tickets)

# Label analytics
answerable = sum(1 for t in tickets if t.get("labels", {}).get("answerable_from_docs") is True)
must_not_auto = sum(1 for t in tickets if t.get("labels", {}).get("must_not_auto_respond") is True)
human_escalate = sum(1 for t in tickets if t.get("labels", {}).get("requires_human_escalation") is True)

# Length statistics (in words)
body_lengths = [len(t.get("body", "").split()) for t in tickets]

print("=== DATASET STATISTICAL PROFILE (500 TICKETS) ===")
print(f"Total Tickets: {total}")
print(f"\nChannel Distribution:")
for k, v in channels.most_common():
    print(f"  - {k}: {v} ({v/total*100:.1f}%)")

print(f"\nCustomer Tier Distribution:")
for k, v in tiers.most_common():
    print(f"  - {k}: {v} ({v/total*100:.1f}%)")

print(f"\nLanguage Fluency:")
for k, v in languages.most_common():
    print(f"  - {k}: {v} ({v/total*100:.1f}%)")

print(f"\nTop Categories:")
for k, v in categories.most_common():
    print(f"  - {k}: {v} ({v/total*100:.1f}%)")

print(f"\nAutomation Feasibility & Guardrails:")
print(f"  - Answerable from docs: {answerable} ({answerable/total*100:.1f}%)")
print(f"  - MUST NOT auto-respond: {must_not_auto} ({must_not_auto/total*100:.1f}%)")
print(f"  - Requires Human Escalation: {human_escalate} ({human_escalate/total*100:.1f}%)")

print(f"\nBody Word Counts: Min={min(body_lengths)}, Max={max(body_lengths)}, Median={median(body_lengths)}, Mean={mean(body_lengths):.1f}")
