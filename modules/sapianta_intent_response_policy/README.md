# Sapianta Intent → Advisory Response Policy — Phase II.4

Status: READ-ONLY
Authority: NONE
Execution: FORBIDDEN

---

## Purpose

This module defines how advisory responses are shaped
based solely on detected intent.

It exists to:
- Enforce non-executable response boundaries
- Prevent instruction leakage
- Prevent action-oriented output
- Preserve user sovereignty

This module does NOT:
- Execute actions
- Provide instructions
- Generate plans or steps
- Trigger modules
- Escalate authority

---

## Policy Scope

The policy operates strictly on abstract intent.

Input:
- Intent (QUESTION, REQUEST, PLAN, META, UNKNOWN)

Output:
- Advisory response constraints

The policy is deterministic and static.

---

## Intent → Advisory Constraints

QUESTION:
- Explanatory language allowed
- No conclusions
- No recommendations

REQUEST:
- Acknowledge only
- Explicit refusal of execution

PLAN:
- High-level considerations only
- No steps, sequences, or procedures

META:
- System description allowed
- No modification or extension

UNKNOWN:
- Clarification request only
- No assumptions

---

## Guarantees

- Zero execution
- Zero side effects
- Zero authority escalation
- Zero routing

This policy layer is mandatory for all future response generation.
Any violation is a governance breach.
