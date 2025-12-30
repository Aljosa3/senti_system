# Sapianta Mandate → Intent Binding — Phase II.3

**Status:** READ-ONLY  
**Authority:** NONE  
**Execution:** FORBIDDEN  

---

## Purpose

This module binds a validated mandate to an abstract intent.

It exists to:
- Give semantic meaning to mandates
- Prepare future routing logic
- Preserve strict non-execution guarantees

It does NOT:
- Execute actions
- Trigger modules
- Grant permissions
- Escalate authority

---

## Binding Rules

The binding is deterministic and static.

| Mandate   | Intent   |
|-----------|----------|
| ANALYZE   | QUESTION |
| DESCRIBE  | META     |
| EXPLAIN   | QUESTION |
| SUMMARIZE | META     |
| CLASSIFY  | META     |
| REFLECT   | META     |

All other mandates result in `NO_BINDING`.

---

## Example

```python
from sapianta_mandate_intent_binding.binder import bind_mandate_to_intent

result = bind_mandate_to_intent("ANALYZE")
