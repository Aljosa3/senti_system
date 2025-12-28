# PHASE 76.0 — CONTROLLED IO
## Boundary Specification (Specification-Only)

Status: ACTIVE  
Phase: 76.0  
Scope: Controlled Input / Output  
Authority: Core-Locked (Phase 72)

---

## 0. PURPOSE

This document defines the **absolute boundary for introducing IO**
into the Senti / Sapianta system.

Phase 76 is **specification-only**.
No IO is implemented in this phase.

The goal is to define:
- which IO categories MAY exist
- under which conditions they MAY be used
- which IO remains permanently forbidden

---

## 1. HARD CONSTRAINTS (LOCKED)

Controlled IO MUST:
- comply with Core Lock (Phase 72)
- preserve Phase 74 invariants
- preserve Phase 75 observability guarantees
- introduce no execution authority
- introduce no mutation authority

Violation of any constraint → **ABORT**.

---

## 2. IO CATEGORIES (EXPLICIT)

### 2.1 ALLOWED IO CATEGORIES (FUTURE PHASES ONLY)

The following IO categories MAY be introduced **in later phases**:

#### A. File READ (Strict)
- read-only access
- explicit file allowlist
- no directory traversal
- no globbing
- no dynamic paths

#### B. Stdout / Text Output
- human-readable only
- advisory only
- no machine-parsable contracts

#### C. Configuration READ
- static configuration
- read-only
- no environment mutation

---

### 2.2 FORBIDDEN IO CATEGORIES (GLOBAL)

The following IO is **permanently forbidden**:

- File WRITE
- File DELETE
- Network IO (any protocol)
- Environment variable WRITE
- Process spawning
- Shell execution
- IPC / sockets
- Device access

Presence of any forbidden IO = **critical violation**.

---

## 3. IO ESCALATION MODEL

Any IO introduction MUST:
- be phase-gated
- reference this document
- update the module MPD
- be reviewed before implementation

No implicit IO escalation is allowed.

---

## 4. IO BINDING RULES

- IO MUST be explicit
- IO MUST be minimal
- IO MUST be isolated
- IO MUST be inspectable
- IO MUST be reversible

Hidden or indirect IO is forbidden.

---

## 5. OBSERVABILITY PRESERVATION

Introducing IO MUST NOT:
- bypass observability boundaries
- introduce hidden side channels
- reduce visibility guarantees
- affect control flow silently

Observability remains **passive**.

---

## 6. VALIDATION CHECKLIST (FOR AI)

Before any IO implementation, AI MUST confirm:

- [ ] IO category is explicitly allowed
- [ ] IO is read-only
- [ ] no execution is introduced
- [ ] no mutation is introduced
- [ ] MPD is updated
- [ ] new Phase exists authorizing IO

Failure of any check → **ABORT**.

---

## 7. FINAL STATEMENT

This document locks the **Controlled IO boundary**
for all future phases.

No IO may be implemented without:
- a dedicated Phase
- explicit scope
- MPD update

**PHASE 76.0 — CONTROLLED IO BOUNDARY ENFORCED**
