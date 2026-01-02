# FAZA VII.b — NEGATIVE SCENARIOS & ABUSE CASES
## Draft — Risk Enumeration Before Any Execution

**Phase:** VII.b  
**Status:** DRAFT  
**Binding:** NO  
**Execution:** STILL PROHIBITED  
**Depends on:**  
- FAZA VI — Formal Lock Declaration  
- FAZA VI.a — Lock Verification Checklist  
- FAZA VI.b — Lock Enforcement Notes  
- FAZA VII — Execution Entry Conditions (Draft)  
- FAZA VII.a — Review & Hardening (Draft)  
- FAZA VIII — Execution Layer Architecture (Concept)

---

## 1. Purpose

FAZA VII.b exists to **enumerate negative scenarios and abuse cases** that could arise if execution were ever enabled.

This phase:
- introduces no execution,
- defines no technical countermeasures,
- does not prioritize usability,
- exists to **surface failure and misuse first**.

Anything not explicitly mitigated here is assumed unsafe.

---

## 2. Classification Method

Scenarios are grouped by **failure origin**, not by implementation.

Each scenario specifies:
- **Description**
- **Why it is dangerous**
- **Why it must be prevented**
- **Required posture** (always prohibited / requires future phase)

No scenario in this document is allowed by default.

---

## 3. Category A — Implicit Execution

### A1: Execution via Conversational Language
**Description:**  
User phrasing implies action (“go ahead”, “do it now”) without explicit consent format.

**Danger:**  
Natural language ambiguity bypasses formal authorization.

**Posture:**  
Always prohibited.

---

### A2: Execution via Context Accumulation
**Description:**  
Multiple benign messages cumulatively imply an action.

**Danger:**  
Intent inference replaces consent.

**Posture:**  
Always prohibited.

---

### A3: Execution via Confirmation Fatigue
**Description:**  
User repeatedly confirms until the system assumes permission.

**Danger:**  
Consent becomes coerced or implicit.

**Posture:**  
Always prohibited.

---

## 4. Category B — Scope Escalation

### B1: “While You’re At It” Expansion
**Description:**  
Execution layer performs additional actions beyond explicit scope.

**Danger:**  
Scope creep creates unbounded side effects.

**Posture:**  
Always prohibited.

---

### B2: Auto-Retry with Modified Parameters
**Description:**  
Execution retries with adjusted parameters after failure.

**Danger:**  
System becomes an optimizer, not executor.

**Posture:**  
Always prohibited.

---

### B3: Partial Success Masking
**Description:**  
System reports success while parts failed.

**Danger:**  
User loses accurate situational awareness.

**Posture:**  
Always prohibited.

---

## 5. Category C — Autonomy Drift

### C1: Execution Initiated by System Suggestion
**Description:**  
System proposes and executes an action proactively.

**Danger:**  
Decision authority shifts from human to system.

**Posture:**  
Always prohibited.

---

### C2: Background or Scheduled Execution
**Description:**  
Execution occurs without immediate human presence.

**Danger:**  
Removes real-time accountability.

**Posture:**  
Requires explicit future phase (never default).

---

### C3: Self-Healing Execution
**Description:**  
System modifies behavior to “fix” issues autonomously.

**Danger:**  
Unbounded autonomy under the guise of safety.

**Posture:**  
Always prohibit
