# Mandate Vocabulary (Phase II.1)

## Purpose
This document defines the canonical mandate types used by Sapianta.
Mandates describe allowed intent scope.
They are not commands and do not authorize execution.

## Core Principles
- Mandates describe intent, not action
- Mandates are declarative
- Mandates do not imply permission to execute
- All mandates are advisory-only at this phase

## Mandate Types

### READ_ONLY
Description:
Used for inspection, explanation, or description.
No mutation, no execution.

### ANALYZE
Description:
Used for reasoning, comparison, or evaluation.
No decisions, no actions.

### PROPOSE
Description:
Used to suggest options or structures.
No steps, no instructions.

### REQUEST_APPROVAL
Description:
Used to ask the user to explicitly approve a future action.
No execution occurs.

### META
Description:
Used for system-level or self-descriptive queries.

## Non-Mandates
The following are explicitly not mandates:
- EXECUTE
- RUN
- APPLY
- MODIFY
- WRITE
- DELETE
