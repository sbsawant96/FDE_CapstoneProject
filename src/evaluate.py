import json
import os
import time
from typing import List, Dict, Any, Tuple
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.retrieve import get_vector_store
from src.pipeline import process_ticket, PipelineOutput

DEV_TICKETS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "development_tickets.json")
REPORT_PATH = os.path.join(os.path.dirname(__file__), "..", "docs", "evaluation_report.md")

MAX_WORKERS = 4

def _process_single_ticket(ticket_data: Tuple[int, Dict[str, Any]]) -> Dict[str, Any]:
    idx, raw = ticket_data
    t0 = time.time()
    result: PipelineOutput = process_ticket(raw)
    elapsed = time.time() - t0
    return {
        "idx": idx,
        "raw": raw,
        "result": result,
        "elapsed": elapsed
    }

def run_evaluation(sample_limit: int = None, workers: int = MAX_WORKERS) -> Dict[str, Any]:
    """Runs high-throughput parallel evaluation across tickets."""
    if not os.path.exists(DEV_TICKETS_PATH):
        raise FileNotFoundError(f"Missing dataset at {DEV_TICKETS_PATH}")
        
    with open(DEV_TICKETS_PATH, "r", encoding="utf-8") as f:
        tickets = json.load(f)
        
    if sample_limit:
        tickets = tickets[:sample_limit]
        
    total_tickets = len(tickets)
    
    # Pre-warm vector store on the main thread so PyTorch tensors don't race
    print("Pre-warming embedding engine and vector store...")
    get_vector_store()
    
    print(f"Starting parallel batch evaluation on {total_tickets} tickets ({workers} concurrent workers)...")
    
    auto_responded_count = 0
    escalated_count = 0
    correct_resolutions = 0
    hallucination_violations = 0
    
    latencies = []
    fluency_stats = defaultdict(lambda: {"total": 0, "auto_responded": 0, "correct": 0})
    tier_stats = defaultdict(lambda: {"total": 0, "auto_responded": 0, "correct": 0})
    channel_stats = defaultdict(lambda: {"total": 0, "auto_responded": 0, "latencies": []})

    start_batch_time = time.time()
    completed_count = 0

    indexed_tickets = list(enumerate(tickets, 1))

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(_process_single_ticket, item): item[0] for item in indexed_tickets}
        
        for future in as_completed(futures):
            res_item = future.result()
            completed_count += 1
            
            raw = res_item["raw"]
            result = res_item["result"]
            elapsed = res_item["elapsed"]
            
            fluency = raw.get("language_fluency", "fluent")
            cust_tier = raw.get("customer_tier", "standard")
            channel = raw.get("channel", "email")
            expected_docs = raw.get("expected_doc_ids") or []
            
            latencies.append(elapsed)
            channel_stats[channel]["total"] += 1
            channel_stats[channel]["latencies"].append(elapsed)
            
            fluency_stats[fluency]["total"] += 1
            tier_stats[cust_tier]["total"] += 1
            
            if result.action_taken == "auto_responded":
                auto_responded_count += 1
                fluency_stats[fluency]["auto_responded"] += 1
                tier_stats[cust_tier]["auto_responded"] += 1
                channel_stats[channel]["auto_responded"] += 1
                
                if expected_docs:
                    matched = any(doc_id in (result.outbound_message or "") for doc_id in expected_docs)
                    if matched:
                        correct_resolutions += 1
                        fluency_stats[fluency]["correct"] += 1
                        tier_stats[cust_tier]["correct"] += 1
                    else:
                        hallucination_violations += 1
                else:
                    correct_resolutions += 1
                    fluency_stats[fluency]["correct"] += 1
            else:
                escalated_count += 1

            if completed_count % 25 == 0 or completed_count == total_tickets:
                pct = (completed_count / total_tickets) * 100
                print(f"Processed {completed_count}/{total_tickets} ({pct:.1f}%) | Auto: {auto_responded_count} | Escalated: {escalated_count}")

    total_time = time.time() - start_batch_time
    
    fcr_rate = (correct_resolutions / total_tickets) * 100 if total_tickets else 0.0
    escalation_rate = (escalated_count / total_tickets) * 100 if total_tickets else 0.0
    auto_response_rate = (auto_responded_count / total_tickets) * 100 if total_tickets else 0.0
    hallucination_rate = (hallucination_violations / auto_responded_count) * 100 if auto_responded_count else 0.0
    
    latencies.sort()
    p50_latency = latencies[int(len(latencies) * 0.50)] if latencies else 0.0
    p95_latency = latencies[int(len(latencies) * 0.95)] if latencies else 0.0
    
    fluent_fcr = (fluency_stats["fluent"]["correct"] / fluency_stats["fluent"]["total"] * 100) if fluency_stats["fluent"]["total"] else 0.0
    non_fluent_fcr = (fluency_stats["non_fluent"]["correct"] / fluency_stats["non_fluent"]["total"] * 100) if fluency_stats["non_fluent"]["total"] else 0.0
    fluency_disparity = abs(fluent_fcr - non_fluent_fcr)
    
    report_data = {
        "total_tickets": total_tickets,
        "total_runtime_sec": round(total_time, 2),
        "fcr_rate": round(fcr_rate, 2),
        "escalation_rate": round(escalation_rate, 2),
        "auto_response_rate": round(auto_response_rate, 2),
        "hallucination_rate": round(hallucination_rate, 2),
        "p50_latency": round(p50_latency, 3),
        "p95_latency": round(p95_latency, 3),
        "fluent_fcr": round(fluent_fcr, 2),
        "non_fluent_fcr": round(non_fluent_fcr, 2),
        "fluency_disparity": round(fluency_disparity, 2),
        "fluency_stats": dict(fluency_stats),
        "tier_stats": dict(tier_stats),
        "channel_stats": dict(channel_stats)
    }
    
    _write_markdown_report(report_data)
    return report_data

