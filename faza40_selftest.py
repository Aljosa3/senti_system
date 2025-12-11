import os
import shutil
import json
import time

from senti_core_module.senti_llm.runtime.llm_runtime_manager import LLMRuntimeManager

print("======================================================")
print("      FAZA 40 — FULL SELF-TEST (Persistent State)    ")
print("======================================================")

# 0) PREPARE CLEAN ENVIRONMENT
if os.path.exists("senti_data/modules/demo_state"):
    shutil.rmtree("senti_data/modules/demo_state")

print("[0] Clean environment prepared.")


# 1) MANAGER INITIALIZATION
m = LLMRuntimeManager()
print("[1] Runtime initialized.")


# 2) LIST BEFORE LOAD
print("\n[2] List before load:", m.handle_input("list"))


# 3) LOAD DEMO_STATE MODULE
print("\n[3] Loading demo_state module...")
result_load = m.handle_input(
    "load senti_core_module/senti_llm/modules/faza40_demo_state_module.py"
)
print("Load result:", json.dumps(result_load, indent=2))

assert result_load["result"]["ok"], "Module failed to load"
assert result_load["result"]["data"]["state_initialized"], "State not initialized"

print("  ✓ Module loaded with state initialized")


# 4) VERIFY INITIAL STATE
print("\n[4] Verifying initial state...")
mod_data = m.exec_orchestrator.module_loader.registry.get("demo_state")
state = mod_data["state"]

initial_counter = state.get("counter")
print(f"  Initial counter: {initial_counter}")

assert initial_counter == 0, f"Initial counter should be 0, got {initial_counter}"

print("  ✓ Initial state correct (counter=0)")


# 5) RUN MODULE FIRST TIME
print("\n[5] Running module first time...")
result_run1 = m.handle_input("run demo_state mode=normal")
print("Run 1 result:", json.dumps(result_run1, indent=2))

assert result_run1["result"]["ok"], "First run failed"
state_after_1 = result_run1["result"]["data"]["state"]

assert state_after_1["counter"] == 1, f"Counter should be 1, got {state_after_1['counter']}"
assert len(state_after_1["messages"]) == 1, f"Should have 1 message, got {len(state_after_1['messages'])}"

print(f"  ✓ After run 1: counter={state_after_1['counter']}, messages={len(state_after_1['messages'])}")


# 6) RUN MODULE SECOND TIME
print("\n[6] Running module second time...")
result_run2 = m.handle_input("run demo_state mode=normal")
print("Run 2 result:", json.dumps(result_run2, indent=2))

assert result_run2["result"]["ok"], "Second run failed"
state_after_2 = result_run2["result"]["data"]["state"]

assert state_after_2["counter"] == 2, f"Counter should be 2, got {state_after_2['counter']}"
assert len(state_after_2["messages"]) == 2, f"Should have 2 messages, got {len(state_after_2['messages'])}"

print(f"  ✓ After run 2: counter={state_after_2['counter']}, messages={len(state_after_2['messages'])}")


# 7) RUN MODULE THIRD TIME
print("\n[7] Running module third time...")
result_run3 = m.handle_input("run demo_state mode=normal")

state_after_3 = result_run3["result"]["data"]["state"]
assert state_after_3["counter"] == 3, f"Counter should be 3, got {state_after_3['counter']}"

print(f"  ✓ After run 3: counter={state_after_3['counter']}")


# 8) VERIFY STATE.JSON FILE EXISTS
print("\n[8] Verifying state.json file exists...")
state_file_path = os.path.join(os.getcwd(), "senti_data/modules/demo_state/state.json")
print(f"  Checking: {state_file_path}")

assert os.path.exists(state_file_path), f"State file not found at: {state_file_path}"

print("  ✓ state.json file exists")


# 9) VERIFY STATE.JSON CONTENT
print("\n[9] Verifying state.json content...")
with open(state_file_path, "r") as f:
    disk_state = json.load(f)

print("  Disk state structure:", json.dumps(disk_state, indent=2))

assert "state" in disk_state, "state.json missing 'state' key"
assert disk_state["state"]["counter"] == 3, f"Disk counter should be 3, got {disk_state['state']['counter']}"

print("  ✓ state.json content verified (counter=3 on disk)")


# 10) TEST STATE PERSISTENCE ACROSS RELOAD
print("\n[10] Testing state persistence across reload...")

