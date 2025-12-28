from pathlib import Path

REGISTRY_PATH = Path("/home/pisarna/senti_system/docs/modules/REGISTRY.md")

def read_registry(module_id: str = None) -> str:
    if not REGISTRY_PATH.exists():
        return "ERROR: REGISTRY.md not found (Phase 77.0)."

    try:
        return REGISTRY_PATH.read_text(encoding="utf-8")
    except Exception:
        return "ERROR: Unable to read REGISTRY.md (Phase 77.0)."
