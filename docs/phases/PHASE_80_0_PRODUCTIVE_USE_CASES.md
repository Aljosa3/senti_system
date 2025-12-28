# PHASE 80.0 — PRODUCTIVE USE CASES (READ-ONLY CLI)

Status: ACTIVE  
Phase: 80.0  
Scope: Productive Use  
Applies to: Sapianta Chat CLI  
Authority: Core-Locked (Phase 72)

---

## 0. PURPOSE

This document defines **practical, real-world use cases**
for the Sapianta Chat CLI.

The goal is to:
- extract value from the existing system
- support human understanding
- assist navigation, auditing, and onboarding
- do so without execution, mutation, or automation

This phase is about **using the tool**, not extending it.

---

## 1. PRIMARY USER ROLES

The CLI is intended for:

- system owner
- auditor / reviewer
- developer (read-only)
- external stakeholder (governance overview)
- future module author (orientation only)

No role receives execution authority.

---

## 2. CORE USE CASE CATEGORIES

### 2.1 SYSTEM ORIENTATION

**Goal:** Understand what exists.

Typical commands:
- `status`
- `read registry`
- `describe module sapianta_chat_cli`

Value delivered:
- fast mental model of the system
- confirmation of module states
- elimination of guesswork

---

### 2.2 GOVERNANCE NAVIGATION

**Goal:** Understand rules and boundaries.

Typical commands:
- `describe phase 72`
- `read phase 74.2`
- `read mpd sapianta_chat_cli`

Value delivered:
- clear visibility into allowed vs forbidden actions
- audit-friendly explanations
- reduced misinterpretation risk

---

### 2.3 ONBOARDING & EXPLANATION

**Goal:** Explain the system to a human.

Typical usage:
- step-by-step walkthrough using CLI output
- reading phases in sequence
- answering “why does this exist?” questions

CLI role:
- explanatory interface
- governance narrator
- documentation navigator

---

### 2.4 REVIEW & AUDIT SUPPORT

**Goal:** Verify integrity without touching the system.

Typical commands:
- `status`
- `read registry`
- `describe permissions sapianta_chat_cli`
- `read phase 79.1`

Value delivered:
- non-invasive audit trail
- confidence in Core Lock integrity
- proof of non-executability

---

### 2.5 DAILY REFERENCE (OWNER USE)

**Goal:** Use the CLI as a memory aid.

Examples:
- “What phase are we in?”
- “Is this module allowed to execute?”
- “Where is observability defined?”

CLI acts as:
- authoritative reference
- single source of truth navigator

---

## 3. WHAT THIS PHASE EXPLICITLY DOES NOT DO

This phase does NOT:
- add new commands
- add automation
- change UX behavior
- enable execution
- introduce observers, logs, or metrics
- modify governance rules

It only **uses what already exists**.

---

## 4. SUCCESS CRITERIA

Phase 80.0 is successful if:

- the CLI is used in real conversations
- documentation is accessed through the CLI
- misunderstandings are reduced
- no pressure exists to “add features” prematurely

---

## 5. TRANSITION FORWARD

After this phase:
- UX refinements may be proposed (Phase 80.1)
- real usage feedback may be documented (Phase 80.2)
- execution remains strictly out of scope

---

## 6. FINAL STATEMENT

Phase 80.0 marks the transition from
**system construction** to **system use**.

The Sapianta Chat CLI is now:
- stable
- trustworthy
- useful

PHASE 80.0 — PRODUCTIVE USE CASES ESTABLISHED
