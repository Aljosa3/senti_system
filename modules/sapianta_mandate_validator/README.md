# Sapianta Mandate Validator — Phase II.2

**Status:** READ-ONLY  
**Authority:** NONE  
**Execution:** FORBIDDEN  

---

## Purpose

This module validates whether a textual mandate is:

- Recognized
- Defined in the approved mandate vocabulary
- Safe to acknowledge

It does NOT:
- Execute anything
- Grant permissions
- Trigger modules
- Escalate authority

This module exists solely for governance validation.

---

## Behavior

Input → Validation → Explanation

The validator always returns a structured explanation.
No side effects occur.

Execution is **never allowed** in Phase II.2.

---

## Example

```python
from sapianta_mandate_validator.validator import validate_mandate

result = validate_mandate("analyze")
