import argparse
import os
import sys
from datetime import datetime

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.evaluate import run_evaluation

def main():
    parser = argparse.ArgumentParser(description="Unattended Support Triage Evaluation Gate")
    parser.add_argument("--input", required=True, help="Input tickets JSON file path")
    parser.add_argument("--output", required=True, help="Output markdown report path")
    parser.add_argument("--workers", type=int, default=4, help="Concurrency worker threads")
    args = parser.parse_args()

    input_path = os.path.abspath(args.input)
    output_path = os.path.abspath(args.output)

    if not os.path.exists(input_path):
        print(f"Error: Dataset not found at {input_path}")
        sys.exit(1)

    print("=" * 65)
    print(" CloudServe Solutions - Automated Evaluation Gate Harness")
    print(f" Timestamp  : {datetime.now().isoformat()}")
    print(f" Input File : {input_path}")
    print(f" Output File: {output_path}")
    print("=" * 65)

    import src.evaluate as ev
    ev.DEV_TICKETS_PATH = input_path
    ev.REPORT_PATH = output_path

    results = ev.run_evaluation(workers=args.workers)
    print("\n[GATE STATUS: COMPLETE]")
    print(f" Processed     : {results['total_tickets']} tickets")
    print(f" FCR Rate      : {results['fcr_rate']}% (Target >= 60.0%)")
    print(f" Escalation    : {results['escalation_rate']}% (Target <= 30.0%)")
    print(f" Fluency Gap   : {results['fluency_disparity']} pp (Target < 5.0 pp)")
    print(f" p95 Latency   : {results['p95_latency']}s (Target < 3.0s)")

if __name__ == "__main__":
    main()
