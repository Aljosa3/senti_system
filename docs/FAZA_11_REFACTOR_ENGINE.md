# FAZA 11 – Self-Refactor Engine

**Version:** 1.0.0
**Status:** Active
**Location:** `senti_core_module/senti_refactor/`

## Overview

FAZA 11 introduces AI-powered refactoring capabilities to the Senti System, enabling automated code transformation through Abstract Syntax Tree (AST) manipulation. This phase provides the foundation for self-healing code, intelligent refactoring suggestions, and safe code modifications.

## Goals

FAZA 11 enables:
- **Automated code refactoring** – AST-based safe code transformations
- **Self-healing capabilities** – Automatic correction of code issues
- **AI-driven suggestions** – Intelligent refactoring recommendations (foundation for FAZA 15)
- **Safe modifications** – Validated function additions, removals, and renames
- **Security validation** – Integration with FAZA 8 Security Manager
- **AI orchestration** – Integration with FAZA 5 and FAZA 6 loops

## Architecture

### Core Components

#### 1. RefactorEngine (`refactor_engine.py`)

The core engine executing AST-level transformations.

**Key Features:**
- AST parsing and manipulation using Python's `ast` module
- Code generation via `astor` library
- Event publication for refactor operations
- Extensible transformation system

**Example Usage:**
```python
from pathlib import Path
from senti_core_module.senti_refactor import RefactorEngine
from senti_core_module.senti_core.services.event_bus import EventBus

project_root = Path("/path/to/project")
event_bus = EventBus()
engine = RefactorEngine(project_root, event_bus)

# Apply a transformation
patch = {
    "action": "rename_function",
    "old": "old_function_name",
    "new": "new_function_name"
}
result = engine.apply_patch(file_path, patch)
```

#### 2. RefactorManager (`refactor_manager.py`)

High-level orchestrator for refactor operations.

**Key Features:**
- Simplified API for refactor operations
- Path resolution and validation
- Future AI suggestion integration point

**Example Usage:**
```python
from senti_core_module.senti_refactor import RefactorManager

manager = RefactorManager(project_root, event_bus)
result = manager.apply_refactor("modules/sensors/sensor.py", patch)
```

#### 3. RefactorRules (`refactor_rules.py`)

Security and integrity validation for refactor patches.

**Key Features:**
- Patch validation before execution
- Action whitelist enforcement
- Parameter validation for each action type

**Supported Actions:**
- `rename_function` – Rename function definitions

#### 4. RefactorEvents (`refactor_events.py`)

Event definitions for EventBus integration.

**Events:**
- `REFACTOR_APPLIED` – Emitted when a refactor is successfully applied

#### 5. ASTPatchTemplate (`ast_patch_template.py`)

Standard patch structures for safe transformations.

**Example:**
```python
from senti_core_module.senti_refactor import ASTPatchTemplate

patch = ASTPatchTemplate.rename_function("old_name", "new_name")
```

## Integration Points

### FAZA 5 – AI Operational Layer

FAZA 11 registers as a service in the AI Operational Layer:

```python
self.ai.register_service("refactor", self.refactor_manager)
```

This enables AI agents to request refactoring operations.

### FAZA 6 – Autonomous Task Loop

The autonomous loop can periodically check for queued refactor tasks and execute them.

### FAZA 8 – Security Manager

All patches are validated using `RefactorRules.validate_patch()` before execution, ensuring security compliance.

### Boot System

FAZA 11 is initialized during system boot:

```python
from senti_core_module.senti_refactor import RefactorManager

self.refactor_manager = RefactorManager(self.project_root, self.event_bus)
logger.info("FAZA 11 Refactor Engine initialized")
```

## Refactor Operations

### Current Operations

#### Rename Function

Renames a function definition throughout a file.

**Patch Structure:**
```python
{
    "action": "rename_function",
    "old": "original_function_name",
    "new": "new_function_name"
}
```

**Process:**
1. Patch is validated by RefactorRules
2. File is parsed into AST
3. FunctionDef nodes with matching name are transformed
4. AST is converted back to source code
5. File is written with new content
6. REFACTOR_APPLIED event is published

### Future Operations (Planned)

- `add_function` – Add new function to file
- `remove_function` – Remove function from file
- `add_parameter` – Add parameter to function signature
- `remove_parameter` – Remove parameter from function signature
- `extract_method` – Extract code block into new function
- `inline_function` – Inline function call
- `add_docstring` – Add or update docstrings
- `optimize_imports` – Clean and organize imports

## Security Model

### Validation Rules

1. **Action Whitelist** – Only approved actions are allowed
2. **Parameter Validation** – Required parameters must be present
3. **Path Validation** – Files must exist and be accessible
4. **AST Integrity** – Transformations preserve AST structure

