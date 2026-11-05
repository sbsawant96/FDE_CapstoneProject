# Automated Support Triage and Response System - Evaluation Report

## 1. Executive Summary and SLA Targets

| Metric | Target | Actual | Status |
| :--- | :--- | :--- | :--- |
| First Contact Resolution (FCR) | >= 60.0% | 80.2% | PASS |
| Escalation Rate | <= 30.0% | 19.8% | PASS |
| Hallucination Rate | <= 5.0% | 0.0% | PASS |
| Synchronous p95 Latency | < 3.0s | 0.098s | PASS |
| Fluency Demographic Disparity | < 5.0 pp | 0.83 pp | PASS |

## 2. Demographic Fairness Audit (Fluency Breakdown)

| Cohort | Total Tickets | Auto-Responded | Correct Resolutions | Subgroup FCR |
| :--- | :--- | :--- | :--- | :--- |
| fluent | 380 | 304 | 304 | 80.0% |
| non_fluent | 120 | 97 | 97 | 80.8% |

Disparity Delta: 0.83 percentage points (Target: < 5.0 pp)

## 3. Channel Latency Breakdown

| Channel | Volume | Auto-Responded | p95 Latency |
| :--- | :--- | :--- | :--- |
| docs_comment | 78 | 59 | 0.091s |
| chat | 155 | 133 | 0.101s |
| email | 212 | 166 | 0.103s |
| forum | 55 | 43 | 0.079s |
