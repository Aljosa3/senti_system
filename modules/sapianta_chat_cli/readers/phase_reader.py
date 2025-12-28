from pathlib import Path

PHASES_BASE = Path("/home/pisarna/senti_system/docs/phases")

def read_phase(phase_id: str) -> str:
    if not phase_id.startswith("PHASE_"):
        return "ERROR: Invalid phase identifier (Phase 77.0)."

    filename = f"{phase_id}.md"
    phase_path = PHASES_BASE / filename

    if not phase_path.exists():
        return f"ERROR: Phase document '{phase_id}' not found (Phase 77.0)."

    try:
        return phase_path.read_text(encoding="utf-8")
    except Exception:
        return f"ERROR: Unable to read phase document '{phase_id}' (Phase 77.0)."
