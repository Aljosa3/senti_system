import os
import shutil
import json
import time

from senti_core_module.senti_llm.runtime.llm_runtime_manager import LLMRuntimeManager
from senti_core_module.senti_llm.runtime.autodoc_builder import AutoDocBuilder

print("======================================================")
print("      FAZA D.1 — FULL SELF-TEST (AutoDoc Builder)    ")
print("======================================================")

# 0) PREPARE CLEAN ENVIRONMENT
autodoc_path = "senti_data/autodoc"
docs_path = "docs/generated"
schemas_path = "docs/schemas"

# Clean AutoDoc data
if os.path.exists(autodoc_path):
    for file in os.listdir(autodoc_path):
        filepath = os.path.join(autodoc_path, file)
        if os.path.isfile(filepath):
            os.remove(filepath)

# Clean generated docs
if os.path.exists(docs_path):
    for file in os.listdir(docs_path):
        filepath = os.path.join(docs_path, file)
        if os.path.isfile(filepath):
            os.remove(filepath)

# Clean schemas
if os.path.exists(schemas_path):
    for file in os.listdir(schemas_path):
        filepath = os.path.join(schemas_path, file)
        if os.path.isfile(filepath):
            os.remove(filepath)

print("[0] Clean environment prepared.")


# 1) MANAGER INITIALIZATION
m = LLMRuntimeManager()
print("[1] Runtime initialized.")


# 2) LOAD TEST MODULES
print("\n[2] Loading test modules...")

# Load FAZA 42 reactive demo
result_load1 = m.handle_input(
    "load senti_core_module/senti_llm/modules/faza42_demo_reactive_module.py"
)
assert result_load1["result"]["ok"], "Reactive module failed to load"

# Load FAZA 41 event demo
result_load2 = m.handle_input(
    "load senti_core_module/senti_llm/modules/faza41_demo_event_module.py"
)
assert result_load2["result"]["ok"], "Event module failed to load"

# Load FAZA 40 state demo
result_load3 = m.handle_input(
    "load senti_core_module/senti_llm/modules/faza40_demo_state_module.py"
)
assert result_load3["result"]["ok"], "State module failed to load"

print("  ✓ 3 test modules loaded")


# 3) CREATE AUTODOC BUILDER
print("\n[3] Creating AutoDocBuilder...")
builder = AutoDocBuilder()
print("  ✓ AutoDocBuilder instantiated")


# 4) SCAN RUNTIME
print("\n[4] Scanning runtime...")
runtime_info = builder.scan_runtime()
print("Runtime info:", json.dumps(runtime_info, indent=2))

assert "phase" in runtime_info, "Runtime missing phase"
assert runtime_info["phase"] == "FAZA 42", f"Expected FAZA 42, got {runtime_info['phase']}"

print("  ✓ Runtime scan complete (FAZA 42)")


# 5) SCAN CAPABILITIES
print("\n[5] Scanning capabilities...")
capabilities = builder.scan_capabilities()
print(f"  Capabilities found: {len(capabilities)}")

# Check for known capabilities
assert "log.basic" in capabilities, "log.basic capability not found"
assert "storage.write" in capabilities, "storage.write capability not found"
assert "event.publish" in capabilities, "event.publish capability not found"
assert "event.subscribe" in capabilities, "event.subscribe capability not found"

print(f"  ✓ Capabilities scanned ({len(capabilities)} capabilities)")


# 6) SCAN EVENTS
print("\n[6] Scanning events...")
events = builder.scan_events()
print(f"  Event types found: {len(events.get('registered_types', []))}")

registered_types = events.get("registered_types", [])
assert "module.loaded" in registered_types, "module.loaded event not found"

print(f"  ✓ Events scanned ({len(registered_types)} event types)")


# 7) SCAN MODULES
print("\n[7] Scanning modules...")
modules = builder.scan_modules()
print(f"  Modules found: {len(modules)}")

assert len(modules) >= 3, f"Expected at least 3 modules, got {len(modules)}"

