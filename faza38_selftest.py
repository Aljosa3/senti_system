import os
import shutil
import json

from senti_core_module.senti_llm.runtime.llm_runtime_manager import LLMRuntimeManager

print("======================================================")
print("      FAZA 38 — FULL SELF-TEST (Module Storage)       ")
print("======================================================")

# 0) PREPARE CLEAN ENVIRONMENT
if os.path.exists("senti_data/modules/storage_demo"):
    shutil.rmtree("senti_data/modules/storage_demo")

print("[0] Clean environment prepared.")


# 1) MANAGER INITIALIZATION
m = LLMRuntimeManager()
print("[1] Runtime initialized.")


# 2) LIST BEFORE LOAD
print("[2] List before load:", m.handle_input("list"))


# 3) LOAD STORAGE DEMO MODULE
result_load = m.handle_input(
    "load senti_core_module/senti_llm/modules/storage_demo_module.py"
)
print("[3] Load result:", result_load)

assert result_load["result"]["ok"], "Module failed to load"


# 4) LIST AFTER LOAD
result_list = m.handle_input("list")
print("[4] List after load:", json.dumps(result_list, indent=2))


# 5) RUN MODULE
result_run = m.handle_input("run storage_demo")
print("[5] Run result:", json.dumps(result_run, indent=2))

assert result_run["result"]["ok"], "Module run failed"
assert (
    result_run["result"]["data"]["written"]
    == result_run["result"]["data"]["read_back"]
), "Written != Read back — storage integrity failure"


# Get storage object for subsequent tests
mod_data = m.exec_orchestrator.module_loader.registry.get("storage_demo")
storage = mod_data["capabilities"]["storage.write"].storage


# 6) VERIFY FILE EXISTS
base = os.path.join(os.getcwd(), "senti_data/modules/storage_demo/test/data.json")
print("[DEBUG] Checking full path:", base)
assert os.path.exists(base), f"Storage file not found at: {base}"


# 7) LOAD JSON FROM DISK
with open(base, "r") as f:
    disk_data = json.load(f)
print("[7] Disk data:", disk_data)


# 8) TRY PATH TRAVERSAL ATTACK
try:
    out = storage.read_text("../../etc/passwd")
    print("[8] ERROR — traversal allowed:", out)
except Exception as e:
    print("[8] Traversal attack blocked OK:", e)


# 9) SYMLINK ESCAPE ATTACK
os.makedirs("senti_data/modules/storage_demo/test2", exist_ok=True)
link_path = "senti_data/modules/storage_demo/test2/passwd_link"
if os.path.exists(link_path):
    os.remove(link_path)

os.symlink("/etc/passwd", link_path)

try:
    out = storage.read_text("test2/passwd_link")
    print("[9] ERROR — symlink escape allowed:", out)
except Exception as e:
    print("[9] Symlink attack blocked OK:", e)


# 10) STORAGE API NEGATIVE TEST
try:
    out = storage.read_text("does_not_exist.json")
    print("[10] Missing file response:", out)
except Exception as e:
    print("[10] Missing file raised exception:", e)


print("======================================================")
print("     FAZA 38 SELF-TEST FINISHED SUCCESSFULLY          ")
print("======================================================")
