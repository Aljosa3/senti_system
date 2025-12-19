Purpose

This policy defines how Sapianta determines what happens next after module discovery.

It governs:

decision authority

decision boundaries

when progression is allowed

when progression must stop

when user involvement is required

This policy is purely decisional.
It does not authorize execution, preparation, or model selection.

Scope

This policy applies to:

all modules returned by the discovery process

all governance states at Phase 60 and beyond

all pre-production and production design stages

This policy does not:

execute modules

prepare modules

select models

alter CORE behavior

Core Invariants

All decisions governed by this policy must respect:

Users approve scope, not structure

Architecture decisions are internal

No silent mutation

No implicit autonomy

CORE is never affected

If any invariant cannot be satisfied, the decision process must stop.

Decision Layer Definition

The Decision Layer exists between:

MODULE_DISCOVERY_POLICY
        ↓
MODULE_DECISION_POLICY
        ↓
MODULE_EXECUTION_POLICY


Its sole responsibility is to determine whether progression is permitted and under what authority.

No action may proceed beyond discovery without passing through this layer.

Decision Outcomes

Every discovered module results in exactly one of the following outcomes.

1. SYSTEM-APPROVED DECISION

The system may approve progression without user intervention only when:

the module is passive or analytical

no state mutation occurs

no execution is implied

no irreversible action exists

no ambiguity of intent exists

System-approved decisions may only allow:

preparation proposals

recommendations

informational use

They never authorize execution.

2. SYSTEM-RECOMMENDED DECISION

The system may recommend progression when:

multiple valid paths exist

intent is inferred but not explicit

trade-offs are present

execution risk exists but is contained

In this case:

the system must clearly mark the recommendation

no action proceeds without explicit user confirmation

the system must remain interruptible

3. USER-REQUIRED DECISION

User confirmation is mandatory when:

execution is possible

state mutation may occur

external systems are involved

irreversible consequences exist

autonomy thresholds may be crossed

Without explicit user approval:

progression halts

no preparation begins

no model is selected

Silence is never consent.

4. SYSTEM-BLOCKED DECISION

The system must block progression when:

intent cannot be reliably determined

governance constraints are violated

invariants are at risk

CORE boundaries may be affected

autonomy would be implicit

In this case:

the system must stop

no alternatives may be silently substituted

no fallback execution is allowed

Decision Authority Rules

Decision authority is determined by risk, not capability.

Situation	Authority
Informational / passive	System
Ambiguous intent	User
Execution-capable	User
Irreversible	User
Governance conflict	Blocked

The system may never elevate its own authority.

Separation of Concerns

The following separations are absolute:

Decision ≠ Execution

Recommendation ≠ Permission

Discovery ≠ Authorization

Capability ≠ Allowance

A positive decision does not imply readiness or execution.

Mandatory Stop Conditions

The decision process must halt if:

intent is unclear

required approvals are missing

multiple decisions conflict

governance state is incompatible

policy resolution is ambiguous

In all stop cases:

no execution layer is entered

no model selection occurs

no autonomous continuation is allowed

Relationship to Autonomy Modes

This policy defines decision gating, not autonomy.

Autonomy modes may only operate:

after a valid decision

within the bounds of that decision

without extending scope

Autonomy can never override a decision requirement.

CORE Protection Clause

Under no circumstances may this policy:

authorize CORE changes

reinterpret CORE permissions

infer CORE consent

enable CORE mutation

CORE governance remains isolated and absolute.

Policy Finality

This policy is normative and binding.

If a situation is not clearly permitted by this document, it is not permitted.