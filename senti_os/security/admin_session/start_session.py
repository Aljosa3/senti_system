#!/usr/bin/env python3
"""
Start Administrative Session
-----------------------------
CLI tool to start a time-bound administrative session.

Usage:
    python start_session.py

Interactive process prompts for identity and optionally duration.
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
    print("ADMINISTRATIVE SESSION - START")
    print("=" * 70)
    print()

    # Check for existing session
    existing = manager.get_active_session()
    if existing:
        print(f"⚠️  Active session already exists:")
        print(f"   Identity: {existing.identity}")
        print(f"   Started: {existing.start_time}")
        print(f"   Expires: {existing.expiry_time}")
        print()
        print("End the current session before starting a new one.")
        print("Command: python senti_os/security/admin_session/end_session.py")
        sys.exit(1)

    # Collect identity
    print("Identity Verification:")
    print("Enter your identity (e.g., 'System Architect', 'Jane Smith'):")
    identity = input("> ").strip()

    if not identity:
        print("ERROR: Identity is required.")
        sys.exit(1)

    print()

    # Collect duration (optional)
    print("Session Duration:")
    print("Enter duration in minutes (press Enter for default 30 minutes):")
    duration_input = input("> ").strip()

    if duration_input:
        try:
            duration_minutes = int(duration_input)
            if duration_minutes <= 0 or duration_minutes > 480:  # Max 8 hours
                print("ERROR: Duration must be between 1 and 480 minutes.")
                sys.exit(1)
        except ValueError:
            print("ERROR: Duration must be a number.")
            sys.exit(1)
    else:
        duration_minutes = None  # Use default

    print()

    # Start session
    try:
        session = manager.start_session(identity, duration_minutes)

        print("=" * 70)
        print("✅ ADMINISTRATIVE SESSION STARTED")
        print("=" * 70)
        print()
        print(f"Session ID: {session.session_id}")
        print(f"Identity: {session.identity}")
        print(f"Start Time: {session.start_time}")
        print(f"Expiry Time: {session.expiry_time}")
        print()
        print("Authorized Operations:")
        for op in session.authorized_operations:
            print(f"  • {op}")
        print()
        print("=" * 70)

    except RuntimeError as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
