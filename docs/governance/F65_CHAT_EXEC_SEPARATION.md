# F65 CHAT CORE / EXECUTION SEPARATION

Version: 1.0  
Status: NORMATIVE  
Phase: 65  
Date: 2025-12-22

---

## 1. PURPOSE

This document explicitly separates Chat Core from execution authority within Phase 65.

It resolves ambiguity regarding the term "execution interface" and clarifies that Chat Core possesses no autonomous execution authority.

---

## 2. CORE DISTINCTION

Execution Decision Authority:
The authority to decide whether, when, and what execution occurs.

Execution Mechanism / Interface:
A technical mediation layer enabling execution after authorization.

Chat Core is an execution mechanism.  
Chat Core is NOT an execution authority.

---

## 3. PROHIBITIONS

Chat Core MUST NOT:

- decide whether execution occurs,
- initiate execution autonomously,
- optimize execution outcomes,
- prioritize execution sequencing,
- override execution gates.

---

## 4. PERMITTED BEHAVIOR

Chat Core MAY:

- mediate explicitly approved execution,
- route execution commands,
- enforce governance constraints,
- halt execution violating governance rules.

---

## 5. EXECUTION CONSTRAINTS

All execution MUST be:

- single-shot,
- explicitly approved,
- non-recursive,
- non-looping,
- fully gated.

---

## 6. FINAL STATEMENT

Chat Core mediates execution.  
It NEVER decides execution.

---

END OF DOCUMENT