# Simulate reload by creating a new manager and reloading module
m2 = LLMRuntimeManager()
result_load2 = m2.handle_input(
    "load senti_core_module/senti_llm/modules/faza40_demo_state_module.py"
)

assert result_load2["result"]["ok"], "Module reload failed"

# Check if state was preserved
mod_data2 = m2.exec_orchestrator.module_loader.registry.get("demo_state")
state2 = mod_data2["state"]

reloaded_counter = state2.get("counter")
print(f"  Reloaded counter: {reloaded_counter}")

assert reloaded_counter == 3, f"Reloaded counter should be 3, got {reloaded_counter}"

print("  ✓ State persisted across reload (counter=3)")


# 11) RUN AFTER RELOAD
print("\n[11] Running module after reload...")
result_run4 = m2.handle_input("run demo_state mode=normal")

state_after_4 = result_run4["result"]["data"]["state"]
assert state_after_4["counter"] == 4, f"Counter should be 4 after reload, got {state_after_4['counter']}"

print(f"  ✓ Counter incremented correctly after reload: {state_after_4['counter']}")


# 12) TEST ERROR HANDLING WITH STATE
print("\n[12] Testing error handling with state...")
result_error = m2.handle_input("run demo_state mode=error")

print("Error result:", json.dumps(result_error, indent=2))

# Should fail but state should be saved
assert not result_error["result"]["ok"], "Error mode should have failed"

# Check error_count was incremented
result_status = m2.handle_input("run demo_state mode=status")
status_state = result_status["result"]["data"]["state"]

assert status_state["error_count"] >= 1, f"error_count should be >= 1, got {status_state['error_count']}"

print(f"  ✓ on_error() hook incremented error_count: {status_state['error_count']}")


# 13) TEST STATE RESET
print("\n[13] Testing state reset...")
result_reset = m2.handle_input("run demo_state mode=reset")

reset_state = result_reset["result"]["data"]["state"]
print("Reset state:", json.dumps(reset_state, indent=2))

# Counter should be reset to 0 after save
# Note: reset sets state but orchestrator saves it
# Let's check after another run
result_after_reset = m2.handle_input("run demo_state mode=status")
status_after_reset = result_after_reset["result"]["data"]["state"]

assert status_after_reset["counter"] == 0, f"Counter should be 0 after reset, got {status_after_reset['counter']}"

print("  ✓ State reset successful (counter=0)")


# 14) VERIFY RUNTIME PHASE
print("\n[14] Verifying runtime phase...")
result_query = m2.handle_input("status")
print("Query result:", json.dumps(result_query, indent=2))

assert result_query["result"]["data"]["phase"] == "FAZA 40", "Phase not updated to FAZA 40"

print("  ✓ Runtime reports FAZA 40")


# 15) TEST STATE CORRUPTION RESILIENCE
print("\n[15] Testing state corruption resilience...")

# Corrupt the state.json file
with open(state_file_path, "w") as f:
    f.write("CORRUPTED JSON{{{")

# Create new manager and try to load
m3 = LLMRuntimeManager()
result_load3 = m3.handle_input(
    "load senti_core_module/senti_llm/modules/faza40_demo_state_module.py"
)

# Module should still load (falling back to default state)
assert result_load3["result"]["ok"], "Module failed to load after corruption"

# Check state was reset to defaults
mod_data3 = m3.exec_orchestrator.module_loader.registry.get("demo_state")
state3 = mod_data3["state"]

corrupted_counter = state3.get("counter")
print(f"  Counter after corruption recovery: {corrupted_counter}")

assert corrupted_counter == 0, f"Counter should be 0 (default) after corruption, got {corrupted_counter}"

print("  ✓ Corrupted state.json handled gracefully (fallback to defaults)")


print("\n======================================================")
print("     FAZA 40 SELF-TEST FINISHED SUCCESSFULLY          ")
print("======================================================")
print("\n✅ All persistent state features working correctly:")
print("   - State initialization from default_state")
print("   - State persistence across runs")
print("   - State persistence across module reloads")
print("   - Automatic state refresh before execution")
print("   - Automatic state save after execution")
print("   - State save on error")
print("   - State reset functionality")
print("   - Corruption recovery (fallback to defaults)")
print("   - Integration with lifecycle hooks")
