"""
Sapianta Chat Audit Logger

Minimal, append-only audit logging.
No semantics. No interpretation.
"""

import os
from datetime import datetime

AUDIT_LOG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "logs",
    "sapianta_chat_audit.log",
)


def log_event(event_type, response_id, channel="cli"):
    timestamp = datetime.utcnow().isoformat(timespec="seconds") + "Z"

    line = f"{timestamp} | {channel} | {event_type} | {response_id}\n"

    os.makedirs(os.path.dirname(AUDIT_LOG_PATH), exist_ok=True)

    with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line)
