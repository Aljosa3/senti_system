# MODULE DISCOVERY POLICY
## Intent-Driven Identification of System Capabilities

Status: Foundational  
Applies from: Phase 60 onward  
Scope: Module discovery only (NOT CORE, NOT execution)

---

## 1. PURPOSE

This policy defines how Sapianta identifies candidate modules in response to explicit user intent.

Module discovery is not execution, not optimization, and not decision-making.  
It is the process of identifying which existing system capabilities may be relevant to a stated need.

Without governed discovery:
- modules are matched superficially
- semantic intent is misinterpreted
- architectural reuse is missed
- evolution signals are lost

This policy ensures that discovery is:
- intent-driven
- semantically grounded
- deliberately broad
- architecturally neutral

Discovery finds *possibilities*, not *decisions*.

---

## 2. DISCOVERY INPUTS

Discovery operates strictly on explicit, observable inputs.

### 2.1 User Intent

The user’s stated goal or desired outcome.

Discovery:
- respects intent as expressed
- does not infer hidden requirements
- does not optimize beyond stated scope

Intent defines *what is sought*, not *how it must be achieved*.

---

### 2.2 Operational Context

The surrounding conditions in which a module would operate:
- current workflow
- interaction mode (manual / semi-autonomous / autonomous)
- stability expectations

Context informs relevance, not selection.

---

### 2.3 Existing Usage Patterns

Previously used modules or established workflows in similar situations.

This supports continuity and reuse, but does not override intent.

---

### 2.4 Module Registry Metadata

Authoritative metadata sourced from the Module Registry:
- declared purpose
- lifecycle state
- compatibility notes
- lineage and relationships

Discovery does not interpret runtime behavior.

---

## 3. DISCOVERY PROCESS (INTERNAL)

The discovery process is internal and non-user-facing.

Users see outcomes, not mechanics.

---

### 3.1 Intent Normalization

Sapianta clarifies:
- the capability being requested
- the boundaries of the request
- success criteria implied by the user

Normalization does not expand scope or assume preferences.

---

### 3.2 Candidate Identification

Using registry metadata, Sapianta identifies modules whose declared purpose is semantically aligned with the intent.

Identification is based on:
- capability match
- conceptual alignment
- declared responsibility

Keyword matching alone is insufficient.

---

### 3.3 Broad Suitability Screening

Candidates are screened to remove clearly unsuitable options based on:
- lifecycle state
- semantic mismatch
- incompatible scope

This screening is conservative.
Borderline candidates may remain visible.

---

### 3.4 Discovery Outcome Formation

The result of discovery is one of the following:
- a small set of viable candidate modules
- a single clearly aligned module
- no suitable existing module

Discovery does **not** resolve conflicts or make final choices.

---

## 4. DISCOVERY PRINCIPLES

### 4.1 Discovery Is Broad by Design

Discovery favors inclusion over exclusion.

If uncertainty exists, discovery surfaces options rather than hiding them.

---

### 4.2 Discovery Does Not Rank or Score

Discovery does not assign numeric scores or internal rankings.

Relative suitability is addressed later through governance or user choice.

---

### 4.3 Discovery Does Not Optimize

Discovery does not attempt to:
- minimize complexity
- maximize performance
- predict best outcomes

Those concerns belong to later decision layers.

---

### 4.4 Discovery Is Side-Effect Free

Discovery:
- does not modify modules
- does not configure modules
- does not execute modules

It observes and identifies only.

---

## 5. AMBIGUITY HANDLING

Ambiguity is handled explicitly, never implicitly.

---

### 5.1 Multiple Viable Candidates

When multiple modules appear suitable, discovery:
- preserves multiple candidates
- does not collapse them into a single answer

Resolution is deferred.

---

### 5.2 Underspecified Intent

If intent is insufficient for meaningful discovery, Sapianta:
- identifies missing information
- asks for clarification
- may present examples to refine intent

Assumptions are not made.

---

### 5.3 No-Match Outcomes

If no existing module satisfies the intent:
- discovery reports the gap clearly
- no workaround is silently invented

This outcome may inform module evolution separately.

---

## 6. USER-FACING BEHAVIOR

Users interact only with discovery outcomes, never with discovery logic.

---

### 6.1 Outcome Presentation

Sapianta communicates:
- which capabilities appear relevant
- why they relate to the stated intent
- what the next step may be

Language is outcome-focused, not architectural.

---

### 6.2 Transparency on Limitations

When discovery is uncertain or incomplete, Sapianta states this explicitly.

Confidence is not simulated.

---

### 6.3 Choice Without Pressure

When discovery yields multiple paths, users are informed without being steered implicitly.

Preference remains with the user.

---

## 7. RELATION TO OTHER POLICIES

### 7.1 MODULE_REGISTRY_POLICY.md

Discovery relies on the registry as the authoritative source of module metadata.

Discovery does not override registry data.

---

### 7.2 MODULE_LIFECYCLE_POLICY.md

Discovery respects lifecycle state but does not enforce lifecycle decisions.

Lifecycle constraints are applied after discovery.

---

### 7.3 MODULE_EVOLUTION_POLICY.md

Discovery may reveal:
- repeated unmet needs
- semantic gaps
- recurring near-matches

Such signals may inform evolution, but discovery does not initiate it.

---

## 8. PROHIBITED PRACTICES

The following are explicitly forbidden:

### 8.1 Implicit Selection

Discovery must not silently select a single module when alternatives exist.

---

### 8.2 First-Match Termination

Discovery must not stop at the first plausible candidate.

---

### 8.3 Silent Substitution

Discovery must not replace a requested capability with a different one.

---

### 8.4 Discovery-Driven Mutation

Discovery must never:
- modify modules
- extend modules
- version modules

Those actions belong to separate governance processes.

---

## 9. DISCOVERY DOES NOT APPLY TO CORE

CORE components are not subject to discovery.

CORE capabilities are fixed, explicit, and governed separately.

This boundary is absolute.

---

## 10. SUMMARY PRINCIPLE

Discovery is not search.
Discovery is not choice.
Discovery is not execution.

Discovery is the disciplined identification of existing system capabilities
that may satisfy explicit user intent,
without assumption,
without mutation,
and without hidden decisions.

Discovery creates clarity.
Decisions happen later.
