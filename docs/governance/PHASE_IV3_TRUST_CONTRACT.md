# PHASE IV.3 — Trust Contract (User ↔ System)

Status: ACTIVE  
Phase: IV.3  
Scope: Governance / Trust / Consent  
Execution: NOT APPLICABLE  

---

## Purpose

This document defines the explicit trust contract between the user and the system.

It exists to:
- Eliminate implicit trust assumptions
- Define what the system may and may not do
- Protect user sovereignty and intent clarity

Trust is never inferred.
Trust is always explicit.

---

## Core Principle

The system operates under the assumption of **zero trust by default**.

Any trust granted by the user must be:
- Explicit
- Contextual
- Revocable
- Narrow in scope

---

## User Commitments

The user agrees that:

- They understand the system is advisory by default
- They retain full responsibility for execution and decisions
- They must explicitly authorize any future execution capabilities
- They may revoke trust at any time without justification

---

## System Commitments

The system guarantees that it will:

- Never assume user consent
- Never perform actions without explicit authorization
- Never hide execution or decision-making
- Always explain its limits and current authority

The system may refuse to act if trust conditions are not met.

---

## Trust Scope

Trust may apply only to the following dimensions:

- Interpretation (reading input)
- Explanation (describing options)
- Validation (checking consistency)
- Simulation (non-executing reasoning)

Trust does NOT apply to:
- Execution
- Automation
- Environment access
- Data export

---

## Revocation

Trust can be revoked by the user at any time by:

- Explicit instruction
- Context reset
- Session termination
- Silence or non-response

Revocation requires no confirmation and takes effect immediately.

---

## Non-Negotiable Constraints

- Silence is never consent
- Convenience never overrides sovereignty
- Intelligence never overrides authority
- Automation is always opt-in

---

## Notes

This trust contract is architectural, not legal.

It is enforced by design separation, not by promises.
