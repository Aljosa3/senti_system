#!/usr/bin/env python3
"""
Administrative Session Info
----------------------------
CLI tool to display current session status.

Usage:
    python session_info.py
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
    print("ADMINISTRATIVE SESSION - STATUS")
    print("=" * 70)
    print()

    info = manager.get_session_info()

    if info["status"] == "NO_SESSION":
        print("Status: No Active Session")
        print()
        print("Start a session with:")
        print("  python senti_os/security/admin_session/start_session.py")
    else:
        print("Status: ACTIVE")
        print()
        print(f"Session ID: {info['session_id']}")
        print(f"Identity: {info['identity']}")
        print(f"Started: {info['start_time']}")
        print(f"Expires: {info['expiry_time']}")
        print(f"Time Remaining: {info['time_remaining']}")
        print()
        print("Authorized Operations:")
        for op in info['authorized_operations']:
            print(f"  • {op}")

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
