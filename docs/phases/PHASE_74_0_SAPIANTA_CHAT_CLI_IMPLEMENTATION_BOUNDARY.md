# PHASE 74.0 — SAPIANTA CHAT CLI
## Implementation Boundary Specification

Status: ACTIVE
Phase: 74.0
Module: Sapianta Chat CLI
Audience: ChatGPT / AI izvajalec
Authority: Core-Locked (Phase 72)

---

## 0. PURPOSE

This document defines the **exact implementation boundary** for the
first real module in the Senti / Sapianta system.

It specifies:
- what MAY be implemented
- what MUST NOT be implemented

This phase allows **practical usefulness** without compromising Core integrity.

---

## 1. HARD PREREQUISITES (LOCKED)

Implementation is allowed **only if all conditions are true**:

- Module `sapianta_chat_cli` exists in `docs/modules/REGISTRY.md`
- Module state is `ACTIVE`
- MPD exists at:
  `/senti_system/docs/modules/mpd/sapianta_chat_cli_MPD.md`
- MPD specifies:
  - `Execution: NO`
  - `Authority Level: ADVISORY`

If any prerequisite is false → **ABORT IMPLEMENTATION**.

---

## 2. ALLOWED IMPLEMENTATION SCOPE

### 2.1 EXPLICITLY ALLOWED

The implementation MAY include:

- text-based CLI interface
- user input parsing
- text output rendering
- read-only access to:
  - `REGISTRY.md`
  - Phase documents
  - MPD documents
- descriptive commands:
  - help
  - about
  - status
  - describe modules
- generation of explanatory text

---

### 2.2 EXPLICITLY FORBIDDEN

The implementation MUST NOT:

- execute shell or system commands
- write to the filesystem
- modify any document or state
- access network or external IO
- invoke Core execution paths
- load or activate other modules
- contain hidden hooks or backdoors
- simulate execution or side effects

---

## 3. STRUCTURAL BOUNDARIES

### 3.1 ALLOWED FILE TYPES

- CLI entrypoint
- argument / command parsers
- text renderers
- read-only document readers

### 3.2 FORBIDDEN STRUCTURES

- executors
- dispatchers with actions
- schedulers
- plugin loaders
- dynamic imports
- background processes

---

## 4. INTERACTION RULES

- every CLI command must be non-executable
- output must be text-only
- errors are described, never auto-fixed
- no command may trigger side effects

---

## 5. SECURITY BOUNDARY (CRITICAL)

If implementation requires:
- filesystem write access
- execution permissions
- network access
- privilege escalation

→ implementation is OUT OF SCOPE
→ requires a new Phase and a new MPD.

---

## 6. AI VALIDATION CHECKLIST

Before generating any code, the AI MUST confirm:

- module is ACTIVE
- MPD exists and is valid
- authority level is ADVISORY
- no execution paths exist
- no side effects are possible
- boundaries are respected

If any check fails → **ABORT**.

---

## 7. FINAL STATEMENT

This document locks the implementation boundary for Phase 74.

PHASE 74.0 — IMPLEMENTATION BOUNDARY ENFORCED
