# PHASE 66 — SIMULATION SCENARIO TEMPLATE

Status: TEMPLATE (OPERATIVE)  
Phase: 66  
Nature: Hypothetical, non-authoritative  
Purpose: Standardize “what-if” scenarios without enabling action

---

## 1. TEMPLATE PURPOSE

This template defines the required structure for all Phase 66 simulation scenarios.

It ensures scenarios are:
- explicitly hypothetical,
- descriptive (not prescriptive),
- bounded and reviewable,
- safe under Phase 65 constraints.

This template introduces no automation or decision authority.

---

## 2. REQUIRED METADATA

- **Scenario ID:**  
  (Unique identifier; format: `sim-YYYYMMDD-XXX`)

- **Title:**  
  (Neutral, descriptive; no implied preference)

- **Phase:**  
  `66`

- **Status:**  
  Draft | Reviewed | Archived

- **Hypothetical Marker:**  
  **THIS SCENARIO IS HYPOTHETICAL AND DOES NOT AUTHORIZE ACTION**

---

## 3. SCENARIO DESCRIPTION (WHAT-IF)

Describe the hypothetical situation using neutral language.

- State assumptions explicitly.
- Avoid verbs that imply action or instruction.
- Avoid “should”, “must”, “optimize”, “best”.

**Description:**
> (Free text; descriptive only)

---

## 4. ASSUMPTIONS & CONSTRAINTS

List assumptions and constraints that define the scenario’s bounds.

- Assumptions are not facts.
- Constraints are not goals.

**Assumptions:**
- (A1) …
- (A2) …

**Constraints:**
- (C1) …
- (C2) …

---

## 5. TIME HORIZON

Define the explicit time window considered.

- Start:
- End:
- Granularity (if any):

Time must be bounded.

---

## 6. INPUT REFERENCES (OPTIONAL)

Reference existing documents or components **for context only**.

- Governance references (traceability only)
- Observability context (descriptive only)

No live data or execution hooks allowed.

---

## 7. EXPECTED OUTPUT SHAPE (DESCRIPTIVE)

Describe the *type* of outputs expected (not the content).

Allowed examples:
- “Possible states that could emerge”
- “Dependencies that may interact”
- “Uncertainty ranges”

Forbidden:
- recommendations
- rankings
- next steps

---

## 8. EXPLICIT NON-GOALS

State what this scenario explicitly does NOT attempt to do.

Examples:
- No recommendation
- No optimization
- No action trigger
- No decision support

---

## 9. VALIDATION CHECKLIST

Before acceptance, confirm ALL are true:

- [ ] Scenario is explicitly hypothetical
- [ ] No action verbs or recommendations
- [ ] No goals or optimization criteria
- [ ] Bounded time horizon
- [ ] Non-authoritative language throughout

If any item fails → scenario is invalid.

---

## 10. EXAMPLES

### 10.1 VALID SCENARIO (ABBREVIATED)

Title: “Hypothetical increase in request volume”

Description:
> This scenario explores potential system states if request volume were to increase under unchanged governance constraints.

Non-Goals:
- No recommendation for scaling
- No prioritization of outcomes

---

### 10.2 INVALID SCENARIO (FORBIDDEN)

Description:
> The system should allocate more resources to handle increased demand efficiently.

Reason:
Contains recommendation and implied optimization.

---

End of Scenario Template
