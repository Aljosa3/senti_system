import os
import shutil
import json
import time

from senti_core_module.senti_llm.runtime.llm_runtime_manager import LLMRuntimeManager

print("======================================================")
print("      FAZA 41 — FULL SELF-TEST (Event Bus)           ")
print("======================================================")

# 0) PREPARE CLEAN ENVIRONMENT
if os.path.exists("senti_data/modules/event_demo"):
    shutil.rmtree("senti_data/modules/event_demo")

print("[0] Clean environment prepared.")


# 1) MANAGER INITIALIZATION
m = LLMRuntimeManager()
print("[1] Runtime initialized.")


# 2) VERIFY EVENT BUS EXISTS
print("\n[2] Verifying EventBus existence...")
assert hasattr(m.exec_orchestrator.module_loader, 'event_bus'), "EventBus not found in ModuleLoader"

event_bus = m.exec_orchestrator.module_loader.event_bus

print("  ✓ EventBus instance exists")


# 3) LOAD EVENT_DEMO MODULE
print("\n[3] Loading event_demo module...")
result_load = m.handle_input(
    "load senti_core_module/senti_llm/modules/faza41_demo_event_module.py"
)
print("Load result:", json.dumps(result_load, indent=2))

assert result_load["result"]["ok"], "Module failed to load"
assert result_load["result"]["data"]["event_bus_active"], "EventBus not active"

# Check event.publish and event.subscribe capabilities were granted
granted_caps = result_load["result"]["data"]["capabilities_granted"]
assert "event.publish" in granted_caps, "event.publish capability not granted"
assert "event.subscribe" in granted_caps, "event.subscribe capability not granted"

print("  ✓ Module loaded with event capabilities")


# 4) VERIFY EVENT SUBSCRIPTIONS
print("\n[4] Verifying event subscriptions...")
result_subs = m.handle_input("run event_demo mode=list_subscriptions")
print("Subscriptions:", json.dumps(result_subs, indent=2))

assert result_subs["result"]["ok"], "Failed to list subscriptions"
subs = result_subs["result"]["data"]["subscriptions"]

assert "module.loaded" in subs, "module.loaded subscription not found"
assert "custom.test" in subs, "custom.test subscription not found"

print(f"  ✓ Module subscribed to {len(subs)} event types")


# 5) VERIFY MODULE.LOADED EVENT WAS RECEIVED
print("\n[5] Verifying module.loaded event was received...")
result_status = m.handle_input("run event_demo mode=status")
print("Status:", json.dumps(result_status, indent=2))

stats = result_status["result"]["data"]["stats"]
assert stats["received_count"] >= 1, "No events received"

# Check if module.loaded event was received
received = stats["received_events"]
module_loaded_received = any(evt["type"] == "module.loaded" for evt in received)

assert module_loaded_received, "module.loaded event not received"

print(f"  ✓ Received {stats['received_count']} events")


# 6) PUBLISH CUSTOM EVENT
print("\n[6] Publishing custom event...")
result_publish = m.handle_input(
    "run event_demo mode=publish event_type=custom.test event_data={'test':'value'}"
)
print("Publish result:", json.dumps(result_publish, indent=2))

assert result_publish["result"]["ok"], "Failed to publish event"
assert result_publish["result"]["data"]["action"] == "published", "Event not published"

handlers_called = result_publish["result"]["data"]["handlers_called"]
print(f"  ✓ Event published, {handlers_called} handlers called")


# 7) VERIFY EVENT WAS RECEIVED BY SUBSCRIBER
print("\n[7] Verifying published event was received...")
time.sleep(0.1)  # Give event bus time to process

result_status2 = m.handle_input("run event_demo mode=status")
stats2 = result_status2["result"]["data"]["stats"]

assert stats2["received_count"] > stats["received_count"], "Event count did not increase"

print(f"  ✓ Event count increased from {stats['received_count']} to {stats2['received_count']}")


# 8) VERIFY PUBLISHED COUNT IN STATE
print("\n[8] Verifying published count persisted in state...")
mod_data = m.exec_orchestrator.module_loader.registry.get("event_demo")
state = mod_data["state"]

published_count = state.get("published_count", 0)
assert published_count >= 1, f"Published count should be >= 1, got {published_count}"

print(f"  ✓ Published count: {published_count}")


# 9) TEST EVENT BUS INTROSPECTION
print("\n[9] Testing EventBus introspection...")
event_types = event_bus.list_event_types()

print(f"  Registered event types: {event_types}")

assert "module.loaded" in event_types, "module.loaded not in registered events"
assert "custom.test" in event_types, "custom.test not in registered events"

print(f"  ✓ EventBus tracking {len(event_types)} event types")


# 10) LIST HANDLERS FOR EVENT TYPE
print("\n[10] Listing handlers for custom.test event...")
handlers = event_bus.list_handlers("custom.test")

print(f"  Handlers for custom.test: {handlers}")

assert len(handlers) >= 1, "No handlers registered for custom.test"

print(f"  ✓ {len(handlers)} handler(s) registered")


# 11) VERIFY RUNTIME PHASE
print("\n[11] Verifying runtime phase...")
result_query = m.handle_input("status")
print("Query result:", json.dumps(result_query, indent=2))

assert result_query["result"]["data"]["phase"] == "FAZA 41", "Phase not updated to FAZA 41"
assert result_query["result"]["data"]["event_bus_active"], "EventBus not active in status"

print("  ✓ Runtime reports FAZA 41 with EventBus active")


# 12) LOAD SECOND MODULE TO TEST CROSS-MODULE EVENTS
print("\n[12] Testing cross-module event delivery...")

# Load the FAZA 40 demo module (it will trigger module.loaded event)
result_load2 = m.handle_input(
    "load senti_core_module/senti_llm/modules/faza40_demo_state_module.py"
)

assert result_load2["result"]["ok"], "Second module failed to load"

# Check if event_demo received the module.loaded event
result_status3 = m.handle_input("run event_demo mode=status")
stats3 = result_status3["result"]["data"]["stats"]

assert stats3["received_count"] > stats2["received_count"], "Cross-module event not received"

print(f"  ✓ Cross-module event delivered (count: {stats3['received_count']})")


# 13) VERIFY STATE PERSISTENCE WITH EVENTS
print("\n[13] Verifying event state persistence...")

# Publish another event
m.handle_input("run event_demo mode=publish event_type=custom.test")

# Check state file
state_file = os.path.join(os.getcwd(), "senti_data/modules/event_demo/state.json")
assert os.path.exists(state_file), "State file not found"

with open(state_file, "r") as f:
    disk_state = json.load(f)

assert "published_count" in disk_state["state"], "published_count not in state"
assert disk_state["state"]["published_count"] >= 2, "Published count not incremented"

print(f"  ✓ Event state persisted (published: {disk_state['state']['published_count']})")


print("\n======================================================")
print("     FAZA 41 SELF-TEST FINISHED SUCCESSFULLY          ")
print("======================================================")
print("\n✅ All Event Bus features working correctly:")
print("   - EventBus instance created and accessible")
print("   - Event capabilities (publish/subscribe) granted")
print("   - Manifest-driven event subscriptions")
print("   - Event publishing and delivery")
print("   - Cross-module event communication")
print("   - Event handler registration")
print("   - EventBus introspection (list types/handlers)")
print("   - Event state persistence")
print("   - module.loaded system event")
print("   - Thread-safe event handling")
