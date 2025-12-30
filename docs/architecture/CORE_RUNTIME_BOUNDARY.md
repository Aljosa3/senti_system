# Core ↔ Runtime Boundary — Phase IV.1

Status: ACTIVE (READ-ONLY)
Scope: Architecture
Execution: FORBIDDEN
Authority: GOVERNANCE ONLY

---

## Purpose

This document defines the strict architectural boundary between:

- **Sapianta Core**
- **Runtime / Local Execution Environment**

The goal is to:
- Preserve user privacy
- Prevent hidden execution
- Enable safe distributed usage
- Avoid architectural drift in later phases

This boundary is non-negotiable once Phase IV.1 is locked.

---

## Definitions

### Sapianta Core

The Core is the **governed reasoning and decision layer**.

Core characteristics:
- Stateless
- User-agnostic
- Read-only
- Advisory only
- No execution capability
- No file system access
- No persistent memory of user data

The Core may run:
- On a remote server
- In a shared environment
- In a containerized or hosted setup

The Core:
- Interprets input
- Classifies intent
- Validates mandates
- Applies response policy
- Enforces execution blocks
- Produces explanations

The Core NEVER:
- Executes commands
- Modifies files
- Calls external APIs
- Stores user state
- Makes decisions on behalf of the user

---

### Runtime / Local Execution Environment

The Runtime is the **user-controlled execution space**.

Runtime characteristics:
- Local to the user or their infrastructure
- Fully isolated from Core governance
- Explicitly enabled by the user
- Responsible for all execution

The Runtime may:
- Execute commands
- Modify files
- Access APIs
- Maintain local state
- Store user data

The Runtime ALWAYS:
- Acts only after explicit user confirmation
- Operates outside Core authority
- Bears full responsibility for outcomes

---

## Information Flow

The information flow is strictly one-directional:

Core → Runtime:  
- Advisory output
- Explanations
- Classifications
- Non-binding recommendations (future phases only)

Runtime → Core:
- NONE

The Core must never receive:
- Execution results
- File contents
- Logs
- User secrets
- Local state

---

## Privacy Guarantee

Because the Core:
- Has no access to execution
- Has no access to files
- Has no memory of user state

User privacy is preserved by architecture, not policy.

Even a compromised Core cannot:
- Exfiltrate user data
- Infer execution outcomes
- Track user behavior over time

---

## Enforcement

This boundary is enforced by:
- Execution gates (Phase III)
- Audit trail (read-only)
- Absence of runtime interfaces
- Explicit governance locks

Any future feature violating this boundary MUST:
- Introduce a new phase
- Be explicitly approved
- Be opt-in
- Be locally executed

---

## Phase Lock

This boundary becomes immutable once:

PHASE_IV1_LOCK.md is committed.

No later phase may weaken this boundary.
Only extensions that preserve this separation are allowed.
