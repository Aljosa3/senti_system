import os
import shutil
import json
import time

from senti_core_module.senti_llm.runtime.llm_runtime_manager import LLMRuntimeManager

print("======================================================")
print("      FAZA 42 — FULL SELF-TEST (Reactive Modules)    ")
print("======================================================")

# 0) PREPARE CLEAN ENVIRONMENT
if os.path.exists("senti_data/modules/reactive_demo"):
    shutil.rmtree("senti_data/modules/reactive_demo")

print("[0] Clean environment prepared.")


# 1) MANAGER INITIALIZATION
m = LLMRuntimeManager()
print("[1] Runtime initialized.")


# 2) VERIFY RUNTIME PHASE
print("\n[2] Verifying runtime phase...")
result_phase = m.handle_input("status")
print("Phase check:", json.dumps(result_phase, indent=2))

assert result_phase["result"]["data"]["phase"] == "FAZA 42", "Phase not FAZA 42"
print("  ✓ Runtime reports FAZA 42")


# 3) LOAD REACTIVE DEMO MODULE
print("\n[3] Loading reactive_demo module...")
result_load = m.handle_input(
    "load senti_core_module/senti_llm/modules/faza42_demo_reactive_module.py"
)
print("Load result:", json.dumps(result_load, indent=2))

assert result_load["result"]["ok"], "Module failed to load"
assert result_load["result"]["data"]["event_bus_active"], "EventBus not active"

# FAZA 42: Check reactive_handlers_registered
reactive_count = result_load["result"]["data"]["reactive_handlers_registered"]
assert reactive_count > 0, "No reactive handlers registered"

print(f"  ✓ Module loaded with {reactive_count} reactive handlers")


# 4) VERIFY REACTIVE HANDLERS IN MANIFEST
print("\n[4] Verifying reactive handlers in manifest...")
result_handlers = m.handle_input("run reactive_demo mode=list_handlers")
print("Handlers:", json.dumps(result_handlers, indent=2))

assert result_handlers["result"]["ok"], "Failed to list handlers"
handlers = result_handlers["result"]["data"]["reactive_handlers"]

assert "module.loaded" in handlers, "module.loaded handler not found"
assert "custom.test" in handlers, "custom.test handler not found"
assert "reactive.ping" in handlers, "reactive.ping handler not found"
assert "reactive.chain" in handlers, "reactive.chain handler not found"

print(f"  ✓ {len(handlers)} reactive handlers declared in manifest")


# 5) VERIFY MODULE.LOADED EVENT WAS RECEIVED
print("\n[5] Verifying module.loaded event was received by reactive handler...")
time.sleep(0.1)  # Give handlers time to process

result_status = m.handle_input("run reactive_demo mode=status")
print("Status:", json.dumps(result_status, indent=2))

stats = result_status["result"]["data"]["stats"]
assert stats["total_events_handled"] >= 1, "No events handled by reactive handlers"
assert stats["module_loaded_count"] >= 1, "module.loaded event not received"

print(f"  ✓ Reactive handler received {stats['total_events_handled']} events")


# 6) TEST MANUAL EVENT PUBLISHING (triggering reactive handlers)
print("\n[6] Publishing custom.test event to trigger reactive handler...")
result_publish = m.handle_input(
    "run reactive_demo mode=publish event_type=custom.test event_data={'test':'reactive'}"
)
print("Publish result:", json.dumps(result_publish, indent=2))

assert result_publish["result"]["ok"], "Failed to publish event"
assert result_publish["result"]["data"]["action"] == "published", "Event not published"

time.sleep(0.1)

# Check stats increased
result_status2 = m.handle_input("run reactive_demo mode=status")
stats2 = result_status2["result"]["data"]["stats"]

assert stats2["custom_event_count"] >= 1, "custom.test reactive handler not triggered"
assert stats2["total_events_handled"] > stats["total_events_handled"], "Event count did not increase"

print(f"  ✓ Reactive handler triggered (custom_event_count: {stats2['custom_event_count']})")


# 7) TEST PING/PONG PATTERN
print("\n[7] Testing ping/pong reactive pattern...")
result_ping = m.handle_input("run reactive_demo mode=trigger_ping")
print("Ping result:", json.dumps(result_ping, indent=2))

assert result_ping["result"]["ok"], "Failed to trigger ping"
assert result_ping["result"]["data"]["action"] == "triggered_ping", "Ping not triggered"

time.sleep(0.1)

result_status3 = m.handle_input("run reactive_demo mode=status")
stats3 = result_status3["result"]["data"]["stats"]

assert stats3["total_events_handled"] > stats2["total_events_handled"], "Ping handler not called"

print("  ✓ Ping/pong pattern works")


# 8) TEST EVENT CHAINING
print("\n[8] Testing event chaining with reactive handlers...")
result_chain = m.handle_input("run reactive_demo mode=trigger_chain level=0")
print("Chain result:", json.dumps(result_chain, indent=2))

assert result_chain["result"]["ok"], "Failed to trigger chain"
assert result_chain["result"]["data"]["action"] == "triggered_chain", "Chain not triggered"

chain_calls = result_chain["result"]["data"]["total_chain_calls"]
assert chain_calls >= 3, f"Chain should propagate at least 3 times, got {chain_calls}"

print(f"  ✓ Event chain propagated {chain_calls} times")


# 9) VERIFY STATE PERSISTENCE WITH REACTIVE HANDLERS
print("\n[9] Verifying state persistence with reactive handlers...")

# Trigger more events
m.handle_input("run reactive_demo mode=publish event_type=custom.test")
time.sleep(0.1)

