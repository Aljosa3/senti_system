PHASE VI.3 — EXECUTION CAPABILITY TAXONOMY

Status: LOCKED
Phase: VI.3
Authority: GOVERNANCE
Execution: DISABLED

Purpose

This document defines a complete taxonomy of execution capabilities
within the Sapianta system.

Its purpose is to:

precisely classify what “execution” means

prevent ambiguous or implicit execution

enable fine-grained governance control

serve as a prerequisite for any future execution enablement

No capability listed here is active.

Core Principle

Execution is not binary.

Execution exists in levels and categories, each requiring
explicit authorization, contracts, and escalation paths.

Capability Levels
LEVEL 0 — NO EXECUTION

Description:

Pure reasoning

Explanation

Classification

Rendering

Audit

Simulation without side effects

Examples:

Advisory responses

Intent detection

Policy explanation

UI rendering

Status:

Always allowed

Default system state

LEVEL 1 — SOFT ACTIONS (NON-SIDE-EFFECT)

Description:

Actions that do not change external or internal system state

Read-only interactions

Examples:

Reading files

Querying system status

Inspecting configurations

Fetching metadata

Requirements:

Explicit user request

Read-only contract

Audit logging

Status:

Defined but disabled

LEVEL 2 — INTERNAL STATE ACTIONS

Description:

Actions that modify internal system state

No external side effects

Examples:

Writing internal memory

Updating indexes

Changing internal flags

Requirements:

Explicit mandate

Execution contract

Human confirmation

Escalation approval

Status:

Defined but disabled

LEVEL 3 — EXTERNAL ACTIONS (LIMITED)

Description:

Actions affecting external systems

Bounded and reversible

Examples:

API calls

File system writes

Network requests

Requirements:

Signed execution contract

Escalation protocol

Capability whitelist

Continuous audit

Status:

Defined but disabled

LEVEL 4 — AUTONOMOUS / IRREVERSIBLE ACTIONS

Description:

Actions with long-term or irreversible impact

High-risk execution

Examples:

Financial transactions

Infrastructure changes

Autonomous scheduling

Requirements:

Multi-party authorization

Time-delayed execution

Kill-switch availability

Legal accountability

Status:

Conceptual only

Not eligible for activation

Capability Classification Matrix

Each executable function MUST declare:

capability level

scope

reversibility

risk class

required approvals

Undeclared capabilities are forbidden by default.

Enforcement Rule

If a capability cannot be classified,
it is treated as LEVEL 0 (NO EXECUTION).

Final Statement

This taxonomy defines the language of execution.

Nothing may execute without a defined place in this taxonomy.