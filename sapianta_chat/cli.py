#!/usr/bin/env python3
"""
DEPRECATED ENTRYPOINT — DO NOT USE

This file is intentionally deprecated and blocked.

Sapianta Chat MUST be started via the canonical entrypoint:

    python3 run_sapianta_chat.py

Reason:
- Prevent ambiguous CLI entrypoints
- Enforce advisory-only governance
- Guarantee correct intent detection (Phase I.2)
- Preserve deterministic renderer and mandate pipeline

Status:
- Deprecated since STABLE v1.0
- Execution is intentionally blocked

If you reached this file:
You are using an outdated or incorrect entrypoint.
"""

import sys


def main():
    message = """
❌ DEPRECATED ENTRYPOINT

You attempted to start Sapianta Chat using:
    sapianta_chat/cli.py

This entrypoint is DEPRECATED and BLOCKED.

✅ Correct way to start Sapianta Chat:
    python3 run_sapianta_chat.py

Why this matters:
- Prevents ambiguous execution paths
- Ensures advisory-only behavior
- Enforces governance and intent contracts

Status:
- Sapianta Chat CLI is STABLE v1.0
- This entrypoint is permanently disabled

Please update your workflow.
"""
    print(message.strip())
    sys.exit(1)


if __name__ == "__main__":
    main()
