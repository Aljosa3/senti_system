# FAZA 13 – Senti OS Prediction Engine

**Version:** 1.0.0
**Status:** Active
**Integration:** FAZA 5, 6, 7, 8, 12

---

## Overview

FAZA 13 implements predictive capabilities for Senti OS, enabling the system to forecast future states, predict potential failures, recommend actions, and anticipate user behavior. The Prediction Engine integrates with:

- **FAZA 12** (Adaptive Memory Engine) - for accessing Working, Episodic, and Semantic memory
- **FAZA 5** (AI Operational Layer) - for AI-driven predictions
- **FAZA 6** (Autonomous Task Loop) - for periodic prediction execution
- **FAZA 8** (Security Manager) - for validation and high-risk alerts

---

## Architecture

The Prediction Engine consists of 6 core components:

### 1. **PredictionEngine** (`prediction_engine.py`)
**Purpose:** Low-level prediction mechanism

**Capabilities:**
- State forecasting based on Working Memory
- Failure prediction based on Episodic Memory patterns
- Action recommendations based on Semantic Knowledge
- User behavior prediction based on recent actions
- Statistical analysis (trends, frequencies, moving averages)

**Key Classes:**
- `PredictionResult` - Data structure for prediction results
- `PredictionEngine` - Core prediction logic

### 2. **PredictionManager** (`prediction_manager.py`)
**Purpose:** High-level orchestrator for prediction operations

**Capabilities:**
- Orchestrates PredictionEngine operations
- Stores predictions in Episodic Memory (FAZA 12)
- Publishes events to EventBus
- Handles multiple trigger types (time_tick, event_trigger, ai_request)
- Manages prediction history and statistics

### 3. **PredictionRules** (`prediction_rules.py`)
**Purpose:** Validation and security compliance (FAZA 8)

**Capabilities:**
- Validates prediction modes against whitelist
- Detects and blocks sensitive data predictions
- Enforces size limits on inputs and outputs
- Validates confidence and risk_score boundaries
- Integrates with FAZA 8 Security Manager

### 4. **PredictionEvents** (`prediction_events.py`)
**Purpose:** Event definitions for EventBus integration

**Event Types:**
- `PREDICTION_GENERATED` - Standard prediction event
- `PREDICTION_TRIGGER` - Trigger notification
- `HIGH_RISK_PREDICTION` - High-risk alert (risk_score > 70)
- `PREDICTION_VALIDATION` - Validation result event
- `PREDICTION_STATS` - Statistics event

### 5. **PredictionService** (`prediction_service.py`)
**Purpose:** OS-level service for FAZA 6 integration

**Capabilities:**
- Periodic prediction execution (configurable interval)
- High-risk alert handling
- Security Manager notifications
- Service statistics tracking
- Manual prediction triggering

### 6. **__init__.py** (`__init__.py`)
**Purpose:** Export layer for module access

---

## Integration Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    BOOT SEQUENCE (boot.py)                   │
│  1. Initialize MemoryManager (FAZA 12)                      │
│  2. Initialize PredictionManager (FAZA 13)                  │
│  3. Register as OS service                                   │
│  4. Pass to AI Layer (FAZA 5)                               │
│  5. Pass to Autonomous Loop (FAZA 6)                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              AI OPERATIONAL LAYER (FAZA 5)                   │
│  • PredictionManager registered in ai_layer dict            │
│  • Available to all AI components                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│           AUTONOMOUS TASK LOOP (FAZA 6)                      │
│  • Calls full_system_prediction() every ~60 seconds         │
│  • Logs high-risk predictions                                │
│  • Triggers security alerts if needed                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    PREDICTION FLOW                           │
│                                                              │
│  Working Memory ──┐                                          │
│  Episodic Memory ─┤──► PredictionEngine ──► PredictionResult│
│  Semantic Memory ─┘                │                         │
│                                    │                         │
│                                    ▼                         │
│                         PredictionRules (FAZA 8 validation) │
│                                    │                         │
│                                    ▼                         │
│                         Store in Episodic Memory (FAZA 12)  │
│                                    │                         │
│                                    ▼                         │
│                         Emit PREDICTION_GENERATED event     │
│                                    │                         │
│                                    ▼                         │
│                    ┌───────────────┴───────────────┐        │
│                    │                               │        │
│               Risk > 70?                      Risk ≤ 70    │
│                    │                               │        │
│                    ▼                               ▼        │
│         Alert Security Manager           Normal logging     │
│         Emit HIGH_RISK_PREDICTION                           │
└─────────────────────────────────────────────────────────────┘
```

---

## API Reference

### PredictionEngine

```python
from senti_core_module.senti_prediction import PredictionEngine

engine = PredictionEngine(memory_manager)

