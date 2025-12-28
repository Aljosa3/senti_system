# PHASE 74.2 — SAPIANTA CHAT CLI
## Behavior & Command Specification

Status: ACTIVE
Phase: 74.2
Module: Sapianta Chat CLI
Audience: ChatGPT / AI izvajalec
Authority: Core-Locked (Phase 72)

---

## 0. PURPOSE

This document defines the **allowed behaviors and command surface**
for the Sapianta Chat CLI module.

It specifies:
- which commands MAY exist
- what each command MAY do
- what each command MUST NOT do

No execution, mutation, or external IO is permitted.

---

## 1. HARD CONSTRAINTS (LOCKED)

All behaviors MUST comply with:
- Module state: ACTIVE (read-only)
- MPD: sapianta_chat_cli_MPD.md
- Phase 74.0 (Implementation Boundary)
- Phase 74.1 (File & Structure Spec)

If any constraint is violated → **ABORT**.

---

## 2. COMMAND MODEL

### 2.1 COMMAND FORMAT

All commands MUST follow the format:

<command> [subcommand] [options]

Commands are:
- text-only
- synchronous
- non-executable
- non-mutating

---

## 3. ALLOWED TOP-LEVEL COMMANDS

### 3.1 help

Purpose:
Display available commands and short descriptions.

Allowed behavior:
- read static command definitions
- render text output

Forbidden behavior:
- dynamic discovery
- execution
- file writes

---

### 3.2 about

Purpose:
Describe the Sapianta Chat CLI module.

Allowed behavior:
- display module purpose
- display lifecycle state
- display restrictions

Forbidden behavior:
- reading non-document files
- state inference beyond registry

---

### 3.3 status

Purpose:
Show current system description (read-only).

Allowed behavior:
- read REGISTRY.md
- display module states

Forbidden behavior:
- state changes
- health checks with side effects

---

### 3.4 describe

Purpose:
Describe documented entities.

Subcommands:
- describe module <module_id>
- describe phase <phase_id>
- describe permissions <module_id>

Allowed behavior:
- read documentation files
- render summaries

Forbidden behavior:
- inference beyond documents
- cross-file mutation

---

### 3.5 read

Purpose:
Read and display approved documents.

Subcommands:
- read registry
- read mpd <module_id>
- read phase <phase_id>

Allowed behavior:
- open and read markdown files
- display text content

Forbidden behavior:
- reading arbitrary paths
- directory traversal
- reading non-approved files

---

## 4. FORBIDDEN COMMANDS (GLOBAL)

The following commands MUST NOT exist:

- run
- exec
- apply
- fix
- write
- delete
- update
- install
- load
- enable
- disable

Presence of any forbidden command constitutes a **Phase 74 violation**.

---

## 5. OUTPUT RULES

- output MUST be text-only
- no ANSI control sequences required
- no colored output required
- no interactive prompts beyond input line
- errors MUST be descriptive, not corrective

---

## 6. ERROR HANDLING

Errors MUST:
- explain what is not allowed
- reference the relevant Phase or MPD
- never attempt remediation
- never suggest execution-based fixes

---

## 7. VALIDATION CHECKLIST (FOR AI)

Before implementing commands, the AI MUST confirm:

- every command is explicitly listed in this document
- no forbidden commands exist
- no command performs execution
- no command mutates state
- all reads are limited to approved documentation

Failure of any check → **ABORT IMPLEMENTATION**.

---

## 8. FINAL STATEMENT

This document locks the **behavior and command surface**
of the Sapianta Chat CLI module.

Any new command or behavior requires:
- a new Phase
- an updated MPD

PHASE 74.2 — BEHAVIOR & COMMAND SPEC ENFORCED
