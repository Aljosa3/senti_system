import os
import shutil
import json

from senti_core_module.senti_llm.runtime.llm_runtime_manager import LLMRuntimeManager

print("======================================================")
print("      FAZA 39 — FULL SELF-TEST (Lifecycle Hooks)     ")
print("======================================================")

# 0) PREPARE CLEAN ENVIRONMENT
if os.path.exists("senti_data/modules/lifecycle_demo"):
    shutil.rmtree("senti_data/modules/lifecycle_demo")

print("[0] Clean environment prepared.")


# 1) MANAGER INITIALIZATION
m = LLMRuntimeManager()
print("[1] Runtime initialized.")


# 2) LIST BEFORE LOAD
print("[2] List before load:", m.handle_input("list"))


# 3) LOAD LIFECYCLE DEMO MODULE
print("\n[3] Loading lifecycle_demo module...")
result_load = m.handle_input(
    "load senti_core_module/senti_llm/modules/faza39_demo_module.py"
)
print("Load result:", json.dumps(result_load, indent=2))

assert result_load["result"]["ok"], "Module failed to load"
assert "hooks_enabled" in result_load["result"]["data"], "hooks_enabled not in response"

hooks_enabled = result_load["result"]["data"]["hooks_enabled"]
print(f"  → Hooks enabled: {hooks_enabled}")

assert "init" in hooks_enabled, "init hook not enabled"
assert "pre_run" in hooks_enabled, "pre_run hook not enabled"
assert "post_run" in hooks_enabled, "post_run hook not enabled"
assert "on_error" in hooks_enabled, "on_error hook not enabled"

print("  ✓ All hooks enabled correctly")


# 4) VERIFY INIT() WAS CALLED
print("\n[4] Verifying init() was called during load...")
mod_data = m.exec_orchestrator.module_loader.registry.get("lifecycle_demo")
instance = mod_data["instance"]

assert instance.init_called, "init() was not called during module load"
print("  ✓ init() hook executed during load")


# 5) RUN MODULE IN NORMAL MODE
print("\n[5] Running module in normal mode...")
result_run = m.handle_input("run lifecycle_demo mode=normal")
print("Run result:", json.dumps(result_run, indent=2))

assert result_run["result"]["ok"], "Normal run failed"
assert result_run["result"]["data"]["ok"], "Module returned ok=False"
assert result_run["result"]["data"]["hooks_working"], "Hooks not working"

# Check that pre_run and post_run were called
assert instance.pre_run_called, "pre_run() was not called"
assert instance.post_run_called, "post_run() was not called"

print("  ✓ pre_run() and post_run() hooks executed")


# 6) CHECK LIFECYCLE STATUS
print("\n[6] Checking lifecycle status...")
result_status = m.handle_input("run lifecycle_demo mode=status")
print("Status result:", json.dumps(result_status, indent=2))

status = result_status["result"]["data"]["lifecycle_status"]
assert status["init_called"], "init not recorded"
assert status["pre_run_called"], "pre_run not recorded"
assert status["post_run_called"], "post_run not recorded"

print("  ✓ Lifecycle status confirmed")


# 7) TEST ON_ERROR HOOK
print("\n[7] Testing on_error hook...")
result_error = m.handle_input("run lifecycle_demo mode=error")
print("Error result:", json.dumps(result_error, indent=2))

# Should fail but on_error hook should have been called
assert not result_error["result"]["ok"], "Error mode should have failed"
assert "error" in result_error["result"], "Error message missing"

# Check that on_error was called
assert instance.on_error_called, "on_error() was not called"

print("  ✓ on_error() hook executed on exception")


# 8) VERIFY LIFECYCLE STAGE TRACKING
print("\n[8] Verifying lifecycle stage tracking...")
context = m.exec_orchestrator.context

# After execution completes, should be back to idle
current_stage = context.get_stage()
print(f"  Current stage: {current_stage}")

assert current_stage == "idle", f"Stage should be 'idle' but is '{current_stage}'"

print("  ✓ Lifecycle stage tracking working")


# 9) CHECK QUERY STATUS (FAZA 39)
print("\n[9] Checking runtime status...")
result_query = m.handle_input("status")
print("Query result:", json.dumps(result_query, indent=2))

assert result_query["result"]["data"]["phase"] == "FAZA 39", "Phase not updated to FAZA 39"

print("  ✓ Runtime reports FAZA 39")


# 10) LIST MODULES WITH HOOKS INFO
print("\n[10] Listing modules...")
result_list = m.handle_input("list")
print("List result:", json.dumps(result_list, indent=2))

modules = result_list["result"]["data"]["modules"]
lifecycle_module = next((m for m in modules if m["name"] == "lifecycle_demo"), None)

assert lifecycle_module is not None, "lifecycle_demo not in module list"
assert lifecycle_module["phase"] == 39, "Module phase not 39"

print("  ✓ Module listed with correct phase")


print("\n======================================================")
print("     FAZA 39 SELF-TEST FINISHED SUCCESSFULLY          ")
print("======================================================")
print("\n✅ All lifecycle hooks working correctly:")
print("   - init() called on module load")
print("   - pre_run() called before execution")
print("   - post_run() called after execution")
print("   - on_error() called on exceptions")
print("   - lifecycle stage tracking operational")
