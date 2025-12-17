#!/usr/bin/env python3
"""
FAZA 59 — Human Confirmation CLI
---------------------------------
Command-line tool to collect human CORE LOCK authorization.

Usage:
    python confirm_lock.py

Interactive process:
1. Present FAZA 58 validation results
2. Present governance context
3. Present lock implications
4. Collect explicit human decision
5. Record decision in immutable audit trail
"""

import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(repo_root))

from senti_os.core.faza59.human_confirmation import HumanConfirmationManager


def main():
    # Create confirmation manager
    manager = HumanConfirmationManager(str(repo_root))

    # Execute confirmation workflow
    try:
        record = manager.execute_confirmation_workflow()

        # Exit with appropriate code
        if record.human_decision == "AUTHORIZED":
            sys.exit(0)
        else:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n")
        print("CORE LOCK authorization CANCELLED by user.")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()
