# PHASE 78.0 — READ-ONLY UX EXPANSION
## Boundary Specification

Status: ACTIVE  
Phase: 78.0  
Scope: CLI User Experience (Read-Only)  
Authority: Core-Locked (Phase 72)

---

## 0. PURPOSE

This document authorizes a **read-only UX expansion**
for the Sapianta Chat CLI module.

Phase 78 introduces:
- improved textual presentation
- summarized views of existing documents
- user-friendly command outputs

No new IO capabilities are introduced.
No execution or mutation authority is granted.

---

## 1. HARD CONSTRAINTS (LOCKED)

All UX expansion MUST:
- reuse existing read-only data sources (Phase 77)
- introduce no new file access
- introduce no execution logic
- preserve Phase 74–77 invariants
- remain advisory-only

Violation of any constraint → **ABORT**.

---

## 2. ALLOWED UX ENHANCEMENTS

The following enhancements are explicitly allowed:

### 2.1 Structured Output

- sectioned text output
- headings and separators
- concise summaries
- trimmed excerpts of documents

---

### 2.2 Command-Level UX Improvements

Existing commands MAY be enhanced:

#### `status`
- display concise module overview
- summarize module states
- avoid dumping full documents

#### `describe module <id>`
- extract and display:
  - purpose
  - capabilities
  - restrictions
  - lifecycle state

#### `describe phase <id>`
- display:
  - phase purpose
  - scope
  - current status
- omit implementation details by default

---

### 2.3 Helper Logic (Pure)

- string parsing
- markdown trimming
- line filtering
- static pattern matching

All helper logic MUST be:
- pure
- deterministic
- side-effect free

---

## 3. EXPLICITLY FORBIDDEN

The UX layer MUST NOT:

- read additional files
- infer undocumented semantics
- cache document contents
- modify documents
- generate machine-actionable output
- introduce interactive prompts

---

## 4. FILE SCOPE (NO EXPANSION)

UX enhancements MUST be implemented only in:

- `modules/sapianta_chat_cli/cli/renderer.py`
- `modules/sapianta_chat_cli/utils/text_helpers.py`
- optionally `cli/command_parser.py` (mapping only)

No new files or directories may be added.

---

## 5. ERROR PRESENTATION RULES

Errors:
- MUST remain descriptive
- MUST reference governing Phase when relevant
- MUST NOT suggest corrective actions involving execution

---

## 6. VALIDATION CHECKLIST (FOR AI)

Before implementation, AI MUST confirm:

- [ ] no new file reads introduced
- [ ] no new IO categories introduced
- [ ] no execution paths added
- [ ] UX logic is purely presentational
- [ ] all data originates from Phase 77 readers

Failure of any check → **ABORT**.

---

## 7. FINAL STATEMENT

This document authorizes **read-only UX improvements**
for the Sapianta Chat CLI.

Any further capability expansion requires:
- a new Phase
- an updated boundary specification

**PHASE 78.0 — READ-ONLY UX BOUNDARY ENFORCED**
