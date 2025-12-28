# PHASE 74.4 — SAPIANTA CHAT CLI
## Wiring & Invocation Specification (Non-Executable)

Status: ACTIVE
Phase: 74.4
Module: Sapianta Chat CLI
Audience: ChatGPT / AI izvajalec
Authority: Core-Locked (Phase 72)

---

## 0. PURPOSE

This document defines **how the Sapianta Chat CLI may be wired and invoked**
by other parts of the system **without executing processes**.

It specifies:
- allowed invocation patterns
- forbidden execution paths
- integration boundaries

This phase introduces **no execution**, **no IO**, and **no side effects**.

---

## 1. HARD CONSTRAINTS (LOCKED)

All wiring MUST comply with:
- Phase 74.0 (Implementation Boundary)
- Phase 74.1 (File & Structure Spec)
- Phase 74.2 (Behavior & Command Spec)
- Phase 74.3 (Read-Only Code Generation)
- MPD: sapianta_chat_cli_MPD.md (Authority: ADVISORY, Execution: NO)

Violation of any constraint → **ABORT**.

---

## 2. ALLOWED INVOCATION MODEL

### 2.1 FUNCTION-LEVEL INVOCATION (ONLY)

The CLI MAY be invoked **only** via a pure function call:

sapianta_chat_cli.cli.entrypoint.run_cli(input_line: str) -> str

Properties:
- synchronous
- deterministic
- text-in / text-out
- no side effects
- no state retention

---

### 2.2 ALLOWED CALLERS

The following MAY call `run_cli()`:
- test harnesses
- REPL-like shells (non-executing)
- documentation viewers
- other read-only modules

Callers MUST:
- provide input as a string
- consume output as a string
- perform no execution based on output
- treat output as advisory text only

---

## 3. FORBIDDEN INVOCATION PATTERNS

The following are **explicitly forbidden**:

- process execution (python -m, __main__)
- shell scripts or shell hooks
- argparse / click / typer
- environment variable wiring
- stdin / stdout binding
- background threads
- async execution
- scheduling or timers

Presence of any forbidden pattern constitutes a **Phase 74 violation**.

---

## 4. IMPORT & LINKING RULES

- imports MUST be static
- no lazy imports
- no runtime discovery
- no plugin hooks
- no monkey patching
- no reflection-based linking

---

## 5. ERROR PROPAGATION

- all errors MUST be returned as text
- no exceptions may escape the module boundary
- callers MUST NOT interpret output as commands or instructions

---

## 6. OBSERVABILITY (READ-ONLY)

The CLI MAY expose:
- returned text
- error messages as plain strings

The CLI MUST NOT:
- log to disk
- emit metrics
- emit events
- register observers or listeners

---

## 7. VALIDATION CHECKLIST (FOR AI)

Before wiring or invoking the CLI, the AI MUST confirm:

- [ ] only `run_cli()` is invoked
- [ ] invocation is function-level only
- [ ] no process execution exists
- [ ] no IO bindings exist
- [ ] no async, threading, or scheduling exists
- [ ] output is treated as advisory text only

Failure of any check → **ABORT**.

---

## 8. FINAL STATEMENT

This document locks the **wiring and invocation boundary**
for the Sapianta Chat CLI module.

Any executable invocation or IO-based integration requires:
- a new Phase
- an updated MPD

PHASE 74.4 — WIRING & INVOCATION SPEC ENFORCED
