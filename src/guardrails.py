import re
from typing import Dict, Any, List

# Standard PII regular expressions
PATTERNS = {
    "api_key": re.compile(r"(?:api[_-]?key|secret|token)[\s:=]+['\"]?([a-zA-Z0-9_\-]{16,})['\"]?", re.IGNORECASE),
    "credit_card": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "email_leak": re.compile(r"\b[A-Za-z0-9._%+-]+@(?!cloudserve\.com)[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
}

def inspect_guardrails(response_text: str, cited_docs: List[str]) -> Dict[str, Any]:
    """Inspects generated response for zero-tolerance governance criteria (FR-06)."""
    
    violations = []
    
    # Check 1: Zero-tolerance PII detection
    for pii_type, pattern in PATTERNS.items():
        if pattern.search(response_text):
            violations.append(f"PII detected: {pii_type}")
            
    # Check 2: Grounding and citation presence
    if not cited_docs or len(cited_docs) == 0:
        violations.append("Grounding failure: response contains no valid document citations")
        
    # Check 3: Scope & Commitment checks
    forbidden_terms = ["guarantee 100% uptime", "full refund authorized", "our CEO promised"]
    for term in forbidden_terms:
        if term in response_text.lower():
            violations.append(f"Scope violation: unauthorized commitment '{term}'")

    passed = len(violations) == 0
    return {
        "passed": passed,
        "violations": violations,
        "action": "pass" if passed else "block_and_escalate"
    }

if __name__ == "__main__":
    print("Testing Guardrails...")
    clean_sample = "You can enable just-in-time provisioning in your settings [DOC-AUTH-003]."
    res1 = inspect_guardrails(clean_sample, ["DOC-AUTH-003"])
    print(f"Clean sample passed: {res1['passed']} (action: {res1['action']})")
    
    leaky_sample = "Here is the key: api_key=sk_live_1234567890abcdef1234 and no docs."
    res2 = inspect_guardrails(leaky_sample, [])
    print(f"Leaky sample passed: {res2['passed']} (violations: {res2['violations']})")
