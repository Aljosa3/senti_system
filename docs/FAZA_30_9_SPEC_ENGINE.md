# FAZA 30.9 – Auto-SPEC Generator and Secure Pre-Build Pipeline

## Overview

FAZA 30.9 is an automated specification generation and secure pre-build pipeline system. It transforms natural language descriptions into structured, validated specifications and safe LLM prompts for code generation.

**Key Capabilities:**
- Extract structured requirements from natural language
- Generate SESY-format specifications
- Sanitize specifications for external LLM use
- Validate for safety, completeness, and feasibility
- Build safe LLM code-generation prompts
- Generate comprehensive build plans

**Security-First Design:**
- No internal architecture leakage
- Strict sanitization of sensitive information
- Multi-stage validation with safety gating
- Fail-safe integration patterns

## Architecture

### Pipeline Stages

```
Natural Language Input
        ↓
    EXTRACTION     ← Extract requirements, constraints, goals
        ↓
    GENERATION     ← Generate SESY specification
        ↓
    SANITIZATION   ← Remove sensitive information
        ↓
    VALIDATION     ← Validate safety & completeness
        ↓
    PROMPT BUILD   ← Build LLM prompt
        ↓
    PLAN BUILD     ← Generate build plan
        ↓
    Complete / Failed
```

### Components

1. **SpecExtractor** - Extracts structured data from natural language
2. **SpecGenerator** - Generates SESY-format specifications
3. **SpecSanitizer** - Removes sensitive information
4. **SpecValidator** - Validates specifications
5. **PromptBuilder** - Builds LLM prompts
6. **PlanBuilder** - Generates build plans
7. **Controller** - Orchestrates the pipeline
8. **IntegrationLayer** - Interfaces with other system phases
9. **EventHooks** - Emits events for monitoring

## Usage

### Basic Usage

```python
from senti_os.core.faza30_9 import process_natural_language

# Process natural language input
result = process_natural_language(
    "Create a component that validates email addresses and phone numbers"
)

if result.success:
    # Access outputs
    print("Generated Spec:", result.generated_spec.name)
    print("LLM Prompt:", result.llm_prompt[:100])

    # Save build plan
    result.build_plan.save_to_files("./output")
else:
    print("Errors:", result.errors)
```

### Advanced Usage

```python
from senti_os.core.faza30_9 import SpecEngineController

# Create controller
controller = SpecEngineController()

# Process with custom component name
result = controller.process(
    natural_language="Build a data processor",
    component_name="data_processor",
    strict_validation=True
)

# Check validation
if result.validation_report:
    print("Validation Result:", result.validation_report.result)
    print("Warnings:", result.validation_report.warnings)
    print("Errors:", result.validation_report.errors)
```

### Component-Level Usage

```python
from senti_os.core.faza30_9 import (
    SpecExtractor,
    SpecGenerator,
    SpecSanitizer,
    SpecValidator
)

# Extract from natural language
extractor = SpecExtractor()
extracted = extractor.extract("Create a validator component")

# Generate specification
generator = SpecGenerator()
spec = generator.generate(extracted.to_dict())

# Sanitize for external use
sanitizer = SpecSanitizer()
sanitized = sanitizer.sanitize(spec.to_dict())

# Validate
validator = SpecValidator()
report = validator.validate(sanitized)

print("Validation passed:", report.is_safe_to_proceed())
```

## SESY Specification Format

SESY (Senti Specification) is the structured format for component specifications.

### Structure

```json
{
  "name": "component_name",
  "purpose": "Component purpose statement",
  "architecture": {
    "type": "modular",
    "complexity": "moderate",
    "components": [],
    "patterns": []
  },
  "api_definitions": [
    {
      "method": "method_name",
      "description": "Method description",
      "inputs": [],
      "outputs": [],
      "errors": []
    }
  ],
  "lifecycle": {
    "initialization": {},
    "execution": {},
    "shutdown": {}
  },
  "integration_points": [],
  "constraints": [],
  "test_plan": {
    "test_cases": [],
    "coverage_target": 0.9,
    "frameworks": ["unittest"],
    "test_types": ["unit", "integration"]
  },
  "metadata": {}
}
```