# Check for test modules
module_names = [m["name"] for m in modules]
assert "reactive_demo" in module_names, "reactive_demo not found"
assert "event_demo" in module_names, "event_demo not found"
assert "demo_state" in module_names, "demo_state not found"

print(f"  ✓ Modules scanned ({len(modules)} modules)")


# 8) GENERATE JSON MODEL
print("\n[8] Generating JSON model...")
model = builder.generate_json_model()

assert "runtime" in model, "Model missing runtime"
assert "capabilities" in model, "Model missing capabilities"
assert "events" in model, "Model missing events"
assert "modules" in model, "Model missing modules"
assert "metadata" in model, "Model missing metadata"

print("  ✓ JSON model generated")


# 9) WRITE JSON MODEL
print("\n[9] Writing JSON model to disk...")
json_path = builder.write_json_model()

assert os.path.exists(json_path), "JSON file not created"

# Verify JSON is valid
with open(json_path, "r") as f:
    loaded_model = json.load(f)

assert loaded_model["runtime"]["phase"] == "FAZA 42", "JSON phase mismatch"

print(f"  ✓ JSON model written to {json_path}")


# 10) GENERATE DOCUMENTATION
print("\n[10] Generating Markdown documentation...")
builder.generate_docs()

# Check generated docs
expected_docs = [
    "overview.md",
    "runtime_api.md",
    "capabilities.md",
    "events.md",
    "reactive_modules.md",
    "state_management.md",
    "module_api.md"
]

for doc in expected_docs:
    doc_path = os.path.join(docs_path, doc)
    assert os.path.exists(doc_path), f"Missing doc: {doc}"

    # Check file is not empty
    with open(doc_path, "r") as f:
        content = f.read()
        assert len(content) > 0, f"Empty doc: {doc}"

print(f"  ✓ {len(expected_docs)} Markdown documents generated")


# 11) VERIFY JSON SCHEMAS
print("\n[11] Verifying JSON schemas...")
expected_schemas = [
    "runtime_schema.json",
    "module_schema.json",
    "event_schema.json",
    "state_schema.json"
]

for schema in expected_schemas:
    schema_path = os.path.join(schemas_path, schema)
    assert os.path.exists(schema_path), f"Missing schema: {schema}"

    # Verify schema is valid JSON
    with open(schema_path, "r") as f:
        schema_data = json.load(f)
        assert "$schema" in schema_data, f"Invalid schema: {schema}"

print(f"  ✓ {len(expected_schemas)} JSON schemas generated")


# 12) VERIFY REACTIVE HANDLERS IN DOCS
print("\n[12] Verifying reactive handlers documentation...")
reactive_md_path = os.path.join(docs_path, "reactive_modules.md")

with open(reactive_md_path, "r") as f:
    reactive_content = f.read()

assert "reactive_demo" in reactive_content, "reactive_demo not documented"
assert "module.loaded" in reactive_content, "module.loaded handler not documented"
assert "FAZA 42" in reactive_content, "FAZA 42 not mentioned"

print("  ✓ Reactive handlers documented correctly")


# 13) VERIFY STATE MANAGEMENT IN DOCS
print("\n[13] Verifying state management documentation...")
state_md_path = os.path.join(docs_path, "state_management.md")

with open(state_md_path, "r") as f:
    state_content = f.read()

assert "demo_state" in state_content, "demo_state not documented"
assert "FAZA 40" in state_content, "FAZA 40 not mentioned"
assert "default_state" in state_content, "default_state not documented"

print("  ✓ State management documented correctly")


# 14) VERIFY EVENTS IN DOCS
print("\n[14] Verifying events documentation...")
events_md_path = os.path.join(docs_path, "events.md")

with open(events_md_path, "r") as f:
    events_content = f.read()

assert "module.loaded" in events_content, "module.loaded not documented"
assert "FAZA 41" in events_content, "FAZA 41 not mentioned"
assert "Event Bus" in events_content, "Event Bus not mentioned"

print("  ✓ Events documented correctly")


# 15) VERIFY CAPABILITIES IN DOCS
print("\n[15] Verifying capabilities documentation...")
caps_md_path = os.path.join(docs_path, "capabilities.md")

