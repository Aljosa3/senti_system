# Module Dependency Rules

Phase: 66  
Status: Normative (Phase-local)  
Scope: All Phase 66 modules

---

## Purpose

This document defines the allowed and forbidden dependency relationships
between modules introduced in Phase 66.

Its purpose is to:
- prevent hidden authority centralization,
- prevent agent-like coordination,
- preserve strict separation of roles,
- ensure Phase 65 governance remains unaffected.

These rules apply to ALL Phase 66 modules without exception.

---

## Core Principle

No Phase 66 module may become a decision hub, authority broker,
or execution coordinator.

Dependencies are permitted ONLY as unidirectional,
read-only information flows.

---

## Allowed Dependency Types

The following dependency relationships are permitted:

### Observability → Consumers
- Observability modules MAY be read by:
  - Interface modules (e.g. Sapianta Chat),
  - Simulation modules,
  - Utility modules.

Observability modules MUST remain:
- read-only,
- non-authoritative,
- non-triggering.

---

### Simulation → Consumers
- Simulation modules MAY be read by:
  - Interface modules,
  - Human-in-the-loop workflows.

Simulation outputs MUST be:
- hypothetical,
- explicitly non-binding,
- non-ranked unless explicitly requested.

Simulation modules MUST NOT:
- influence execution,
- trigger automation,
- recommend decisions.

---

### Interface → Presentation Only
- Interface modules MAY:
  - present information,
  - structure content,
  - clarify relationships,
  - explain context.

Interface modules MUST NOT:
- aggregate authority,
- prioritize options autonomously,
- coordinate other modules.

---

## Forbidden Dependency Patterns

The following patterns are STRICTLY FORBIDDEN:

- Bidirectional dependencies between modules.
- Circular dependency chains.
- Any module depending on execution outcomes.
- Any module that both:
  - consumes simulation,
  - and influences execution.
- Interface modules acting as orchestration layers.
- Any implicit dependency created through shared state.

Any occurrence constitutes a Phase 66 violation.

---

## Authority Separation Enforcement

Authority is NOT a dependency.

No module may:
- request authority from another module,
- infer authority from data access,
- transfer authority implicitly.

Authority remains external to Phase 66 modules.

---

## Dependency Declaration Requirement

Every Phase 66 module MUST explicitly declare:

- which modules it depends on,
- the direction of dependency,
- the nature of data consumed.

Undeclared dependencies are INVALID.

---

## Escalation Rule

If a dependency requirement:
- cannot be expressed within these rules,
- implies authority coordination,
- requires reinterpretation of Phase 65,

work MUST:
1. halt immediately,
2. document the conflict,
3. escalate to governance authority.

Workarounds are forbidden.

---

## Reversibility Guarantee

All dependencies MUST be:
- removable,
- non-destructive,
- free of hidden coupling.

If removal of a module breaks governance assumptions,
the dependency design is invalid.

---

## Closure Statement

These dependency rules are mandatory for Phase 66.

They introduce no authority, no execution capability,
and no agent-like behavior.

Any modification requires an explicit Phase upgrade protocol.

---

End of document.
