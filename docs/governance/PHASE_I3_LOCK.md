# PHASE I.3 — CORE LOCK

Status: LOCKED  
Scope: Advisory response framing  
Authority: NONE (advisory-only)

## Guarantees
- No execution
- No file access
- No system calls
- No LLM
- No state
- Deterministic intent-to-response mapping

## Fixed Mapping
- QUESTION → explanatory framing
- REQUEST → refusal with boundary explanation
- PLAN → structural description without steps
- META → system self-description
- UNKNOWN → neutral response

## Non-negotiables
- This phase SHALL NOT infer intent.
- This phase SHALL NOT alter detected intent.
- This phase SHALL NOT propose actions or steps.
- This phase SHALL NOT store or access user data.
- Any extension requires a new phase declaration.

## Purpose
Provide a canonical proof that response behavior
can be shaped without authority or execution.

## Activation
This lock is active immediately upon commit.
