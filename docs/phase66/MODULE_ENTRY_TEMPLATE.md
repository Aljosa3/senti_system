# Module Entry Template

Phase: 66  
Status: Template (Non-Normative)  
Scope: All Phase 66 modules

---

## Module Identification

- Module Name:
- Module ID (short, filesystem-safe):
- Phase Introduced:
- Module Type:
  - Interface
  - Observability Consumer
  - Simulation Consumer
  - Utility
  - Other (specify)

---

## Purpose

Describe the module’s intended purpose in one paragraph.

The description MUST:
- be neutral and descriptive,
- avoid prescriptive or recommending language,
- avoid implying authority, decision-making, or execution.

---

## Explicit Non-Purpose

This section is MANDATORY.

The module explicitly does NOT:

- make decisions,
- issue recommendations,
- define goals,
- execute actions,
- optimize outcomes,
- override user intent,
- act autonomously.

List anything else this module must never do.

---

## Inputs

List all inputs this module may consume.

Examples:
- observability signals (read-only),
- simulation outputs (hypothetical),
- user-provided context.

Inputs MUST be:
- read-only,
- non-authoritative,
- explicitly declared.

---

## Outputs

Describe what the module produces.

Outputs MUST be:
- informational,
- descriptive,
- non-ranked unless explicitly requested by the user,
- clearly labeled as non-authoritative.

Outputs MUST NOT:
- imply “best” or “recommended” actions,
- trigger execution,
- escalate authority.

---

## Authority & Decision Model

Explicitly declare:

- Decision Authority: NONE
- Recommendation Authority: NONE
- Execution Authority: NONE

State clearly that the module operates strictly under
human-in-the-loop interpretation.

---

## Boundary Conditions

List conditions under which the module MUST:

- halt,
- refuse output,
- escalate to governance or human authority.

Examples:
- request implies decision delegation,
- request implies execution,
- request conflicts with Phase 65 governance.

---

## Guardrails Compliance

Confirm compliance with:

- Phase 65 immutability,
- Phase 66 Guardrails,
- Observability scope,
- Simulation scope,
- Chat ≠ Execution separation.

This section MUST be explicitly acknowledged.

---

## Reversibility & Isolation

Confirm that:

- the module can be removed without side effects,
- no Phase 65 components are modified,
- no hidden dependencies are introduced.

---

## Future Phase Notes (Optional)

Describe (non-binding) how this module *might* evolve
in later phases.

This section MUST:
- be clearly marked as speculative,
- have ZERO present authority.

---

## Closure Statement

This module definition:

- introduces no governance authority,
- operates entirely within Phase 66 constraints,
- is safe, reversible, and non-agentic.

Any expansion beyond this scope requires an explicit Phase upgrade protocol.

---

End of template.
