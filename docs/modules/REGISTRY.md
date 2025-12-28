# SENTI MODULE REGISTRY

Status: ACTIVE  
Phase: 73.1  
Core Lock: ENFORCED  
Mutation: FORBIDDEN (runtime)

This document is the single source of truth for all modules
within the Senti / Sapianta system.

No module exists unless explicitly listed here.
No capability is implied beyond what is written.

---

## Module: Sapianta Chat CLI

ID: sapianta_chat_cli
State: ACTIVE
Category: CLI

Purpose:
Text-based conversational interface for interacting with the Senti system
in a non-authoritative, read-only manner.

Capabilities:
- read
- generate
- describe

Restrictions:
- no execution
- no mutation
- no external IO

Core Dependency:
- READ_ONLY

Introduced In Phase: 73
Last State Change: 2025-12-27

Notes:
- Interface-only module
- No direct system control

---

## Module: Notes

ID: notes
State: ACTIVE
Category: Personal Knowledge

Purpose:
Personal, read-only notes and research module.

Capabilities:
- read
- describe

Restrictions:
- no execution
- no mutation via system

Core Dependency:
- READ_ONLY

Introduced In Phase: 80
Last State Change: 2025-XX-XX

Notes:
- Human-maintained
- Generated via Sapianta Chat draft

---

## Module: Trading Intel

ID: trading_intel
State: ACTIVE
Category: Intelligence

Purpose:
Read-only intelligence about trading concepts and scenarios.

Capabilities:
- read
- describe

Restrictions:
- no execution
- no mutation

Core Dependency:
- READ_ONLY

Introduced In Phase: 80
