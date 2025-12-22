# PHASE 66 — ENTRY CHECKLIST

Status: OPERATIVE  
Applies after: Phase 65 hard-lock (`phase65-hard-lock`)  
Purpose: Safe continuation of development without modifying Core governance

---

## 0. PREREQUISITES (MUST BE TRUE)

Phase 66 MUST NOT begin unless ALL of the following are true:

- [x] Phase 65 is hard-locked (commit + tag exist)
- [x] Phase 65 governance documents are immutable
- [x] Phase 65 Closure Summary exists
- [x] PHASE_66_ENTRY.md exists
- [x] No unresolved Phase 65 governance conflicts remain

If any item is false → Phase 66 MUST NOT start.

---

## 1. ABSOLUTE PROHIBITIONS (DO NOT TOUCH)

During Phase 66, it is FORBIDDEN to:

- modify any Phase 65 governance document
- reinterpret Phase 65 terminology (execution, autonomy, authority)
- introduce temporary exceptions or workarounds
- bypass governance through UX or tooling
- introduce global decision centers
- create agent-like execution loops
- optimize behavior that alters authority boundaries

If a task requires any of the above → it is NOT Phase 66 work.

---

## 2. PERMITTED SCOPE (SAFE ZONE)

Phase 66 MAY include work on:

- modules below the governance boundary
- controlled and exploratory layers only
- systems that analyze, simulate, observe, or propose
- automation without decision authority
- performance optimization without rule changes
- new interfaces that respect Phase 65 authority model

Rule:
> Capability may increase. Authority may not.

---

## 3. ESCALATION RULE (MANDATORY)

If at any point a question arises:

“Does this potentially affect Phase 65?”

Then Phase 66 work MUST:

1. Halt immediately
2. Explicitly identify the Phase 65 rule at risk
3. Escalate for conscious review
4. Await explicit authorization

Silent adaptation or workaround is a violation.

---

## 4. EXPERIMENTATION REQUIREMENTS

All Phase 66 experiments MUST be:

- non-invasive
- reversible
- isolated
- traceable
- independent of Phase 65 modification

If an experiment cannot be removed cleanly → it is NOT allowed.

---

## 5. RECOMMENDED INITIAL ACTIVITIES

Safe starting points for Phase 66 include:

- mapping future modules (no implementation)
- defining interfaces without authority
- simulation pipelines (input → analysis → output)
- observability and logging
- controlled “what-if” scenarios

---

## 6. PRE-COMMIT CHECK QUESTIONS

Before ANY Phase 66 commit, verify:

- Would this still work if Chat Core did not exist?
- Could this become agent-like without new rules?
- Does this change who decides?
- Does this require reinterpretation of Phase 65?

If ANY answer is YES → STOP.

---

## 7. FORMAL START OF PHASE 66

Phase 66 is considered started when the first commit:

- does not modify governance
- operates below Phase 65 boundary
- is clearly marked as Phase 66 work

Recommended commit prefix:
phase66(<area>): <description>

---

## 8. DOCUMENT STATUS

This checklist is:

- operational
- non-normative
- non-authoritative
- intended as a safety reference

It does NOT override Phase 65 governance.

---

End of Phase 66 Entry Checklist