# State prediction
result = engine.predict_state(context={"key": "value"})

# Failure prediction
result = engine.predict_failure()

# Action recommendation
result = engine.predict_action(context={"task": "optimize"})

# User behavior prediction
result = engine.predict_user_behavior(["commit", "push", "commit"])

# Full system assessment
results = engine.full_system_assessment()
# Returns: {"state": result1, "failure": result2, "action": result3, "user": result4}
```

### PredictionManager

```python
from senti_core_module.senti_prediction import PredictionManager

manager = PredictionManager(memory_manager, event_bus)

# Context prediction
result = manager.predict_context({"key": "value"})

# Failure prediction
result = manager.predict_failures()

# Action prediction
result = manager.predict_actions({"task": "refactor"})

# User behavior prediction
result = manager.predict_user_behavior(["action1", "action2"])

# Full system prediction
results = manager.full_system_prediction()

# Handle triggers
manager.handle_trigger("time_tick", {})
manager.handle_trigger("event_trigger", {"event_type": "ERROR"})
manager.handle_trigger("ai_request", {"request_type": "failure"})

# Get last prediction
last = manager.get_last_prediction("failure")

# Get statistics
stats = manager.get_statistics()

# Enable/disable
manager.enable()
manager.disable()
```

### PredictionRules

```python
from senti_core_module.senti_prediction import PredictionRules

rules = PredictionRules(security_manager)

# Validate mode
valid = rules.validate_prediction_mode("state")

# Validate context
valid = rules.validate_context_data({"key": "value"})

# Validate result
valid = rules.validate_prediction_result(prediction_result)

# Full operation validation
valid = rules.validate_full_operation(
    mode="state",
    context={"key": "value"},
    result=prediction_result
)

# Get violations
violations = rules.get_violations()

# Get validation report
report = rules.get_validation_report()
```

### PredictionService

```python
from senti_core_module.senti_prediction import PredictionService

service = PredictionService(
    prediction_manager=manager,
    event_bus=event_bus,
    security_manager=security_mgr,
    interval=60  # seconds
)

# Start/stop service
service.start()
service.stop()

# Manual prediction
results = service.manual_prediction("failure")
results = service.manual_prediction()  # Full system

# Get statistics
stats = service.get_statistics()

# Change interval
service.set_interval(120)

# Reset statistics
service.reset_statistics()

# Check status
running = service.is_running()

# Get last predictions
last = service.get_last_predictions()
```

---

## PredictionResult Structure

```python
{
    "prediction": str,      # Prediction text
    "confidence": float,    # 0.0 to 1.0
    "risk_score": int,      # 0 to 100
    "source": str,          # "working", "episodic", "semantic", "hybrid"
    "timestamp": str        # ISO format
}
```

---

## Event Payloads

### PREDICTION_GENERATED

```python
{
    "category": str,        # "context", "failure", "action", "user_behavior"
    "prediction": str,
    "confidence": float,
    "risk_score": int,
    "source": str,
    "timestamp": str
}
```

### HIGH_RISK_PREDICTION

```python
{
    "prediction": str,
    "risk_score": int,      # > 70
    "category": str,
    "details": {
        "confidence": float,
        "source": str,
        "timestamp": str
    }
}
```

---

## Code Examples

### Example 1: Basic Prediction

```python
from senti_core_module.senti_prediction import PredictionManager

# Initialize (typically done in boot.py)
manager = PredictionManager(memory_manager, event_bus)

# Make a prediction
result = manager.predict_failures()

print(f"Prediction: {result.prediction}")
print(f"Confidence: {result.confidence}")
print(f"Risk Score: {result.risk_score}")

# Example output:
# Prediction: Moderate risk of failure - monitoring recommended
# Confidence: 0.75
# Risk Score: 60
```

### Example 2: Full System Assessment

```python
# Get comprehensive system prediction
results = manager.full_system_prediction()

for category, result in results.items():
    print(f"\n{category.upper()}:")
    print(f"  Prediction: {result.prediction}")
    print(f"  Risk: {result.risk_score}")
    print(f"  Confidence: {result.confidence}")
```

### Example 3: Event Listening

```python
def on_prediction_event(payload):
    print(f"New prediction: {payload['prediction']}")
    if payload['risk_score'] > 70:
        print("⚠️  HIGH RISK ALERT!")

# Subscribe to events
event_bus.subscribe("PREDICTION_GENERATED", on_prediction_event)
```

### Example 4: Validation

```python
from senti_core_module.senti_prediction import PredictionRules

rules = PredictionRules()

# Validate before prediction
context = {"task": "optimize_memory"}

if rules.validate_context_data(context):
    result = manager.predict_actions(context)

    if rules.validate_prediction_result(result):
        print("Prediction valid!")
    else:
        print("Violations:", rules.get_violations())
