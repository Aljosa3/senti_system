# FAZA 10 - AI Expansion Engine

**Version:** 1.0.0
**Status:** ✅ Fully Integrated
**Location:** `senti_core_module/senti_expansion/`

## Overview

FAZA 10 is the AI-driven expansion engine that allows Senti OS to dynamically create, generate, and register new modules at runtime. This enables the system to self-expand and adapt based on AI orchestration layer decisions.

## Architecture

### Components

```
senti_expansion/
├── __init__.py                  # Package initialization and exports
├── expansion_manager.py         # High-level orchestrator
├── expansion_engine.py          # Core expansion engine
├── expansion_rules.py           # Security and validation rules
├── module_template.py           # Module code generator
└── expansion_events.py          # EventBus integration
```

### Component Details

#### 1. ExpansionManager
**Purpose:** High-level API for managing expansion operations

**Key Methods:**
- `create_module(name, directory)` - Create a new module
- `handle_ai_request(request)` - Process AI expansion requests

**Usage:**
```python
from pathlib import Path
from senti_core_module.senti_core.services.event_bus import EventBus
from senti_core_module.senti_expansion import ExpansionManager

event_bus = EventBus()
manager = ExpansionManager(Path.cwd(), event_bus)

result = manager.create_module(
    name="my_new_sensor",
    directory="modules/sensors"
)
```

#### 2. ExpansionEngine
**Purpose:** Core engine that performs the actual module creation

**Responsibilities:**
- Directory creation
- File generation
- Event publishing
- Rule validation

**Key Methods:**
- `expand(module_name, target_dir)` - Expand system with new module

#### 3. ExpansionRules
**Purpose:** Enforce security and integrity during expansion

**Security Features:**
- Name validation (valid Python identifiers only)
- Protected directory enforcement
- Prevents modification of core system directories

**Protected Directories:**
- `senti_core`
- `senti_os`
- `senti_core_module`

#### 4. ModuleTemplate
**Purpose:** Generate standardized module code

**Template Structure:**
```python
"""
Auto-generated module created by Senti Expansion Engine.
Module name: {module_name}
"""

class {ModuleName}:
    def __init__(self):
        pass

    def run(self):
        print("Module {module_name} is active")
```

#### 5. ExpansionEvent
**Purpose:** EventBus integration for tracking expansion operations

**Event Types:**
- `MODULE_CREATED` - Emitted when a new module is successfully created

**Event Payload:**
```python
{
    "name": "module_name",
    "path": "/absolute/path/to/module"
}
```

## Security Model

### Validation Rules

1. **Module Name Validation**
   - Must match pattern: `^[a-zA-Z_][a-zA-Z0-9_]*$`
   - Valid Python identifier
   - No special characters or spaces

2. **Directory Protection**
   - Cannot create modules in system directories
   - Prevents corruption of core components
   - Raises `PermissionError` on violation

3. **Safe Expansion**
   - All operations within project boundaries
   - No arbitrary file system access
   - Controlled template generation

## Usage Examples

### Example 1: Simple Module Creation

```python
from pathlib import Path
from senti_core_module.senti_core.services.event_bus import EventBus
from senti_core_module.senti_expansion import ExpansionManager

# Initialize
project_root = Path("/home/pisarna/senti_system")
event_bus = EventBus()
manager = ExpansionManager(project_root, event_bus)

# Create new sensor module
result = manager.create_module(
    name="temperature_sensor",
    directory="modules/sensors"
)

print(f"Module created: {result['directory']}")
```

### Example 2: AI-Driven Expansion

```python
# AI agent prepares expansion request
ai_request = {
    "action": "create_module",
    "name": "ai_generated_processor",
    "directory": "modules/processing"
}

# Manager handles the request
result = manager.handle_ai_request(ai_request)

if result['status'] == 'success':
    print(f"AI successfully created: {result['module']}")
```

### Example 3: Event Subscription

```python
def on_module_created(payload):
    print(f"New module created: {payload['name']}")
    print(f"Location: {payload['path']}")

# Subscribe to expansion events
event_bus.subscribe("MODULE_CREATED", on_module_created)

# Trigger expansion
manager.create_module("new_module", "modules/processing")
```

## Testing

### Run FAZA 10 Tests

```bash
cd /home/pisarna/senti_system
PYTHONPATH=/home/pisarna/senti_system:$PYTHONPATH python3 tests/test_faza10_expansion.py
```

### Expected Output

```
============================================================
FAZA 10 — AI Expansion Engine Test
============================================================

✓ ExpansionManager initialized

[TEST 1] Creating test module 'test_ai_module'...
✓ Module created successfully

[TEST 2] Testing AI request handling...
✓ AI request handled successfully

[TEST 3] Testing security validation...
✓ Security validation working

============================================================
FAZA 10 Test Complete
============================================================
```

## Integration with Senti OS

FAZA 10 integrates seamlessly with:

1. **EventBus** - All expansion operations publish events
2. **AI Operational Layer (FAZA 5)** - AI agents can request expansions
3. **Task Orchestration Engine** - Expansion tasks can be orchestrated
4. **Security Layer (FAZA 8)** - All operations validated by security rules

## Future Enhancements

Potential future capabilities:
- Module dependency management
- Automatic import registration
- Runtime module loading
- Module versioning
- Expansion rollback
- AI-driven code generation improvements
- Module marketplace integration

## API Reference

### ExpansionManager API

```python
class ExpansionManager:
    def __init__(self, project_root: Path, event_bus: EventBus)
    def create_module(self, name: str, directory: str = "modules") -> dict
    def handle_ai_request(self, request: dict) -> dict
```

### ExpansionEngine API

```python
class ExpansionEngine:
    def __init__(self, project_root: Path, event_bus: EventBus)
    def expand(self, module_name: str, target_dir: str = "modules") -> dict
```

### ExpansionRules API

```python
class ExpansionRules:
    def __init__(self, project_root: Path)
    def validate_module_name(self, name: str) -> None
    def validate_target_directory(self, target_dir: str) -> None
```

## Notes

- FAZA 10 is production-ready and fully tested
- All security rules are enforced automatically
- Expansion operations are logged via EventBus
- Generated modules follow Senti System conventions
- Integration with AI Operational Layer enables autonomous expansion

---

**Document Version:** 1.0.0
**Last Updated:** 2025-12-01
**Integration Status:** ✅ Complete
