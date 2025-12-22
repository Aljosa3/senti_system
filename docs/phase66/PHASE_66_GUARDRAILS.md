# Phase 66 Guardrails

Phase: 66  
Status: Normative (Phase-local)  
Scope: All Phase 66 work

---

## Purpose

This document defines mandatory guardrails for all Phase 66 activities.

Its purpose is to:
- protect Phase 65 governance invariants,
- prevent silent authority escalation,
- prevent agent drift,
- ensure Phase 66 remains exploratory, modular, and reversible.

These guardrails apply to ALL Phase 66 documents, modules, experiments,
and implementations.

---

## Absolute Invariants

The following are ABSOLUTE and NON-NEGOTIABLE:

- Phase 65 governance is immutable.
- Phase 66 MUST NOT reinterpret Phase 65 intent.
- Phase 66 MUST NOT introduce authority implicitly.
- Phase 66 MUST NOT centralize decisions.
- Phase 66 MUST NOT create agent-like behavior.

Any violation constitutes a governance breach.

---

## Document Classification Rules

Every Phase 66 document MUST explicitly declare its status as one of:

- **Normative (Phase-local)**  
  Rules that constrain Phase 66 behavior only.

- **Descriptive / Informational**  
  Explanatory material with ZERO authority.

- **Templates / Examples**  
  Non-binding structural guidance.

If a document does not declare its status, it is INVALID.

---

## Forbidden Content Patterns

The following are NOT allowed in Phase 66 documents:

- implicit recommendations,
- ranked options without user decision,
- language implying “best”, “optimal”, or “preferred” actions,
- automation that selects goals or priorities,
- hidden defaults that replace human choice,
- execution triggers derived from observation or simulation.

---

## Authority Separation

Phase 66 components MUST respect strict separation:

- Observability → signals only
- Simulation → hypothetical exploration only
- Authority → external (human / governance)
- Execution → explicitly gated, external

No Phase 66 component may combine these roles.

---

## Escalation Rule

If any Phase 66 work:

- touches Phase 65 governance,
- requires reinterpretation of locked rules,
- blurs authority boundaries,
- introduces decision pressure,

work MUST:
1. halt immediately,
2. explicitly name the violated boundary,
3. escalate for governance review.

Silent continuation is forbidden.

---

## Reversibility Requirement

All Phase 66 work MUST be:

- reversible,
- non-destructive,
- removable without Phase 65 impact,
- free of hidden dependencies.

If a change cannot be cleanly reverted, it does not belong in Phase 66.

---

## Language Discipline

Phase 66 documents MUST use:

- explicit qualifiers,
- neutral, descriptive language,
- conditional framing (“may”, “could”, “hypothetical”).

Imperative or prescriptive language is prohibited unless explicitly normative.

---

## Closure Statement

These guardrails are mandatory for the entirety of Phase 66.

They do not add new governance authority.
They exist solely to preserve clarity, safety, and architectural integrity.

Any future relaxation or modification requires an explicit Phase upgrade
protocol beyond Phase 66.

---

End of document.