# Check state file
state_file = os.path.join(os.getcwd(), "senti_data/modules/reactive_demo/state.json")
assert os.path.exists(state_file), "State file not found"

with open(state_file, "r") as f:
    disk_state = json.load(f)

assert "events_handled" in disk_state["state"], "events_handled not in state"
assert disk_state["state"]["events_handled"] > 0, "Event count not persisted"

print(f"  ✓ State persisted (events_handled: {disk_state['state']['events_handled']})")


# 10) VERIFY EventBus INTROSPECTION
print("\n[10] Testing EventBus introspection for reactive handlers...")
event_bus = m.exec_orchestrator.module_loader.event_bus

event_types = event_bus.list_event_types()
print(f"  Registered event types: {event_types}")

assert "module.loaded" in event_types, "module.loaded not in event types"
assert "custom.test" in event_types, "custom.test not in event types"
assert "reactive.ping" in event_types, "reactive.ping not in event types"
assert "reactive.chain" in event_types, "reactive.chain not in event types"

# Check handler count for custom.test
handlers_custom = event_bus.list_handlers("custom.test")
print(f"  Handlers for custom.test: {len(handlers_custom)}")

# Should have at least 1 handler (from reactive_demo)
assert len(handlers_custom) >= 1, "No handlers for custom.test"

print(f"  ✓ EventBus tracking {len(event_types)} event types")


# 11) TEST CROSS-MODULE REACTIVE HANDLERS
print("\n[11] Testing cross-module event delivery to reactive handlers...")

# Load FAZA 41 event demo module (it manually subscribes to module.loaded)
result_load2 = m.handle_input(
    "load senti_core_module/senti_llm/modules/faza41_demo_event_module.py"
)

assert result_load2["result"]["ok"], "Second module failed to load"

time.sleep(0.1)

# Check if reactive_demo received the module.loaded event
result_status4 = m.handle_input("run reactive_demo mode=status")
stats4 = result_status4["result"]["data"]["stats"]

assert stats4["module_loaded_count"] > stats3["module_loaded_count"], \
    "Reactive handler didn't receive cross-module event"

print(f"  ✓ Cross-module event delivered to reactive handler")


# 12) VERIFY BACKWARDS COMPATIBILITY
print("\n[12] Verifying backwards compatibility with FAZA 40/41 modules...")

# FAZA 41 module (manual subscriptions) should still work
result_faza41 = m.handle_input("run event_demo mode=status")
assert result_faza41["result"]["ok"], "FAZA 41 module not working"

# FAZA 40 module should also work
result_load3 = m.handle_input(
    "load senti_core_module/senti_llm/modules/faza40_demo_state_module.py"
)
assert result_load3["result"]["ok"], "FAZA 40 module failed to load"

result_faza40 = m.handle_input("run state_demo mode=read key=counter")
assert result_faza40["result"]["ok"], "FAZA 40 module not working"

print("  ✓ Backwards compatibility maintained (FAZA 40/41 modules work)")


# 13) TEST REACTIVE HANDLER VALIDATION
print("\n[13] Testing reactive handler validation...")

# Create temporary invalid module
invalid_module_path = "senti_data/test_invalid_reactive.py"
with open(invalid_module_path, "w") as f:
    f.write("""
MODULE_MANIFEST = {
    "name": "invalid_reactive",
    "version": "1.0.0",
    "phase": 42,
    "entrypoint": "InvalidModule",
    "capabilities": {"requires": ["module.run"]},
    "reactive": {
        "enabled": True,
        "handlers": {
            "test.event": "missing_handler"
        }
    }
}

class InvalidModule:
    def __init__(self, context, capabilities, state):
        pass

    def run(self, payload):
        return {"ok": True}
""")

# Try to load invalid module
result_invalid = m.handle_input(f"load {invalid_module_path}")
print("Invalid module result:", json.dumps(result_invalid, indent=2))

# Should fail validation (check data.ok, not result.ok)
assert not result_invalid["result"]["data"]["ok"], "Invalid module should not load"
assert "Reactive handler" in result_invalid["result"]["data"]["error"] or \
       "missing_handler" in result_invalid["result"]["data"]["error"], \
       "Should fail with reactive handler validation error"

# Cleanup
os.remove(invalid_module_path)

print("  ✓ Reactive handler validation working correctly")


# 14) FINAL STATUS CHECK
print("\n[14] Final status check...")
result_final = m.handle_input("status")

assert result_final["result"]["data"]["phase"] == "FAZA 42", "Phase changed unexpectedly"
assert result_final["result"]["data"]["event_bus_active"], "EventBus not active"

loaded_count = result_final["result"]["data"]["module_count"]
print(f"  Loaded modules: {loaded_count}")
print(f"  Modules: {result_final['result']['data']['loaded_modules']}")

assert loaded_count >= 3, f"Expected at least 3 modules, got {loaded_count}"

print("  ✓ Final status OK")


print("\n======================================================")
print("     FAZA 42 SELF-TEST FINISHED SUCCESSFULLY          ")
print("======================================================")
print("\n✅ All Reactive Module features working correctly:")
print("   - Runtime phase updated to FAZA 42")
print("   - Reactive handler validation")
print("   - Automatic handler registration from manifest")
print("   - Declarative event-to-method mapping")
print("   - Reactive handlers receiving events")
print("   - State updates in reactive handlers")
print("   - Event chaining with reactive handlers")
print("   - Ping/pong reactive patterns")
print("   - Cross-module reactive event delivery")
print("   - EventBus introspection for reactive handlers")
print("   - State persistence with reactive modules")
print("   - Backwards compatibility with FAZA 40/41")
print("   - Invalid reactive handler detection")
print("\n🎯 FAZA 42 implementation complete and verified!")
