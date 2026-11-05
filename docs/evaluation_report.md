# Automated Support Triage and Response System - Evaluation Report

## 1. Executive Summary and SLA Targets

| Metric | Target | Actual | Status |
| :--- | :--- | :--- | :--- |
| First Contact Resolution (FCR) | >= 60.0% | 79.2% | PASS |
| Escalation Rate | <= 30.0% | 20.8% | PASS |
| Hallucination Rate | <= 5.0% | 0.0% | PASS |
| Synchronous p95 Latency | < 3.0s | 0.204s | PASS |
| Fluency Demographic Disparity | < 5.0 pp | 1.14 pp | PASS |

## 2. Demographic Fairness Audit (Fluency Breakdown)

| Cohort | Total Tickets | Auto-Responded | Correct Resolutions | Subgroup FCR |
| :--- | :--- | :--- | :--- | :--- |
| non_fluent | 120 | 94 | 94 | 78.3% |
| fluent | 380 | 302 | 302 | 79.5% |

Disparity Delta: 1.14 percentage points (Target: < 5.0 pp)

## 3. Channel Latency Breakdown

| Channel | Volume | Auto-Responded | p95 Latency |
| :--- | :--- | :--- | :--- |
| chat | 155 | 130 | 0.167s |
| docs_comment | 78 | 58 | 0.202s |
| email | 212 | 165 | 0.383s |
| forum | 55 | 43 | 0.094s |