```

### Example 5: Periodic Service

```python
from senti_core_module.senti_prediction import PredictionService

# Create service (runs predictions every 60 seconds)
service = PredictionService(
    prediction_manager=manager,
    event_bus=event_bus,
    security_manager=security_mgr,
    interval=60
)

# Start service
service.start()

# Service will automatically:
# - Run full_system_prediction() every 60 seconds
# - Alert Security Manager on high-risk predictions
# - Publish statistics events
# - Log predictions to memory

# Later...
stats = service.get_statistics()
print(f"Total runs: {stats['service']['total_runs']}")
print(f"High-risk alerts: {stats['service']['high_risk_alerts']}")
print(f"Average risk score: {stats['service']['avg_risk_score']}")
```

---

## Security Integration (FAZA 8)

The Prediction Engine enforces strict security policies:

### Sensitive Data Protection

Predictions involving sensitive keywords are blocked:
- `password`, `secret`, `key`, `token`
- `credential`, `private_key`, `api_key`, `auth_token`

### Size Limits

- Max context size: 1000 characters
- Max action list size: 50 items
- Max prediction length: 500 characters

### Whitelisted Modes

Only these prediction modes are allowed:
- `state`, `failure`, `action`, `user_behavior`, `context`, `full_system`

### Validation Boundaries

- Confidence: Must be in [0.0, 1.0]
- Risk Score: Must be in [0, 100]
- Source: Must be in `["working", "episodic", "semantic", "hybrid", "system"]`

---

## Memory Integration (FAZA 12)

Predictions are automatically stored in Episodic Memory:

```python
# Storage format
{
    "type": "prediction",
    "category": "failure",
    "prediction": "High risk of failure detected",
    "confidence": 0.9,
    "risk_score": 90,
    "source": "episodic",
    "timestamp": "2025-12-01T10:30:00"
}
```

**Tags:**
- `"prediction"` - All predictions
- Category tag - `"context"`, `"failure"`, `"action"`, `"user_behavior"`
- `"high_risk"` - Risk score > 70

---

## Performance Characteristics

- **Prediction latency:** < 50ms (without AI model)
- **Memory overhead:** ~100KB base + history
- **Event throughput:** 100+ predictions/second
- **Periodic interval:** Configurable (default: 60s)

---

## Testing

Run FAZA 13 tests:

```bash
# Set PYTHONPATH
export PYTHONPATH=/home/pisarna/senti_system:$PYTHONPATH

# Run tests
python3 -m pytest tests/test_faza13_prediction.py -v

# Or with unittest
python3 tests/test_faza13_prediction.py
```

**Test Coverage:**
- ✅ Basic prediction output
- ✅ Confidence and risk_score boundaries
- ✅ Event emission (PREDICTION_GENERATED)
- ✅ Episodic memory integration
- ✅ Rules validation
- ✅ Prediction service periodic operation
- ✅ High-risk workflow
- ✅ Full integration tests

---

## Future Enhancements

### Planned for Future FAZAs:

1. **Machine Learning Integration**
   - Train models on historical predictions
   - Improve accuracy over time
   - Anomaly detection

2. **Advanced Patterns**
   - Seasonal trend detection
   - Multi-variate analysis
   - Correlation discovery

3. **User Feedback Loop**
   - Allow users to rate predictions
   - Adaptive confidence scoring
   - Personalized predictions

4. **Distributed Predictions**
   - Multi-agent prediction consensus
   - Distributed risk assessment
   - Collaborative forecasting

---

## Troubleshooting

### Predictions Always Low Confidence

**Cause:** Insufficient memory data
**Solution:** Ensure FAZA 12 Memory Manager is collecting data

### No Events Emitted

**Cause:** EventBus not connected
**Solution:** Verify `event_bus` parameter in PredictionManager initialization

### High Memory Usage

**Cause:** Large prediction history
**Solution:** Call `manager.clear_history()` periodically

### Service Not Running

**Cause:** Not started or crashed
**Solution:** Check logs, ensure `service.start()` was called

---

## Related Documentation

- [FAZA 12 - Adaptive Memory Engine](./FAZA_12_MEMORY_ENGINE.md)
- [FAZA 8 - Security Manager](./FAZA_8_SECURITY_MANAGER.md)
- [FAZA 6 - Autonomous Task Loop](./FAZA_6_AUTONOMOUS_LOOP.md)
- [FAZA 5 - AI Operational Layer](./FAZA_5_AI_LAYER.md)

---

## Contact & Support

For questions or issues related to FAZA 13:
- Check integration points in `boot.py`
- Review test cases in `test_faza13_prediction.py`
- Examine event logs for prediction activities

---

**Last Updated:** 2025-12-01
**Maintained By:** Senti OS Development Team