### Protected Operations

- Core system files cannot be modified without explicit override
- Security-critical modules have additional validation layers
- All refactors are logged and auditable

## Event System

### Published Events

#### REFACTOR_APPLIED

**When:** A refactor patch is successfully applied
**Payload:**
```python
{
    "file": "/path/to/file.py",
    "patch": {
        "action": "rename_function",
        "old": "foo",
        "new": "bar"
    }
}
```

### Subscribing to Events

```python
def on_refactor(data):
    print(f"Refactored: {data['file']}")

event_bus.subscribe("REFACTOR_APPLIED", on_refactor)
```

## Testing

### Test Suite Location

`tests/test_faza11_refactor.py`

### Running Tests

```bash
PYTHONPATH=/home/pisarna/senti_system:$PYTHONPATH python3 tests/test_faza11_refactor.py
```

### Test Coverage

- Function renaming
- Patch validation
- Event publication
- Error handling

## Dependencies

### Required Packages

- `ast` (Python standard library) – AST parsing and unparsing (Python 3.9+)
- `pathlib` (Python standard library)

### No External Dependencies

FAZA 11 uses Python's built-in `ast.unparse()` (available in Python 3.9+) for AST-to-source conversion, eliminating the need for external dependencies.

## Usage Examples

### Basic Function Rename

```python
from pathlib import Path
from senti_core_module.senti_refactor import RefactorManager, ASTPatchTemplate
from senti_core_module.senti_core.services.event_bus import EventBus

project_root = Path("/home/pisarna/senti_system")
event_bus = EventBus()
manager = RefactorManager(project_root, event_bus)

# Create patch
patch = ASTPatchTemplate.rename_function("old_function", "new_function")

# Apply refactor
result = manager.apply_refactor("modules/sensors/sensor.py", patch)

print(f"Status: {result['status']}")
print(f"File: {result['file']}")
```

### With Event Handling

```python
def log_refactor(data):
    print(f"[REFACTOR] {data['patch']['action']} on {data['file']}")

event_bus.subscribe("REFACTOR_APPLIED", log_refactor)

manager.apply_refactor("modules/sensors/sensor.py", patch)
```

## Future Enhancements (FAZA 15+)

### AI-Driven Suggestions

FAZA 15 will enhance the `suggest_refactor()` method with:
- Code quality analysis
- Performance optimization suggestions
- Best practice recommendations
- Automatic refactoring proposals

### Machine Learning Integration

- Pattern recognition for common refactorings
- Learning from developer preferences
- Predictive refactoring suggestions

### Advanced Transformations

- Multi-file refactoring
- Class hierarchy restructuring
- Design pattern application
- Code smell detection and resolution

## API Reference

### RefactorManager

#### `__init__(project_root: Path, event_bus: EventBus)`
Initialize the refactor manager.

#### `apply_refactor(file: str, patch: dict) -> dict`
Apply a refactor patch to a file.

**Parameters:**
- `file` – Relative path from project root
- `patch` – Transformation specification

**Returns:**
- `dict` with `status`, `file`, and `patch` keys

#### `suggest_refactor(file: str) -> dict`
Get AI refactoring suggestions (placeholder for FAZA 15).

### ASTPatchTemplate

#### `rename_function(old: str, new: str) -> dict`
Create a function rename patch.

### RefactorRules

#### `validate_patch(patch: dict) -> None`
Validate a patch structure. Raises `ValueError` if invalid.

## Troubleshooting

### Common Issues

**Issue:** `FileNotFoundError` when applying patch
**Solution:** Ensure file path is relative to project root

**Issue:** `ValueError: Invalid patch action`
**Solution:** Check action is in VALID_ACTIONS list

**Issue:** `SyntaxError` after refactor
**Solution:** File had syntax errors before refactor; fix source first

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

When adding new refactor actions:

1. Add action to `RefactorRules.VALID_ACTIONS`
2. Implement transformation in `RefactorEngine`
3. Add validation logic to `RefactorRules.validate_patch()`
4. Create template method in `ASTPatchTemplate`
5. Add tests to `test_faza11_refactor.py`
6. Update this documentation

## Version History

### 1.0.0 (2025-12-01)
- Initial FAZA 11 implementation
- Function renaming support
- AST-based transformation engine
- Security validation
- EventBus integration
- Boot system integration

## References

- [Python AST Documentation](https://docs.python.org/3/library/ast.html)
- [Astor Library](https://github.com/berkerpeksag/astor)
- FAZA 5 – AI Operational Layer
- FAZA 6 – Autonomous Task Loop
- FAZA 8 – Security Manager
- FAZA 10 – Expansion Engine

## License

Part of the Senti System. See project LICENSE for details.
