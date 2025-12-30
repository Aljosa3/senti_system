# Sapianta Chat ↔ Mandate Bridge — Phase V.1

Status: READ-ONLY  
Authority: NONE  
Execution: FORBIDDEN  

---

## Purpose

This module connects chat input to the mandate system.

It exists to:
- Bridge chat intent detection with mandate validation
- Provide a unified, explainable interpretation of user input
- Prepare higher phases for controlled execution (future)

It does NOT:
- Execute actions
- Grant permissions
- Modify state
- Escalate authority

---

## Behavior

Input → Intent Detection → Mandate Validation → Intent Binding → Explanation

All steps are:
- Deterministic
- Read-only
- Explainable

---

## Output

The bridge always returns a structured explanation containing:
- Detected intent
- Validated mandate (or rejection)
- Binding result
- Advisory constraints
- Execution status (always false)

---

## Governance

Phase: V.1  
Execution Allowed: NO  
Lock Required: PHASE_V1_LOCK
