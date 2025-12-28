from pathlib import Path

MPD_BASE = Path("/home/pisarna/senti_system/docs/modules/mpd")

def read_mpd(module_id: str) -> str:
    if not module_id:
        return "ERROR: Module ID required to read MPD (Phase 77.0)."

    filename = f"{module_id}_MPD.md"
    mpd_path = MPD_BASE / filename

    if not mpd_path.exists():
        return f"ERROR: MPD not found for module '{module_id}' (Phase 77.0)."

    try:
        return mpd_path.read_text(encoding="utf-8")
    except Exception:
        return f"ERROR: Unable to read MPD for module '{module_id}' (Phase 77.0)."
