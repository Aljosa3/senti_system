# PHASE 74.1 — SAPIANTA CHAT CLI
## File & Structure Specification

Status: ACTIVE
Phase: 74.1
Module: Sapianta Chat CLI
Audience: ChatGPT / AI izvajalec
Authority: Core-Locked (Phase 72)

---

## 0. PURPOSE

This document defines the **exact file and directory structure**
for the Sapianta Chat CLI module implementation.

It specifies:
- which directories MAY exist
- which files MUST exist
- which files MUST NOT exist

This is a **structural specification only**.
No behavior, execution, or logic is defined here.

---

## 1. ROOT LOCATION (LOCKED)

All implementation files for this module MUST reside under:

/senti_system/modules/sapianta_chat_cli/

No files outside this directory are allowed.

---

## 2. ALLOWED DIRECTORY STRUCTURE

The following directory structure is **explicitly allowed**:

sapianta_chat_cli/
├── README.md
├── __init__.py
├── cli/
│   ├── __init__.py
│   ├── entrypoint.py
│   ├── command_parser.py
│   └── renderer.py
├── readers/
│   ├── __init__.py
│   ├── registry_reader.py
│   ├── mpd_reader.py
│   └── phase_reader.py
└── utils/
    ├── __init__.py
    └── text_helpers.py

---

## 3. REQUIRED FILES

The following files MUST exist:

- README.md
- __init__.py
- cli/entrypoint.py
- cli/command_parser.py
- cli/renderer.py
- readers/registry_reader.py
- readers/mpd_reader.py
- readers/phase_reader.py

Each required file MUST:
- be read-only in behavior
- produce no side effects
- comply with MPD restrictions
- contain no execution logic

---

## 4. FORBIDDEN FILES AND DIRECTORIES

The following are **explicitly forbidden**:

- executor.py
- runner.py
- shell.py
- network.py
- writer.py
- loader.py
- plugins/
- actions/
- tasks/
- any file enabling execution, IO, or mutation

Presence of any forbidden file constitutes a **Phase 74 violation**.

---

## 5. FILE RESPONSIBILITIES (NON-EXECUTIVE)

### cli/entrypoint.py
- CLI entry only
- no execution logic
- no side effects

### cli/command_parser.py
- parse user input
- map input to descriptive intents
- must not trigger actions

### cli/renderer.py
- text-only output formatting
- no filesystem access
- no network access

### readers/*
- read-only access to documentation files
- no caching
- no mutation
- no state retention

### utils/*
- pure helper functions
- no state
- no side effects

---

## 6. IMPORT RULES (CRITICAL)

- only static imports are allowed
- no dynamic imports
- no plugin loading
- no reflection-based discovery
- no runtime module scanning

---

## 7. VALIDATION CHECKLIST (FOR AI)

Before generating any code, the AI MUST confirm:

- all files are under /modules/sapianta_chat_cli/
- no forbidden files exist
- no execution paths exist
- no write operations exist
- directory structure matches this specification exactly

Failure of any check → **ABORT IMPLEMENTATION**.

---

## 8. FINAL STATEMENT

This document locks the **file and directory structure**
for the Sapianta Chat CLI module.

Any deviation requires:
- a new Phase
- an updated MPD

PHASE 74.1 — FILE & STRUCTURE SPEC ENFORCED
