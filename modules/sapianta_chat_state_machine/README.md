# SAPIANTA CHAT STATE MACHINE - FAZA I

Status: **LOCKED** 🔒
Version: 1.0.0-faza1
Avtoriteta: `docs/governance/SAPIANTA_CHAT_CORE.md`

---

## Overview

This module implements the **canonical state machine** for Sapianta Chat, following strict governance rules defined in `SAPIANTA_CHAT_CORE.md`.

**FAZA I** provides the minimal, locked foundation:
- 11-state state machine
- Strict transition enforcement
- Advisory mode (not autonomous)
- Explicit mandate confirmation
- Stub execution (no real actions)

---

## Architecture

```
modules/sapianta_chat_state_machine/
├── __init__.py          # Module exports
├── state.py             # State and response type definitions
├── transitions.py       # Transition rules and validation
├── handlers.py          # Handler for each state
├── machine.py           # Core ChatStateMachine class
├── execution_stub.py    # Stub execution (FAZA I only)
├── test_faza1_scenarios.py  # Mandatory test scenarios
├── DOD_VALIDATION.md    # Definition of Done validation
└── README.md            # This file
```

---

## States

The system has **11 canonical states**:

1. **IDLE** - Waiting for user input
2. **INTENT_RECEIVED** - Analyzing user intent
3. **ADVISORY** - Presenting options (⭐ marks optimal)
4. **USER_DECISION** - Waiting for explicit user choice
5. **ROUTING_CHECK** - Validating decision against constraints
6. **MANDATE_DRAFT** - Creating mandate structure
7. **MANDATE_CONFIRM** - Waiting for explicit confirmation
8. **EXECUTION** - Executing mandate (passthrough state)
9. **RESULT** - Presenting execution results
10. **CLARIFY** - Requesting clarification
11. **REFUSE** - Refusing invalid request

---

## Absolute Rules

### 🚫 NO EXECUTION WITHOUT MANDATE_CONFIRM

The **absolute governance rule**:
- EXECUTION can ONLY be reached from MANDATE_CONFIRM
- Any other path is blocked by `TransitionRules`
- Runtime validation enforces this rule

### 🤝 EXPLICIT CONFIRMATION REQUIRED

- Advisory ≠ Decision ≠ Execution
- System can recommend (⭐) but cannot decide
- User MUST explicitly confirm mandate
- Silence = no action

### 🛑 NEGATIVE FLOWS STOP SYSTEM

- Unclear input → CLARIFY → IDLE
- Invalid request → REFUSE → IDLE
- No decision → IDLE
- Rejection → IDLE

---

## Usage

### Basic Usage

```python
from modules.sapianta_chat_state_machine import ChatStateMachine

# Create machine
machine = ChatStateMachine()

# Handle user input
response = machine.handle_input("I want to analyze data")

# Check current state
print(machine.get_current_state())  # ChatState.INTENT_RECEIVED

# Get structured response
print(response)
# {
#     "state": ChatState.INTENT_RECEIVED,
#     "type": ResponseType.ADVISORY,
#     "message": "...",
#     "data": {...}
# }
```

### Full Flow Example

```python
machine = ChatStateMachine()

# 1. User input
response = machine.handle_input("I want to process data")
# State: IDLE → INTENT_RECEIVED → ADVISORY

# 2. User sees options (⭐ marks optimal)
response = machine.handle_input("more info")
# State: ADVISORY (presents options)

# 3. User makes decision
response = machine.handle_input("choose option B")
# State: USER_DECISION → ROUTING_CHECK → MANDATE_DRAFT → MANDATE_CONFIRM

# 4. User explicitly confirms
response = machine.handle_input("confirm")
# State: MANDATE_CONFIRM → EXECUTION → RESULT → IDLE

# 5. System returns to IDLE
# Ready for next interaction
```

### Checking Transitions

```python
# Get allowed transitions from current state
allowed = machine.get_allowed_transitions()

# Check if specific transition is allowed
can_execute = machine.can_transition_to(ChatState.EXECUTION)
# False (if not in MANDATE_CONFIRM)
```

---

## Testing

Run mandatory test scenarios:

```bash
PYTHONPATH=/home/pisarna/senti_system:$PYTHONPATH python3 \
  modules/sapianta_chat_state_machine/test_faza1_scenarios.py
```

All 5 scenarios must pass:
1. ✅ No EXECUTION without MANDATE_CONFIRM
2. ✅ Silence in USER_DECISION → IDLE
3. ✅ Unclear input → CLARIFY
4. ✅ Violation → REFUSE
5. ✅ EXECUTION → RESULT → IDLE

---

## Response Structure

Every response has this structure:

```python
{
    "state": ChatState,       # Current state (enum)
    "type": ResponseType,     # ADVISORY, CLARIFY, REFUSE, CONFIRMATION, RESULT, ACKNOWLEDGMENT
    "message": str,           # Human-readable message
    "data": dict              # Optional additional data
}
```

---

## Important Notes

### ⚠️ This is FAZA I - Stub Implementation

- **Execution is FAKE** - `ExecutionStub` does NOT perform real actions
- Real execution will be implemented in **FAZA III**
- This module provides the **locked foundation** for future phases

### 🔒 Governance Compliance

All implementation follows `docs/governance/SAPIANTA_CHAT_CORE.md`:
- No improvisation
- No optimization beyond spec
- No additional features
- Strict adherence to DoD

### 📋 Definition of Done

See `DOD_VALIDATION.md` for full DoD checklist.
**Status: ALL REQUIREMENTS SATISFIED** ✅

---

## Next Phases

This module serves as foundation for:
- **FAZA II**: Mandate Pipeline (constraints, validation)
- **FAZA III**: Real Execution (module integration)
- **FAZA IV**: Inspect Integration (audit, trace)

---

## Support

For questions or modifications, refer to:
- `docs/governance/SAPIANTA_CHAT_CORE.md` - Governance rules
- `DOD_VALIDATION.md` - Implementation validation
- `test_faza1_scenarios.py` - Test scenarios

**Status: LOCKED** 🔒
**Version: 1.0.0-faza1**
