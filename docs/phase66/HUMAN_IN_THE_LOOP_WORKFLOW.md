# Human-in-the-loop Workflow

Phase: 66  
Status: Normative (Phase-local)  
Scope: All human–system interaction in Phase 66

---

## Purpose

This document defines the mandatory human-in-the-loop workflow
for all Phase 66 interactions.

Its purpose is to:
- preserve human decision sovereignty,
- prevent implicit delegation of authority,
- integrate observability and simulation safely,
- ensure the system never acts as a decision-maker.

This workflow is REQUIRED for all Phase 66 usage.

---

## Core Principle

The human is the sole decision authority.

The system may:
- observe,
- simulate,
- explain,
- structure information.

The system may NOT:
- decide,
- recommend,
- prioritize,
- execute.

---

## Workflow Stages

### 1. Observe

**Description:**  
The system presents factual signals and system state.

**Source:**
- Observability modules only.

**Constraints:**
- Read-only.
- No interpretation beyond factual description.
- No implied importance.

---

### 2. Explore

**Description:**  
The human explores meaning, context, and implications.

**Source:**
- Sapianta Chat (Explain / Explore modes).

**Constraints:**
- Multiple perspectives allowed.
- No narrowing of options.
- No ranking or recommendation.

---

### 3. Simulate (Optional)

**Description:**  
The system presents hypothetical scenarios.

**Source:**
- Simulation modules only.

**Constraints:**
- Hypothetical only.
- Explicit uncertainty required.
- No outcome preference.

---

### 4. Reflect

**Description:**  
The system mirrors the human’s stated reasoning.

**Source:**
- Sapianta Chat (Reflect mode).

**Constraints:**
- No correction.
- No steering.
- No judgment.

---

### 5. Decide (Human Only)

**Description:**  
The human makes the decision.

**Source:**
- Human authority exclusively.

**Constraints:**
- The system MUST NOT influence the decision.
- The system MUST NOT frame “best” choices.

---

### 6. Act (Outside Phase 66)

**Description:**  
Execution occurs outside Phase 66 scope.

**Source:**
- External systems or future phases.

**Constraints:**
- Phase 66 has ZERO execution capability.
- Any execution requires explicit, external authorization.

---

## Prohibited Shortcuts

The following are FORBIDDEN:

- skipping the human decision stage,
- collapsing stages into a single system response,
- presenting “actionable conclusions”,
- auto-transition from simulation to action,
- silent defaults.

Any shortcut constitutes a Phase 66 violation.

---

## Escalation Rule

If a request attempts to:

- bypass the workflow,
- delegate decision authority,
- trigger execution,

the system MUST:
1. halt immediately,
2. explicitly state the boundary,
3. refuse continuation without human decision.

---

## Compliance Statement

This workflow complies with:

- Phase 65 hard-lock,
- Phase 66 Guardrails,
- Module Dependency Rules,
- Sapianta Chat interaction modes,
- Observability and Simulation scopes.

---

## Closure Statement

This workflow is the only valid interaction model for Phase 66.

It guarantees:
- human sovereignty,
- system safety,
- architectural clarity.

Any deviation requires an explicit Phase upgrade protocol.

---

End of document.
