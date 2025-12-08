# FAZA 16 UPGRADE DOCUMENTATION

**Version:** 2.0
**Date:** 2025-12-05
**Status:** Production-Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [New Modules](#new-modules)
4. [Upgraded Modules](#upgraded-modules)
5. [API Reference](#api-reference)
6. [Integration with FAZA 31](#integration-with-faza-31)
7. [Routing Logic](#routing-logic)
8. [Fallback Matrix](#fallback-matrix)
9. [Examples](#examples)
10. [Testing](#testing)

---

## Overview

FAZA 16 has been upgraded into a complete **multi-LLM validation, routing, verification, and safety engine**. This upgrade transforms FAZA 16 from a basic LLM control layer into a production-grade system capable of:

- **Multi-model orchestration** with intelligent routing
- **Comprehensive SPEC validation** for auto-generated specifications
- **AST-based code safety analysis** with dangerous pattern detection
- **Architecture compatibility checking** against Senti OS structure
- **Health monitoring** with scoring and failure rerouting
- **Risk-aware routing** with dynamic model selection
- **Full integration** with FAZA 31 auto-spec and auto-build pipeline

**Key Principles:**
- ✅ No external dependencies (stdlib only)
- ✅ Full type hints throughout
- ✅ Production-grade code (no mocks, no stubs)
- ✅ Deterministic outputs
- ✅ Complete test coverage

---

## Architecture

```
FAZA 16 - LLM Validation & Routing Engine
├─────────────────────────────────────────────────┐
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │         LLM Manager (Orchestrator)       │   │
│  │  • Model Selection                       │   │
│  │  • Failure Rerouting                     │   │
│  │  • Cross-Evaluation                      │   │
│  │  • Output Scoring                        │   │
│  └──────────┬───────────────────────────────┘   │
│             │                                    │
│  ┌──────────┴───────────┬──────────────────┐    │
│  │                      │                  │    │
│  ▼                      ▼                  ▼    │
│ ┌────────────┐  ┌──────────────┐  ┌────────┐   │
│ │ Config     │  │ Health       │  │ Router │   │
│ │ Loader     │  │ Monitor      │  │        │   │
│ └────────────┘  └──────────────┘  └────────┘   │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │         Rules Engine                     │   │
│  │  • Anti-Hallucination                    │   │
│  │  • Safety Filters                        │   │
│  │  • SPEC Validation ◄─────────────┐       │   │
│  │  • Code Integrity   ◄──────┐     │       │   │
│  │  • Architecture     ◄────┐ │     │       │   │
│  │  • Risk Scoring          │ │     │       │   │
│  └──────────────────────────┼─┼─────┼───────┘   │
│                             │ │     │           │
│  ┌──────────────────────────┼─┼─────┼───────┐   │
│  │  Validation Pipeline     │ │     │       │   │
│  │                          │ │     │       │   │
│  │  ┌───────────────────────┴─┴─────┴────┐  │   │
│  │  │    Knowledge Validation Engine     │  │   │
│  │  │  • Full Validation Pipeline        │  │   │
│  │  │  • Cross-Component Integration     │  │   │
│  │  └─────────┬──────────────────────────┘  │   │
│  │            │                              │   │
│  │  ┌─────────┴──────┬──────────┬─────────┐ │   │
│  │  │                │          │         │ │   │
│  │  ▼                ▼          ▼         ▼ │   │
│  │ ┌─────┐  ┌──────────┐  ┌─────────┐  ┌───┤ │
│  │ │SPEC │  │Code      │  │Arch     │  │...│ │
│  │ │Valid│  │Safety    │  │Diff     │  │   │ │
│  │ └─────┘  └──────────┘  └─────────┘  └───┘ │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
└─────────────────────────────────────────────────┘
                      │
                      │ FAZA 31 Integration
                      ▼
        ┌─────────────────────────┐
        │   Auto-Spec & Build     │
        │   (FAZA 30.9 / 31)      │
        └─────────────────────────┘
```

---

## New Modules

### 1. **llm_config_loader.py**

**Purpose:** Load and validate LLM configuration from JSON files.

**Features:**
- Schema validation
- Environment variable substitution (`ENV:VAR_NAME`)
- Default value handling
- Multi-model configuration support

**Example:**
```python
from senti_os.core.faza16.llm_config_loader import create_loader

loader = create_loader()
config = loader.load_config()
model = loader.get_model_config("gpt-4")
```

**Config Format:**
```json
{
  "models": [
    {
      "model_id": "gpt4",
      "provider": "openai",
      "model_name": "gpt-4",
      "api_key": "ENV:OPENAI_API_KEY",
      "max_tokens": 8192,
      "roles": ["code_generation", "reasoning"],
      "capabilities": ["text_generation", "analysis"]
    }
  ],
  "default_model": "gpt4",
  "fallback_chain": ["gpt4", "claude", "local"]
}
```

---

### 2. **llm_health_monitor.py**

**Purpose:** Track model health metrics and compute health scores.

**Metrics Tracked:**
- Response latency (ms)
- Error rates
- Hallucination scores
- SPEC consistency scores
- Code quality scores

**Health Score Calculation (0-100):**
```
score = weighted_sum(
    latency_score    * 0.15,
    error_score      * 0.30,
    hallucination    * 0.25,
    spec_consistency * 0.15,
    code_quality     * 0.15
)
```

**Health Status Levels:**
- EXCELLENT: 90-100
- GOOD: 70-89
- FAIR: 50-69
- POOR: 30-49
- CRITICAL: 0-29

**Example:**
```python
from senti_os.core.faza16.llm_health_monitor import create_monitor

monitor = create_monitor()

# Record interaction
monitor.record_interaction(
    model_id="gpt4",
    latency_ms=450.0,
    success=True,
    hallucination_score=0.05,
)

# Get health report
report = monitor.get_health_report("gpt4")
print(f"Health: {report.health_score}/100")
```

---

### 3. **spec_validator.py**

**Purpose:** Validate SPEC documents for structure, completeness, and safety.

**Checks:**
- Required sections (Objective, Architecture, Implementation, Testing)
- Contradictory statements
- Phase numbering validity
- Dangerous patterns (eval, exec, etc.)
- Incomplete sections (TODO, TBD)

**Scoring:**
- Starts at 100
- Deducts for CRITICAL (-25), ERROR (-10), WARNING (-5), INFO (-1)

**Example:**
```python
from senti_os.core.faza16.spec_validator import validate_spec

spec_text = """
# Objective
Build a sensor module

## Architecture
Three-layer design

## Implementation
Step-by-step implementation

## Testing
Unit and integration tests
"""

result = validate_spec(spec_text, "sensor_module")
print(f"Valid: {result.is_valid}, Score: {result.score}")
```

---

### 4. **code_safety_analyzer.py**

**Purpose:** AST-based Python code safety analysis.

**Detects:**
- Dangerous function calls: `eval()`, `exec()`, `compile()`
- Unsafe imports: `os.system`, `subprocess`, `pickle.loads`
- Forbidden path references: `/etc/`, `/sys/`, `senti_os/boot/`
- Incomplete module definitions
- Empty functions and classes

**Safety Score:**
- Starts at 100
- Deducts for CRITICAL (-30), ERROR (-15), WARNING (-5)

**Example:**
```python
from senti_os.core.faza16.code_safety_analyzer import analyze_code

code = """
def safe_function(data):
    return data.upper()
"""

report = analyze_code(code)
print(f"Safe: {report.is_safe}, Score: {report.safety_score}")
```

---

### 5. **architecture_diff.py**

**Purpose:** Compare new modules against existing Senti OS architecture.

**Validates:**
- Module location (valid directories)
- Protected directory access
- Import path validity
- Naming conventions
- Required components

**Protected Directories:**
- `senti_os/boot`
- `senti_os/kernel`
- `senti_os/drivers`

**Example:**
```python
from senti_os.core.faza16.architecture_diff import analyze_module

module_spec = {
    "name": "new_sensor",
    "imports": ["senti_os.core.faza16"],
    "files": ["__init__.py", "sensor.py"],
}

analysis = analyze_module(module_spec, "modules/sensors/new_sensor")
print(f"Compatible: {analysis.is_compatible}")
```

---

## Upgraded Modules

### 1. **llm_manager.py**

**New Methods:**
- `select_model(task_profile)` - Select best model for task
- `reroute_on_failure(failed_model_id, task_profile)` - Reroute after failure
- `get_model_health(model_id)` - Get health metrics
- `score_model_output(model_id, output)` - Score output quality
- `compare_models(output_a, output_b, model_a_id, model_b_id)` - Compare models

**Integration:**
- Config loader for model configuration
- Health monitor for reliability tracking

---

### 2. **llm_rules.py**

**New Rules:**
- `spec_validation` - SPEC document validation
- `code_integrity` - Code safety analysis
- `architecture_constraints` - Architecture compatibility

**New Methods:**
- `validate_spec(spec_text)` - Validate SPEC
- `validate_code(code_text)` - Validate code safety
- `validate_architecture(module_spec, module_path)` - Validate architecture
- `calculate_risk_score(...)` - Calculate overall risk
- `validate_with_user_override(...)` - Apply FAZA 29 governance override

**Risk Scoring:**
```
risk_score = (
    (100 - spec_score)   * 0.30 +
    (100 - code_score)   * 0.40 +
    (100 - arch_score)   * 0.30
)

risk_level = LOW | MODERATE | HIGH | CRITICAL
```

---

### 3. **knowledge_validation_engine.py**

**New Methods:**
- `run_full_validation(...)` - Complete validation pipeline
- `validate_spec_pipeline(spec_text)` - SPEC validation
- `validate_code_ast(code)` - AST code analysis
- `validate_architecture_diff(module_spec, module_path)` - Architecture analysis

**Full Validation Pipeline:**
1. SPEC validation (if provided)
2. Code safety analysis (if provided)
3. Architecture compatibility (if provided)
4. Aggregate results with recommendations

**Returns:**
```python
{
    "timestamp": "...",
    "validations_performed": ["spec", "code", "architecture"],
    "overall_status": "PASS|FAIL|PASS_WITH_WARNINGS",
    "issues_found": 0,
    "recommendations": [...]
}
```

---

### 4. **llm_router.py**

**New Parameters (RoutingRequest):**
- `required_role` - Role-based routing
- `risk_level` - Risk-aware routing

**New Methods:**
- `route_by_role(role, task_type)` - Route by required role
- `route_with_risk_awareness(request, risk_level)` - Risk-aware routing
- `route_with_fallback(request, exclude_sources)` - Multi-model fallback

**Risk-Aware Routing:**
```python
risk_reliability_map = {
    "low": 0.7,
    "moderate": 0.75,
    "high": 0.85,
    "critical": 0.95
}
```

For high/critical risk, automatically switches to QUALITY priority mode.

---

## API Reference

### FAZA 31 Integration APIs

#### `select_model(task_profile: dict) -> str`
Select best model for task profile.

```python
from senti_os.core.faza16 import select_model

model_id = select_model({
    "task_type": TaskType.CODE_GENERATION,
    "priority_mode": PriorityMode.QUALITY,
    "max_cost": 1.0,
})
```

#### `validate_spec(spec_text: str) -> dict`
Validate SPEC document.

```python
from senti_os.core.faza16 import validate_spec

result = validate_spec(spec_text)
# Returns: {"is_valid": bool, "score": float, "issues": [...]}
```

#### `validate_code(code_text: str) -> dict`
Validate Python code safety.

```python
from senti_os.core.faza16 import validate_code

result = validate_code(code_text)
# Returns: {"is_safe": bool, "safety_score": float, "issues": [...]}
```

#### `validate_architecture(module_spec: dict, module_path: str) -> dict`
Validate module architecture.

```python
from senti_os.core.faza16 import validate_architecture

result = validate_architecture(module_spec, module_path)
# Returns: {"is_compatible": bool, "compatibility_score": float, "diffs": [...]}
```

#### `run_full_validation(...) -> dict`
Run complete validation pipeline.

```python
from senti_os.core.faza16 import run_full_validation

report = run_full_validation(
    spec_text="...",
    code_text="...",
    module_spec={...},
    module_path="..."
)
```

#### `route_request(task_type: str, priority_mode: str, risk_level: str) -> dict`
Route LLM request with risk awareness.

```python
from senti_os.core.faza16 import route_request

result = route_request(
    task_type="code",
    priority_mode="quality",
    risk_level="high"
)
```

#### `compute_health_score(model_id: str) -> float`
Get model health score (0-100).

```python
from senti_os.core.faza16 import compute_health_score

score = compute_health_score("gpt4")
```

---

## Integration with FAZA 31

**FAZA 31** (Auto-Spec & Auto-Build) integrates with FAZA 16 for:

### 1. SPEC Generation Validation
```python
# FAZA 31 generates SPEC
spec = generate_spec_for_feature(user_request)

# FAZA 16 validates
validation = validate_spec(spec)

if not validation["is_valid"]:
    # Regenerate with corrections
    spec = regenerate_spec(spec, validation["issues"])
```

### 2. Code Generation Validation
```python
# FAZA 31 generates code
code = generate_code_from_spec(spec)

# FAZA 16 validates safety
safety = validate_code(code)

if not safety["is_safe"]:
    # Fix safety issues
    code = fix_safety_issues(code, safety["issues"])
```

### 3. Architecture Compatibility
```python
# FAZA 31 proposes module
module_spec = create_module_spec(feature)

# FAZA 16 checks compatibility
compat = validate_architecture(module_spec, proposed_path)

if not compat["is_compatible"]:
    # Adjust module design
    module_spec = adjust_module(module_spec, compat["diffs"])
```

### 4. Full Pipeline Integration
```python
# Complete FAZA 31 + FAZA 16 workflow
def auto_build_feature(user_request):
    # Step 1: Generate SPEC
    spec = generate_spec(user_request)

    # Step 2: Full validation
    validation = run_full_validation(
        spec_text=spec,
        module_spec=module_spec,
        module_path=proposed_path
    )

    if validation["overall_status"] == "FAIL":
        return {"error": "Validation failed", "issues": validation}

    # Step 3: Generate code
    code = generate_code(spec)

    # Step 4: Validate code
    code_validation = validate_code(code)

    if not code_validation["is_safe"]:
        return {"error": "Code unsafe", "issues": code_validation}

    # Step 5: Deploy
    deploy_module(code, proposed_path)

    return {"success": True, "validation": validation}
```

---

## Routing Logic

### Standard Routing
```
1. Filter sources by constraints:
   - Enabled
   - Min reliability >= threshold
   - Cost <= max_cost
   - Max tokens >= needed

2. Score each source:
   score = Σ(weight_i * score_i)

   Weights (BALANCED):
   - quality: 0.25
   - cost: 0.20
   - speed: 0.20
   - reliability: 0.25
   - domain: 0.10

3. Select highest scoring source
```

### Role-Based Routing
```
1. Filter sources with required role
2. Apply standard routing on filtered set
```

### Risk-Aware Routing
```
Risk Level → Min Reliability
- low: 0.7
- moderate: 0.75
- high: 0.85
- critical: 0.95

High/Critical → Force QUALITY priority
```

---

## Fallback Matrix

```
Primary Model Fails
        │
        ▼
┌───────────────────┐
│ Record Failure    │
│ Update Health     │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Get Fallback      │
│ Chain (Top 3)     │
└─────────┬─────────┘
          │
          ▼
    ┌─────────┐
    │ Model 2 │──── Success ──→ Continue
    └────┬────┘
         │ Fail
         ▼
    ┌─────────┐
    │ Model 3 │──── Success ──→ Continue
    └────┬────┘
         │ Fail
         ▼
    ┌─────────┐
    │ Model 4 │──── Success ──→ Continue
    └────┬────┘
         │ Fail
         ▼
    ╔═══════════╗
    ║   ERROR   ║
    ║ No models ║
    ║ available ║
    ╚═══════════╝
```

---

## Examples

### Example 1: Validate New Module
```python
from senti_os.core.faza16 import run_full_validation

spec = """
# Objective
Build temperature sensor module

## Architecture
Sensor class with data collection

## Implementation
1. Create Sensor class
2. Add temperature reading method
3. Implement error handling

## Testing
Unit tests for accuracy
"""

code = """
class TemperatureSensor:
    def __init__(self):
        self.readings = []

    def read_temperature(self):
        # Safe implementation
        return 25.0
"""

module_spec = {
    "name": "temperature_sensor",
    "imports": ["typing", "dataclasses"],
    "files": ["__init__.py", "sensor.py"],
    "functions": ["read_temperature"],
    "classes": ["TemperatureSensor"],
}

report = run_full_validation(
    spec_text=spec,
    code_text=code,
    module_spec=module_spec,
    module_path="modules/sensors/temperature"
)

print(f"Status: {report['overall_status']}")
print(f"Issues: {report['issues_found']}")
```

### Example 2: Risk-Aware Model Selection
```python
from senti_os.core.faza16 import route_request

# High-risk code generation
result = route_request(
    task_type="code",
    priority_mode="quality",
    risk_level="high"
)

print(f"Selected: {result['selected_model']}")
print(f"Reasoning: {result['reasoning']}")
```

### Example 3: Model Health Monitoring
```python
from senti_os.core.faza16.llm_health_monitor import create_monitor
from senti_os.core.faza16.llm_manager import create_manager

monitor = create_monitor()
manager = create_manager()

# Record interactions
for i in range(10):
    monitor.record_interaction(
        model_id="gpt4",
        latency_ms=400.0,
        success=True,
        hallucination_score=0.05,
    )

# Check health
health = manager.get_model_health("gpt4")
print(f"Health: {health['health_score']}/100")
print(f"Status: {health['health_status']}")
```

---

## Testing

### Run All Tests
```bash
cd /home/pisarna/senti_system
python3 -m unittest tests/test_faza16_upgrade.py -v
```

### Test Coverage

**Module Tests:**
- ✅ LLM Config Loader (4 tests)
- ✅ LLM Health Monitor (4 tests)
- ✅ SPEC Validator (4 tests)
- ✅ Code Safety Analyzer (5 tests)
- ✅ Architecture Diff (3 tests)
- ✅ Upgraded LLM Manager (3 tests)
- ✅ Upgraded LLM Rules (3 tests)
- ✅ Upgraded Knowledge Validation (1 test)
- ✅ FAZA 31 API Integration (2 tests)

**Total: 29 tests**

All tests use:
- Real implementations (no mocks)
- Stdlib only (no external deps)
- Deterministic assertions

---

## Next Steps

### For FAZA 30.9 (Auto-Spec Generator)
Integrate FAZA 16 validation:
```python
from senti_os.core.faza16 import validate_spec

def generate_validated_spec(user_request):
    spec = generate_spec(user_request)

    validation = validate_spec(spec)

    if not validation["is_valid"]:
        spec = regenerate_with_fixes(spec, validation["issues"])

    return spec
```

### For FAZA 31 (Auto-Build System)
Full integration pipeline:
```python
from senti_os.core.faza16 import run_full_validation

def auto_build_module(spec, code, module_spec, path):
    validation = run_full_validation(
        spec_text=spec,
        code_text=code,
        module_spec=module_spec,
        module_path=path
    )

    if validation["overall_status"] == "FAIL":
        raise ValidationError(validation)

    # Proceed with build
    build_and_deploy(code, path)
```

---

## Summary

**Files Created:** 5 new modules
**Files Upgraded:** 4 existing modules
**Tests Added:** 29 comprehensive tests
**API Functions:** 7 FAZA 31 integration APIs

**FAZA 16 is now production-ready** for multi-LLM orchestration, validation, and integration with FAZA 30.9 and FAZA 31 auto-generation systems.

---

**End of Documentation**
