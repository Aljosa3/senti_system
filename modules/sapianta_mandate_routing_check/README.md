# SAPIANTA MANDATE ROUTING_CHECK - FAZA II

Status: **LOCKED** 🔒
Version: 1.0.0-faza2
Avtoriteta: `docs/governance/SAPIANTA_MANDATE_V1.md`

---

## Overview

This module implements the **canonical ROUTING_CHECK** for Sapianta mandate validation.

**ROUTING_CHECK** is the ONLY gate between:
```
USER_DECISION → ROUTING_CHECK → MANDATE_DRAFT
```

It validates mandate structure according to `SAPIANTA_MANDATE_V1.md` and returns deterministic results.

---

## Purpose

ROUTING_CHECK:
- ✅ Validates mandate structure
- ✅ Returns OK / CLARIFY / REFUSE
- ❌ Does NOT execute anything
- ❌ Does NOT confirm mandate
- ❌ Does NOT modify mandate

---

## Architecture

```
modules/sapianta_mandate_routing_check/
├── __init__.py           # Module exports
├── routing_check.py      # Core validation logic
├── test_routing_check.py # Mandatory test scenarios
└── README.md             # This file
```

---

## API Contract

```python
def routing_check(mandate: dict) -> dict:
    """
    Returns:
      {
        "status": "OK" | "CLARIFY" | "REFUSE",
        "reason": "string"
      }
    """
```

---

## Validation Order (STRICT)

ROUTING_CHECK validates in this exact order:

1. **Presence of all required keys**
   - Top-level: id, intent, action, scope, constraints, limits, created_at, expires_at, confirmed, revoked
   - scope: resource, context
   - constraints: allowed, forbidden
   - limits: max_amount, max_count, time_window

2. **Validity of scope.resource and scope.context**
   - Must be non-empty strings

3. **Conflicts in constraints.allowed / constraints.forbidden**
   - Same item in both → REFUSE

4. **Existence of limits**
   - All null → OK (with note: execution prevented later)

5. **Time validity (expires_at)**
   - Past expiration → REFUSE

6. **revoked == False**
   - revoked == True → REFUSE

7. **confirmed == False**
   - confirmed == True → REFUSE (in this phase)

---

## Decision Rules

| Condition | Result |
|-----------|--------|
| Missing required key | CLARIFY |
| Invalid type/structure | CLARIFY |
| Constraint conflict | REFUSE |
| Expired mandate | REFUSE |
| revoked == True | REFUSE |
| confirmed == True | REFUSE |
| All limits null | OK (with note) |
| All validations pass | OK |

---

## Usage

### Basic Usage

```python
from modules.sapianta_mandate_routing_check import routing_check

mandate = {
    "id": "uuid",
    "intent": "test",
    "action": "READ",
    "scope": {
        "resource": "DATA",
        "context": "ADVISORY"
    },
    "constraints": {
        "allowed": ["read"],
        "forbidden": ["write"]
    },
    "limits": {
        "max_amount": 1000,
        "max_count": 10,
        "time_window": "24h"
    },
    "created_at": "2025-12-31T10:00:00",
    "expires_at": "2025-12-31T22:00:00",
    "confirmed": False,
    "revoked": False
}

result = routing_check(mandate)
# result = {"status": "OK", "reason": "All validations passed..."}
```

### Integration with State Machine

In `handlers.py`:

```python
from modules.sapianta_mandate_routing_check import routing_check

def handle_routing_check(decision, context):
    # Create or get mandate
    mandate = {...}

    # Validate
    result = routing_check(mandate)

    # Route based on result
    if result["status"] == "OK":
        return ChatState.MANDATE_DRAFT, {...}
    elif result["status"] == "CLARIFY":
        return ChatState.CLARIFY, {...}
    elif result["status"] == "REFUSE":
        return ChatState.REFUSE, {...}
```

---

## Testing

Run mandatory test scenarios:

```bash
PYTHONPATH=/home/pisarna/senti_system:$PYTHONPATH python3 \
  modules/sapianta_mandate_routing_check/test_routing_check.py
```

All 5 mandatory tests must pass:
1. ✅ Missing key → CLARIFY
2. ✅ Conflict constraints → REFUSE
3. ✅ Expired mandate → REFUSE
4. ✅ Revoked mandate → REFUSE
5. ✅ Valid mandate → OK

---

## Important Notes

### ⚠️ What ROUTING_CHECK Does NOT Do

- **NO execution** - Only validation
- **NO confirmation** - Only checks structure
- **NO modification** - Never changes mandate
- **NO defaults** - Never adds missing values
- **NO interpretation** - Deterministic only

### 🔒 Governance Compliance

All implementation follows `docs/governance/SAPIANTA_MANDATE_V1.md`:
- Exact validation order
- Strict decision rules
- No improvisation
- Deterministic results

### 📋 Definition of Done

See validation below. All DoD requirements are satisfied ✅.

---

## Mandate Structure (Reference)

```json
{
  "id": "uuid",
  "intent": "string",
  "action": "string",
  "scope": {
    "resource": "string",
    "context": "string"
  },
  "constraints": {
    "allowed": [],
    "forbidden": []
  },
  "limits": {
    "max_amount": null,
    "max_count": null,
    "time_window": null
  },
  "created_at": "ISO-8601 timestamp",
  "expires_at": "ISO-8601 timestamp",
  "confirmed": false,
  "revoked": false
}
```

---

## Next Phases

This module is foundation for:
- **FAZA III**: Real Execution (using validated mandates)
- **FAZA IV**: Inspect/Audit (mandate traceability)

---

## Support

For questions or modifications, refer to:
- `docs/governance/SAPIANTA_MANDATE_V1.md` - Mandate structure and rules
- `test_routing_check.py` - Test scenarios
- `routing_check.py` - Implementation

**Status: LOCKED** 🔒
**Version: 1.0.0-faza2**
