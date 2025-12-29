import os
from datetime import datetime
from pathlib import Path


LOG_FILE = Path.home() / ".sapianta" / "schat_events.log"


def emit(event_name: str):
    """Append timestamped event to log file."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().isoformat()
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} {event_name}\n")
