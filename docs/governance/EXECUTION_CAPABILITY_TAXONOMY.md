# Execution Capability Taxonomy

Status: DRAFT → LOCKED (Phase VI.3)
Execution: NOT ACTIVE
Implementation: NONE

---

## Purpose

This document defines a taxonomy of execution capabilities
for future phases of the system.

It does NOT grant execution.
It does NOT implement execution.
It does NOT imply permission.

The taxonomy exists solely to prevent ambiguity,
scope creep, and silent escalation.

---

## Core Principle

Not all execution is equal.

Execution capabilities differ by:
- risk
- reversibility
- scope
- authority
- audit requirements

They must never be treated as a single category.

---

## Capability Classes

### CLASS 0 — NO_EXECUTION

Description:
- Pure advisory
- Pure inspection
- Pure explanation

Examples:
- analysis
- summarization
- explanation
- classification

Risk Level: NONE  
Default State: ALWAYS ALLOWED  

---

### CLASS 1 — LOCAL_REVERSIBLE

Description:
- Local user-side actions
- Fully reversible
- No external side effects

Examples:
- temporary file creation
- UI state changes
- ephemeral computations

Risk Level: LOW  
Default State: FORBIDDEN until explicitly enabled  

---

### CLASS 2 — LOCAL_PERSISTENT

Description:
- Local actions with persistence
- Reversible with effort
- User-owned environment

Examples:
- file writes
- configuration changes
- local database updates

Risk Level: MEDIUM  
Default State: FORBIDDEN  

---

### CLASS 3 — SYSTEM_LEVEL

Description:
- Actions affecting system state
- May affect availability or integrity

Examples:
- service restarts
- process management
- resource allocation

Risk Level: HIGH  
Default State: FORBIDDEN  

---

### CLASS 4 — EXTERNAL_SIDE_EFFECT

Description:
- Actions outside the local system
- Irreversible or partially irreversible

Examples:
- network calls
- API mutations
- financial actions
- hardware interaction

Risk Level: CRITICAL  
Default State: ABSOLUTELY FORBIDDEN  

---

## Escalation Rules

- No class may implicitly escalate to another
- Each class requires a distinct execution contract
- Higher classes require stronger consent and audit

---

## Audit Requirements

Audit strictness increases with class level:

- Class 0: optional logging
- Class 1: mandatory local audit
- Class 2: immutable audit log
- Class 3+: governance-supervised audit

---

## Phase Constraint

This taxonomy is declarative only.

No execution capability may be implemented
until a future phase explicitly enables it.
