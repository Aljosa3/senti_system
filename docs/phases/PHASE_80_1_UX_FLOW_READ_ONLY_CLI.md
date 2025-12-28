# PHASE 80.1 — UX FLOW (READ-ONLY CLI)

Status: ACTIVE  
Phase: 80.1  
Scope: UX Flow  
Applies to: Sapianta Chat CLI  
Authority: Core-Locked (Phase 72)

---

## 0. PURPOSE

This document defines **how humans actually interact**
with the Sapianta Chat CLI in day-to-day use.

The focus is:
- clarity
- predictability
- explainability

No new commands are introduced.
No behavior is changed.

---

## 1. GENERAL UX PRINCIPLES

The CLI MUST:
- be calm and non-technical where possible
- avoid jargon unless necessary
- explain errors instead of fixing them
- act as a guide, not an executor

The CLI is **not** a shell.
The CLI is **not** an automation tool.

---

## 2. TYPICAL USER FLOWS

### 2.1 FIRST CONTACT (ORIENTATION)

User intent:
> “What is this system?”

Flow:
- `status`
- `read registry`
- `describe module sapianta_chat_cli`

Expected outcome:
- user understands scope
- user understands limitations
- no confusion about authority

---

### 2.2 GOVERNANCE UNDERSTANDING

User intent:
> “What is allowed and what is not?”

Flow:
- `describe phase 72`
- `read phase 74.2`
- `read mpd sapianta_chat_cli`

Expected outcome:
- clear boundary awareness
- reduced misuse risk
- audit-friendly explanation

---

### 2.3 AUDIT / REVIEW SESSION

User intent:
> “Verify integrity without touching anything.”

Flow:
- `status`
- `read registry`
- `read phase 79.1`
- `read phase 79.2`

Expected outcome:
- confidence in Core Lock
- proof of non-executability
- zero system impact

---

### 2.4 DAILY OWNER REFERENCE

User intent:
> “Remind me where things are.”

Flow:
- `status`
- `describe phase <current>`
- `read registry`

Expected outcome:
- fast recall
- no need to search files manually

---

## 3. ERROR UX (IMPORTANT)

Errors MUST:
- state what is not allowed
- reference the relevant Phase or rule
- avoid suggesting actions
- avoid technical stack traces

Example:
> “This command is not available.  
> See Phase 74.2 — Behavior & Command Spec.”

Errors are **educational**, not corrective.

---

## 4. OUTPUT STYLE

Output SHOULD:
- be structured
- be readable without context
- avoid excessive verbosity
- prefer explanation over raw data

No colors.
No ASCII art.
No interactivity beyond text.

---

## 5. WHAT THIS PHASE DOES NOT DO

This phase does NOT:
- add commands
- change parsing logic
- alter renderer behavior
- introduce state or memory
- enable execution

It documents **usage only**.

---

## 6. SUCCESS CRITERIA

Phase 80.1 is successful if:
- new users understand the system faster
- audits require less explanation
- the CLI feels trustworthy, not dangerous

---

## 7. FINAL STATEMENT

Phase 80.1 formalizes the CLI as a
**human-facing governance interface**.

It completes the transition from
“tool that exists” to “tool that is used”.

PHASE 80.1 — UX FLOW ESTABLISHED
