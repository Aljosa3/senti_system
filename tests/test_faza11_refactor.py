#!/usr/bin/env python3
"""
FAZA 11 Test — AST-based Self-Refactor Engine
"""

from pathlib import Path
from senti_core_module.senti_refactor import RefactorManager, ASTPatchTemplate
from senti_core_module.senti_core.services.event_bus import EventBus

ROOT = Path(__file__).resolve().parents[1]


def test_rename_function():
    """Test renaming a function using AST transformation."""
    test_file = ROOT / "modules" / "processing" / "test_refactor_module.py"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("""
def test():
    return 1
""")

    event_bus = EventBus()
    manager = RefactorManager(ROOT, event_bus)

    patch = ASTPatchTemplate.rename_function("test", "test_new")
    result = manager.apply_refactor(str(test_file.relative_to(ROOT)), patch)

    assert result["status"] == "ok"
    assert "test_new" in test_file.read_text()

    print("[PASS] test_rename_function")


def test_patch_validation():
    """Test that invalid patches are rejected."""
    event_bus = EventBus()
    manager = RefactorManager(ROOT, event_bus)

    # Test invalid action
    try:
        invalid_patch = {"action": "invalid_action"}
        manager.apply_refactor("dummy.py", invalid_patch)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Invalid patch action" in str(e)
        print("[PASS] test_patch_validation - invalid action")

    # Test missing parameters
    try:
        invalid_patch = {"action": "rename_function", "old": "foo"}
        manager.apply_refactor("dummy.py", invalid_patch)
        assert False, "Should have raised ValueError"
    except (ValueError, FileNotFoundError) as e:
        print("[PASS] test_patch_validation - missing parameters")


def test_event_publication():
    """Test that refactor events are published."""
    test_file = ROOT / "modules" / "processing" / "test_event_module.py"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("""
def old_name():
    pass
""")

    event_bus = EventBus()
    manager = RefactorManager(ROOT, event_bus)

    events_received = []

    def capture_event(data):
        events_received.append(data)

    event_bus.subscribe("REFACTOR_APPLIED", capture_event)

    patch = ASTPatchTemplate.rename_function("old_name", "new_name")
    manager.apply_refactor(str(test_file.relative_to(ROOT)), patch)

    assert len(events_received) == 1
    assert events_received[0]["patch"]["action"] == "rename_function"

    print("[PASS] test_event_publication")


def test_suggest_refactor():
    """Test refactor suggestion API (placeholder for FAZA 15)."""
    event_bus = EventBus()
    manager = RefactorManager(ROOT, event_bus)

    result = manager.suggest_refactor("modules/sensors/sensor.py")

    assert result["status"] == "suggestion"
    assert "FAZA 15" in result["message"]

    print("[PASS] test_suggest_refactor")


if __name__ == "__main__":
    print("=" * 60)
    print("FAZA 11 — Self-Refactor Engine Tests")
    print("=" * 60)

    try:
        test_rename_function()
        test_patch_validation()
        test_event_publication()
        test_suggest_refactor()

        print("=" * 60)
        print("All tests passed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()
