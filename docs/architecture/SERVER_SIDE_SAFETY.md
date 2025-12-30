# Server-Side Safety Model — Phase IV.1

Status: ACTIVE (READ-ONLY)
Scope: Architecture
Execution: FORBIDDEN
Authority: GOVERNANCE ONLY

---

## Purpose

This document defines the safety guarantees and limitations of running
**Sapianta Core on a server-side environment**.

The objective is to:
- Enable hosted Core usage
- Preserve user sovereignty
- Prevent server-side overreach
- Eliminate trust requirements beyond architecture

This model assumes the Core may be hosted, shared, or centrally deployed.

---

## Core Server Assumptions

The server-side Core is assumed to be:

- Potentially multi-tenant
- Potentially observable by infrastructure operators
- Potentially compromised

Therefore, **no security guarantee may rely on secrecy or trust**.

All guarantees must be enforced structurally.

---

## What the Server Can See

The server-side Core may observe:

- Incoming user input (current session only)
- Internal reasoning structures
- Intent classification
- Mandate validation results
- Policy application logic

This visibility is considered acceptable.

---

## What the Server Can NEVER Access

The server-side Core must never have access to:

- Local file systems
- Execution environments
- Command outputs
- API credentials
- Tokens or secrets
- User identity
- Persistent user state
- Historical interaction data (beyond session scope)

If such access exists, the architecture is invalid.

---

## Statelessness Requirement

The Core MUST be stateless.

This means:
- No databases
- No disk writes
- No memory across sessions
- No user identifiers
- No profiling
- No learning from individual users

All reasoning must be ephemeral.

---

## No Execution Guarantee

The Core:

- Cannot spawn processes
- Cannot execute commands
- Cannot trigger automation
- Cannot initiate network calls
- Cannot mutate any environment

Even if the Core generates text resembling instructions,
it remains non-operative by design.

---

## Audit Without Surveillance

Auditability is limited to:

- Structural correctness
- Phase enforcement
- Policy compliance

The Core does NOT:
- Log user actions
- Track behavior
- Store transcripts
- Retain execution attempts

Audit exists to validate the system — not the user.

---

## Threat Model

Even in the event of:
- Server compromise
- Malicious operator
- Instrumented runtime
- Full code visibility

The attacker gains:
- Reasoning visibility only

The attacker cannot:
- Execute user commands
- Modify user systems
- Extract user data
- Act on the user's behalf

---

## Architectural Guarantee

User safety is guaranteed because:

- Execution is external
- Authority is local
- Decisions remain human
- Core output is advisory
- Runtime is isolated

This guarantee holds regardless of deployment topology.

---

## Phase Lock

This server-side safety model becomes immutable once:

PHASE_IV1_LOCK.md is committed.

Any change requires:
- A new phase
- Explicit user opt-in
- Local execution only
