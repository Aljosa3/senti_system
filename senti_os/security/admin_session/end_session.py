#!/usr/bin/env python3
"""
End Administrative Session
---------------------------
CLI tool to end the current administrative session.

Usage:
    python end_session.py
"""

import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(repo_root))

from senti_os.security.admin_session.session_manager import get_session_manager


def main():
    manager = get_session_manager(str(repo_root))

    print("=" * 70)
    print("ADMINISTRATIVE SESSION - END")
    print("=" * 70)
    print()

    # Check for active session
    session = manager.get_active_session()
    if not session:
        print("No active administrative session to end.")
        sys.exit(0)

    print(f"Active Session:")
    print(f"  Session ID: {session.session_id}")
    print(f"  Identity: {session.identity}")
    print(f"  Started: {session.start_time}")
    print()

    # End session
    try:
        manager.end_session()

        print("=" * 70)
        print("✅ ADMINISTRATIVE SESSION ENDED")
        print("=" * 70)
        print()

    except RuntimeError as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
