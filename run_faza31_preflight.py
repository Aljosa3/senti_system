#!/usr/bin/env python3
"""
FAZA 31 Preflight Simulation Runner
Runs complete FAZA 31 Auto-Build pipeline with preflight spec
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, '/home/pisarna/senti_system')

from senti_core_module.senti_build import build_executor
from senti_core_module.senti_build import build_reporter


def mock_llm_callable(prompt: str) -> str:
    """
    Mock LLM that generates correct output for preflight test.
    In production, this would call real LLM (FAZA 30.95).
    """
    output = """FILE: /home/pisarna/senti_system/senti_sandbox/test_module_a.py
\"\"\"
Test module A - FAZA 31 Preflight
\"\"\"


def hello():
    \"\"\"Return test string.\"\"\"
    return 'A_OK'

FILE: /home/pisarna/senti_system/senti_sandbox/test_module_b.py
\"\"\"
Test module B - FAZA 31 Preflight
\"\"\"


def value():
    \"\"\"Return test value.\"\"\"
    return 123
"""
    return output


def load_contract():
    """Load FA31_LLM_CONTRACT.md content."""
    contract_path = Path('/home/pisarna/senti_system/senti_core_module/senti_llm/FA31_LLM_CONTRACT.md')
    if contract_path.exists():
        return contract_path.read_text()
    return None


def main():
    print("=" * 60)
    print("FAZA 31 PREFLIGHT SIMULATION")
    print("=" * 60)
    print()

    spec_path = Path('/home/pisarna/senti_system/FA31_PRELIGHT_SPEC.json')

    if not spec_path.exists():
        print(f"ERROR: Spec file not found: {spec_path}")
        return 1

    print(f"Loading spec: {spec_path}")
    with open(spec_path, 'r') as f:
        spec_data = json.load(f)

    print(f"Files to generate: {len(spec_data.get('files', []))}")
    for file_entry in spec_data.get('files', []):
        print(f"  - {file_entry.get('path', '')}")
    print()

    contract_text = load_contract()
    if contract_text:
        print(f"Contract loaded: {len(contract_text)} chars")
    else:
        print("Contract: using placeholder")
    print()

    print("Starting FAZA 31 Auto-Build pipeline...")
    print("-" * 60)
    print()

    result = build_executor.build(
        spec=spec_data,
        llm_callable=mock_llm_callable,
        contract_text=contract_text
    )

    print("Build completed.")
    print()
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    print()

    report = result.get('report', {})
    formatted_report = build_reporter.format_report(report)
    print(formatted_report)

    if result['status'] == 'OK':
        print()
        print("=" * 60)
        print("GENERATED FILES PREVIEW")
        print("=" * 60)
        print()

        files = result.get('files', {})
        for path, content in files.items():
            print(f"FILE: {path}")
            print("-" * 60)
            lines = content.split('\n')
            for i, line in enumerate(lines[:20], 1):
                print(f"{i:3d} | {line}")
            if len(lines) > 20:
                print(f"... ({len(lines) - 20} more lines)")
            print()

    if result['status'] == 'OK':
        print("✓ PREFLIGHT SIMULATION: SUCCESS")
        return 0
    else:
        print("✗ PREFLIGHT SIMULATION: FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(main())
