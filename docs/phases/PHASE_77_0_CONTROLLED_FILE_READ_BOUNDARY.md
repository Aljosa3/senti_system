# PHASE 77.0 — CONTROLLED FILE READ
## Boundary Specification (Implementation Gate)

Status: ACTIVE  
Phase: 77.0  
Scope: File READ (Read-Only)  
Authority: Core-Locked (Phase 72)

---

## 0. PURPOSE

This document authorizes the **first real IO implementation**
in the Senti / Sapianta system: **controlled, read-only file access**.

This phase:
- permits reading a **strict allowlist** of documentation files
- introduces **no execution authority**
- introduces **no mutation authority**

---

## 1. HARD PREREQUISITES (LOCKED)

Implementation is allowed **only if all are true**:

- Phase 76 Review is COMPLETE
- Module `sapianta_chat_cli` is ACTIVE
- MPD exists and specifies:
  - Execution: NO
  - Mutation: NO
  - IO: READ-ONLY (File)

If any prerequisite fails → **ABORT IMPLEMENTATION**.

---

## 2. ALLOWED FILE READ SCOPE (ALLOWLIST)

Only the following files MAY be read:

### 2.1 Registry

- `/senti_system/docs/modules/REGISTRY.md`

---

### 2.2 Module Permission Descriptors (MPD)

- `/senti_system/docs/modules/mpd/*.md`

Constraints:
- filename must exactly match `<MODULE_ID>_MPD.md`
- no directory traversal
- no wildcard expansion at runtime

---

### 2.3 Phase Documents

- `/senti_system/docs/phases/PHASE_*.md`

Constraints:
- exact filename resolution
- no recursive directory scans
- no globbing in code

---

## 3. PATH RESOLUTION RULES (CRITICAL)

- all paths MUST be absolute
- paths MUST be constructed from constants
- user input MUST NOT directly map to filesystem paths
- no `..`, no symlinks, no environment-based resolution

Violation → **CRITICAL GOVERNANCE BREACH**.

---

## 4. READ BEHAVIOR RULES

- open files in read-only mode
- read text only
- no binary reads
- no caching
- no buffering beyond necessity

Errors MUST:
- be descriptive
- reference the governing Phase
- never attempt recovery or fallback

---

## 5. FORBIDDEN ACTIONS (GLOBAL)

The implementation MUST NOT:

- write, delete, or modify any file
- read files outside the allowlist
- scan directories
- infer file existence dynamically
- expose raw filesystem errors
- log file contents outside CLI output

---

## 6. OBSERVABILITY INTEGRATION

- every file read MAY be observed
- observability MUST remain passive
- no side channels allowed
- no hidden reads permitted

---

## 7. VALIDATION CHECKLIST (FOR AI)

Before implementation, AI MUST confirm:

- [ ] allowlist is exact and minimal
- [ ] no wildcard resolution in code
- [ ] no path traversal possible
- [ ] MPD updated (if required)
- [ ] implementation confined to approved module

Failure of any check → **ABORT**.

---

## 8. FINAL STATEMENT

This document authorizes **controlled, read-only file access**
for the Sapianta Chat CLI module.

Any expansion of file access requires:
- a new Phase
- an updated boundary specification
- an MPD review

**PHASE 77.0 — CONTROLLED FILE READ BOUNDARY ENFORCED**