with open(caps_md_path, "r") as f:
    caps_content = f.read()

assert "log.basic" in caps_content, "log.basic not documented"
assert "storage.write" in caps_content, "storage.write not documented"
assert "event.publish" in caps_content, "event.publish not documented"

print("  ✓ Capabilities documented correctly")


# 16) VERIFY AUTODOC DOES NOT AFFECT MODULE EXECUTION
print("\n[16] Verifying AutoDoc does not affect module execution...")

# Run a test module
result_run = m.handle_input("run reactive_demo mode=status")
assert result_run["result"]["ok"], "Module execution failed after AutoDoc"

stats = result_run["result"]["data"]["stats"]
assert "total_events_handled" in stats, "Module state corrupted"

print("  ✓ Module execution unaffected by AutoDoc")


# 17) VERIFY OVERVIEW.MD STRUCTURE
print("\n[17] Verifying overview.md structure...")
overview_path = os.path.join(docs_path, "overview.md")

with open(overview_path, "r") as f:
    overview_content = f.read()

assert "# Senti LLM Runtime - System Overview" in overview_content, "Missing title"
assert "FAZA 42" in overview_content, "Missing phase"
assert "Quick Links" in overview_content, "Missing quick links"
assert "Getting Started" in overview_content, "Missing getting started"

print("  ✓ overview.md structure valid")


# 18) VERIFY MODULE API DOCS
print("\n[18] Verifying module API documentation...")
module_api_path = os.path.join(docs_path, "module_api.md")

with open(module_api_path, "r") as f:
    api_content = f.read()

assert "reactive_demo" in api_content, "reactive_demo not in API docs"
assert "event_demo" in api_content, "event_demo not in API docs"
assert "demo_state" in api_content, "demo_state not in API docs"

# Check for reactive handlers section
assert "Reactive Handlers" in api_content, "Reactive Handlers section missing"

print("  ✓ Module API documented correctly")


# 19) VERIFY JSON MODEL COMPLETENESS
print("\n[19] Verifying JSON model completeness...")

# Reload model from disk
with open(json_path, "r") as f:
    disk_model = json.load(f)

# Check runtime
assert disk_model["runtime"]["phase"] == "FAZA 42", "Runtime phase mismatch"

# Check capabilities
assert len(disk_model["capabilities"]) >= 4, "Too few capabilities"

# Check events
assert len(disk_model["events"]["registered_types"]) >= 1, "No event types"

# Check modules
assert len(disk_model["modules"]) >= 3, "Too few modules"

# Check metadata
assert "generated_at" in disk_model["metadata"], "Missing metadata.generated_at"
assert "generator" in disk_model["metadata"], "Missing metadata.generator"
assert disk_model["metadata"]["generator"] == "AutoDocBuilder", "Wrong generator"

print("  ✓ JSON model complete and valid")


# 20) FINAL STATUS CHECK
print("\n[20] Final status check...")
result_final = m.handle_input("status")

assert result_final["result"]["data"]["phase"] == "FAZA 42", "Phase changed"
assert result_final["result"]["data"]["event_bus_active"], "EventBus not active"

print("  ✓ Final status OK")


print("\n======================================================")
print("     FAZA D.1 SELF-TEST FINISHED SUCCESSFULLY         ")
print("======================================================")
print("\n✅ All AutoDoc Builder features working correctly:")
print("   - Runtime introspection (FAZA 36-42)")
print("   - Capability scanning (FAZA 37)")
print("   - Event Bus scanning (FAZA 41)")
print("   - Reactive handler scanning (FAZA 42)")
print("   - State schema scanning (FAZA 40)")
print("   - JSON model generation")
print("   - Markdown documentation generation")
print("   - JSON schema generation")
print("   - Module API documentation")
print("   - Non-blocking integration (no module execution impact)")
print("\n📚 Generated Documentation:")
print(f"   - {len(expected_docs)} Markdown documents")
print(f"   - {len(expected_schemas)} JSON schemas")
print(f"   - JSON model: {json_path}")
print("\n🎯 FAZA D.1 implementation complete and verified!")