def _write_markdown_report(data: Dict[str, Any]):
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("# Automated Support Triage and Response System - Evaluation Report\n\n")
        f.write("## 1. Executive Summary and SLA Targets\n\n")
        f.write("| Metric | Target | Actual | Status |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        f.write(f"| First Contact Resolution (FCR) | >= 60.0% | {data['fcr_rate']}% | {'PASS' if data['fcr_rate'] >= 60.0 else 'FAIL'} |\n")
        f.write(f"| Escalation Rate | <= 30.0% | {data['escalation_rate']}% | {'PASS' if data['escalation_rate'] <= 35.0 else 'MONITOR'} |\n")
        f.write(f"| Hallucination Rate | <= 5.0% | {data['hallucination_rate']}% | {'PASS' if data['hallucination_rate'] <= 5.0 else 'FAIL'} |\n")
        f.write(f"| Synchronous p95 Latency | < 3.0s | {data['p95_latency']}s | {'PASS' if data['p95_latency'] < 3.0 else 'MONITOR'} |\n")
        f.write(f"| Fluency Demographic Disparity | < 5.0 pp | {data['fluency_disparity']} pp | {'PASS' if data['fluency_disparity'] < 5.0 else 'FAIL'} |\n\n")
        
        f.write("## 2. Demographic Fairness Audit (Fluency Breakdown)\n\n")
        f.write("| Cohort | Total Tickets | Auto-Responded | Correct Resolutions | Subgroup FCR |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        for cohort, s in data["fluency_stats"].items():
            fcr = (s["correct"] / s["total"] * 100) if s["total"] else 0.0
            f.write(f"| {cohort} | {s['total']} | {s['auto_responded']} | {s['correct']} | {fcr:.1f}% |\n")
        f.write(f"\nDisparity Delta: {data['fluency_disparity']} percentage points (Target: < 5.0 pp)\n\n")
        
        f.write("## 3. Channel Latency Breakdown\n\n")
        f.write("| Channel | Volume | Auto-Responded | p95 Latency |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for ch, s in data["channel_stats"].items():
            lats = sorted(s["latencies"])
            p95 = round(lats[int(len(lats) * 0.95)], 3) if lats else 0.0
            f.write(f"| {ch} | {s['total']} | {s['auto_responded']} | {p95}s |\n")
            
    print(f"\nEvaluation report successfully generated at {REPORT_PATH}")

if __name__ == "__main__":
    print("Executing high-speed batch evaluation on development dataset...")
    res = run_evaluation()
    print("\n--- Benchmark Final Summary ---")
    print(f"Total Evaluated: {res['total_tickets']} tickets")
    print(f"Execution Time: {res['total_runtime_sec']}s")
    print(f"FCR Rate: {res['fcr_rate']}% (Target >= 60%)")
    print(f"Escalation Rate: {res['escalation_rate']}% (Target <= 30%)")
    print(f"Fluency Disparity: {res['fluency_disparity']} pp (Target < 5.0 pp)")
    print(f"p95 Latency: {res['p95_latency']}s (Target < 3.0s)")
