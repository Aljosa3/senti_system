#!/usr/bin/env python3
"""
FAZA 58 — Integrity Audit CLI
------------------------------
Command-line tool to execute FAZA 58 integrity audit.

Usage:
    python run_audit.py [--create-baseline] [--output-json]

Options:
    --create-baseline: Create baseline if none exists
    --output-json: Output report as JSON instead of human-readable text
"""

import argparse
import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(repo_root))

from senti_os.core.faza58.integrity_audit import IntegrityAuditor


def main():
    parser = argparse.ArgumentParser(
        description="FAZA 58 - Integrity Audit & Pre-Lock Validation"
    )
    parser.add_argument(
        "--create-baseline",
        action="store_true",
        help="Create baseline if none exists"
    )
    parser.add_argument(
        "--output-json",
        action="store_true",
        help="Output report as JSON"
    )
    parser.add_argument(
        "--repo-root",
        type=str,
        default=str(repo_root),
        help="Path to repository root"
    )

    args = parser.parse_args()

    # Create auditor
    auditor = IntegrityAuditor(args.repo_root)

    # Perform audit
    print("=" * 70, file=sys.stderr)
    print("FAZA 58 — Integrity Audit Starting...", file=sys.stderr)
    print("=" * 70, file=sys.stderr)
    print("", file=sys.stderr)

    report = auditor.perform_audit(create_baseline=args.create_baseline)

    # Output report
    if args.output_json:
        print(report.to_json())
    else:
        print(auditor.generate_human_readable_report(report))

    # Exit with appropriate code
    if report.overall_status == "READY":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
