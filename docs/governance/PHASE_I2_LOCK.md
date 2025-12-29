# PHASE I.2 — CORE LOCK

Status: LOCKED  
Scope: Intent-only classification  
Authority: NONE (advisory-only)

## Guarantees
- No execution
- No file access
- No system calls
- No LLM
- No state
- Deterministic, rule-based intent detection

## Fixed Intent Classes
- QUESTION
- REQUEST
- PLAN
- META
- UNKNOWN

## Non-negotiables
- This module SHALL NOT execute actions.
- This module SHALL NOT call any other modules.
- This module SHALL NOT store or infer state.
- Any extension requires a new phase declaration.

## Purpose
Provide a canonical proof that intent can be detected
without authority, execution, or autonomy.

## Activation
This lock is active immediately upon commit.