## Safety Features

### Sanitization

The SpecSanitizer removes all sensitive information:

- Internal architecture references
- Module and directory names
- File paths
- Phase/FAZA references
- Agent names
- Governance mechanisms
- System internals

**Example:**

```python
from senti_os.core.faza30_9 import SpecSanitizer

sanitizer = SpecSanitizer()

original = {
    "name": "component",
    "description": "Uses FAZA 16 and senti_os kernel"
}

sanitized = sanitizer.sanitize(original)
# Output: description contains [REDACTED] instead of sensitive terms

# Validate sanitization
is_safe, found = sanitizer.validate_sanitization(sanitized)
print("Safe:", is_safe)
```

### Validation

The SpecValidator performs comprehensive validation:

1. **Completeness** - All required fields present
2. **Consistency** - No internal contradictions
3. **Architecture Compliance** - Follows system patterns
4. **Safety** - No dangerous operations
5. **Feasibility** - Can be implemented

**Validation Results:**

- `PASS` - Fully valid, proceed
- `PASS_WITH_WARNINGS` - Valid but has concerns
- `BLOCK` - Invalid, cannot proceed

**Example:**

```python
from senti_os.core.faza30_9 import validate_spec

spec = {
    "name": "validator",
    "purpose": "Validate inputs",
    # ... full spec
}

report = validate_spec(spec)

if report.result == ValidationResult.BLOCK:
    print("Blocked:", report.errors)
elif report.result == ValidationResult.PASS_WITH_WARNINGS:
    print("Warnings:", report.warnings)
else:
    print("Passed validation")
```

## Build Plans

Build plans define the compilation and build process.

### Components

1. **compile_plan.json** - Compilation steps and dependencies
2. **build_context.json** - Context for code generation
3. **safety_constraints.json** - Safety rules and restrictions

### Example

```python
from senti_os.core.faza30_9 import PlanBuilder

builder = PlanBuilder()
plan = builder.build(spec, sanitized_spec)

# Save to files
files = plan.save_to_files("./output")
print("Created files:", files)

# Access plan data
print("Steps:", plan.compile_plan["compilation_steps"])
print("Safety:", plan.safety_constraints["file_system"])
```

## Integration

### EventBus Integration

```python
from senti_os.core.faza30_9 import initialize_event_hooks
from senti_core_module.senti_core.services.event_bus import EventBus

# Initialize with EventBus
event_bus = EventBus()
hooks = initialize_event_hooks(event_bus)

# Events are automatically emitted to EventBus
# Subscribe to events: faza30_9.extraction_started, etc.
```

### Integration Layer

```python
from senti_os.core.faza30_9 import (
    get_integration_layer,
    IntegrationType,
    enable_integration
)

# Get integration layer
layer = get_integration_layer()

# Enable specific integration
enable_integration(IntegrationType.GOVERNANCE)

# Register handler
def governance_handler(payload):
    print("Governance event:", payload)

layer.register_handler(IntegrationType.GOVERNANCE, governance_handler)

# Send messages
layer.notify_governance("spec_validated", {"spec": "data"})
```

## Error Handling

The pipeline is designed to fail gracefully at each stage:

```python
result = process_natural_language("Some input")

if not result.success:
    print("Failed at stage:", result.stage.value)
    print("Errors:", result.errors)
    print("Warnings:", result.warnings)

    # Access partial results
    if result.extracted_spec:
        print("Extraction succeeded")

    if result.generated_spec:
        print("Generation succeeded")
```

## Testing

### Run Tests

```bash
PYTHONPATH=/home/pisarna/senti_system:$PYTHONPATH python3 tests/test_faza30_9.py
```

### Test Coverage

The test suite covers:

- SpecExtractor: Extraction from natural language
- SpecGenerator: SESY specification generation
- SpecSanitizer: Sensitive information removal
- SpecValidator: Safety and completeness validation
- PromptBuilder: LLM prompt generation
- PlanBuilder: Build plan generation
- Controller: End-to-end pipeline
- IntegrationLayer: Integration patterns
- EventHooks: Event emission
- End-to-end workflows

## Best Practices

### 1. Always Validate

```python
result = process_natural_language(input_text)

# Always check validation report
if result.validation_report:
    if result.validation_report.is_blocked():
        print("Validation blocked, cannot proceed")
        return
```

### 2. Use Strict Validation for Production

```python
controller = SpecEngineController()
result = controller.process(
    input_text,
    strict_validation=True  # Blocks on any errors
)
```

### 3. Verify Sanitization

```python
from senti_os.core.faza30_9 import SpecSanitizer

sanitizer = SpecSanitizer()
sanitized = sanitizer.sanitize(spec)

# Verify safety
is_safe, found = sanitizer.validate_sanitization(sanitized)
if not is_safe:
    print("Sanitization incomplete:", found)
```

### 4. Monitor Events

```python
from senti_os.core.faza30_9 import get_event_hooks

hooks = get_event_hooks()

# Get event summary
summary = hooks.get_event_summary()
print("Events emitted:", summary["total_events"])
```

### 5. Handle Failures Gracefully

```python
result = process_natural_language(input_text)

if result.success:
    # Use outputs
    pass
else:
    # Check partial results
    if result.extracted_spec:
        # Extraction worked, use that
        pass

    # Request self-healing if needed
    from senti_os.core.faza30_9 import get_integration_layer

    layer = get_integration_layer()
    layer.request_self_healing(
        error=result.errors[0],
        context={"stage": result.stage.value}
    )
```

## API Reference

### Main Functions

- `process_natural_language(text, name=None)` - Process input through pipeline
- `sanitize_spec(spec)` - Sanitize specification
- `validate_spec(spec)` - Validate specification
- `build_prompt(spec)` - Build LLM prompt
- `build_plan(spec, sanitized)` - Build compilation plan

### Classes

- `SpecEngineController` - Main orchestration controller
- `SpecExtractor` - Extract from natural language
- `SpecGenerator` - Generate SESY specifications
- `SpecSanitizer` - Sanitize specifications
- `SpecValidator` - Validate specifications
- `PromptBuilder` - Build LLM prompts
- `PlanBuilder` - Build compilation plans
- `IntegrationLayer` - Integration interface
- `EventHooks` - Event emission

### Data Classes

- `ExtractedSpec` - Extracted specification data
- `SESYSpec` - SESY-format specification
- `ValidationReport` - Validation results
- `PipelineResult` - Pipeline execution result
- `BuildPlan` - Complete build plan

## Troubleshooting

### Issue: Validation Blocked

**Problem:** Pipeline blocked at validation stage

**Solution:**
```python
# Check validation report
if result.validation_report:
    print("Errors:", result.validation_report.errors)
    print("Checks failed:", result.validation_report.checks_failed)

    # Modify input and retry
```

### Issue: Sanitization Incomplete

**Problem:** Sensitive terms found after sanitization

**Solution:**
```python
# Check sanitization report
sanitizer = SpecSanitizer()
report = sanitizer.get_sanitization_report(original, sanitized)
print("Found sensitive:", report["found_sensitive_terms"])

# Manual sanitization if needed
```

### Issue: Extraction Too Short

**Problem:** Input text insufficient for extraction

**Solution:**
```python
# Provide more detailed input
input_text = """
Create a component that validates user input.

Requirements:
- Must validate email addresses
- Must validate phone numbers
- Must return structured validation results

Constraints:
- No external dependencies
- No network access
"""

result = process_natural_language(input_text)
```

## Version

- **Version:** 1.0.0
- **Phase:** FAZA 30.9
- **Python:** 3.12+
- **Dependencies:** Standard library only

## See Also

- FAZA 16: LLM Manager and Router
- FAZA 27: Graph Expansion
- FAZA 28: Security Manager
- FAZA 29: Governance Layer
- FAZA 30: Self-Healing System
