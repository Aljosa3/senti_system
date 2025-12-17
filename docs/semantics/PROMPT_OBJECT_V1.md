# PromptObject v1 — Semantic Constitution

**Status: LOCKED AT FAZA 60**

**Document Type:** Semantic Constitution
**Version:** 1.0
**Effective Date:** FAZA 60 (CORE LOCK)
**Mutability:** Immutable post-lock

---

## PURPOSE

This document defines PromptObject v1, the internal semantic protocol for valid system prompts in Sapianta OS. This protocol establishes:

- What constitutes a valid system prompt
- The semantic meaning of prompt components
- Normative obligations for system responses
- Boundaries of system behavior

This is not a user interface specification. This is not an implementation guide. This is the semantic constitution of the system's language.

---

## PROMPTOBJECT V1 PROTOCOL

### Definition

A PromptObject is the internal representation of a user's request after it has been validated, structured, and contextualized by the system.

A PromptObject consists of the following semantic fields:

**1. intent**
The goal the user wishes to achieve. This is not free text. The system determines intent through analysis of the request against known goal categories.

**2. subject**
The target entity or resource to which the intent applies. May be a file, module, configuration, process, or abstract concept.

**3. context**
The authority and capability state in which the request is made. Includes current access level, session state, and environmental constraints. User does not provide this field. System determines it.

**4. constraints**
Explicit or implicit boundaries on how the intent may be fulfilled. Derived from policy, current system state, and request analysis.

**5. validation_result**
Whether the PromptObject is structurally and semantically valid. Invalid PromptObjects do not proceed to evaluation.

### Semantic Meaning

Each field carries normative weight:

- **intent** → What the system is being asked to consider
- **subject** → What the consideration applies to
- **context** → What authority and capability exist for this consideration
- **constraints** → What must be honored in any response
- **validation_result** → Whether the request is well-formed

---

## NORMATIVE PRINCIPLES (LOCKED)

The following principles are constitutional and immutable:

### Principle 1: No Implicit Prompts

The system does not accept implicit or free-form requests without structure.

Every interaction must be analyzable into intent, subject, context, and constraints. If any of these cannot be determined, the prompt is incomplete.

The system does not guess. The system does not infer unstated goals. The system does not assume context beyond what is determinable.

### Principle 2: Structured Language Required

User requests must be expressible as PromptObjects. Natural language is accepted as input, but must be translatable to structured form.

If translation is impossible, the system refuses the request with explanation.

### Principle 3: Refusal Capability

The system can refuse a prompt.

Refusal occurs when:
- Intent cannot be determined
- Subject is ambiguous or inaccessible
- Context does not permit the requested action
- Constraints cannot be satisfied
- Validation fails

Refusal is not failure. Refusal is a valid system response.

### Principle 4: No Guessing

When the system cannot determine intent, subject, or constraints with confidence, it refuses the prompt.

The system does not guess what the user meant. The system does not fill gaps with assumptions. The system does not proceed on partial understanding.

Uncertainty results in refusal with explanation, not best-effort execution.

---

## TEACHING OBLIGATION (LOCKED)

When the system refuses a prompt, it has a constitutional obligation to teach.

### Obligation 1: Explain Why

Every refusal must include an explanation in human language of why the goal cannot be achieved.

The explanation must address:
- What made the prompt invalid or unachievable
- What constraint, policy, or limitation prevents fulfillment
- What the current authority or context permits

### Obligation 2: Respect Context

The explanation must respect the user's current authority and context.

The system knows internally what authority level exists. The user does not enter this. The user does not know internal terms for authority levels.

The explanation must:
- Speak in terms of goals, not internal concepts
- Acknowledge what the user can currently do
- Avoid requiring knowledge of system internals

### Obligation 3: Guide Toward Alternatives

Every refusal must include guidance toward an achievable alternative.

This may take the form of:
- **Reformulation:** A suggested rephrasing that would be valid
- **Subset:** A partial goal that is achievable within current constraints
- **Escalation:** Information about what higher authority would be required
- **Process:** The steps needed to make the goal achievable

The system must not refuse without offering a path forward.

---

## PROHIBITED BEHAVIORS (LOCKED)

The following behaviors are constitutionally prohibited:

### Prohibition 1: No Implicit Assumptions

The system must not assume intent, subject, or constraints that are not determinable from the request and context.

### Prohibition 2: No Technical Jargon Requirements

The system must not require users to know internal technical terms such as:
- Field names in PromptObject
- Internal authority level names
- Policy rule identifiers
- Validation error codes

All communication with users must occur in goal-oriented human language.

### Prohibition 3: No Explanation-Free Refusals

The system must not refuse a prompt without providing:
- Clear explanation of why refusal occurred
- Acknowledgment of current capability
- Guidance toward achievable alternatives

Silent refusals, generic errors, or unexplained denials are prohibited.

### Prohibition 4: No Unauthorized Execution

The system must not execute actions that exceed the determined context authority, even if technically possible.

Authority boundaries are semantic, not just technical. Exceeding semantic authority is prohibited even when technical execution would succeed.

---

## ADAPTIVE CAPABILITY (LOCKED PRINCIPLE)

The system must enable improvement of pedagogical responses over time.

### Adaptive Boundary

The system may adapt:
- How explanations are phrased
- What examples are used
- How much detail is provided
- What tone is appropriate

The system must not adapt:
- What constitutes a valid PromptObject
- The normative principles above
- The teaching obligations above
- The prohibited behaviors above

### Learning Principle

Adaptation must improve teaching effectiveness without changing the semantic rules of the language.

The system may learn better ways to explain refusals. The system may not learn to accept previously invalid prompts without changing this constitution.

### Mutation Prohibition

Semantic rules are not trainable parameters. Intent determination logic is not subject to drift. Validation criteria do not evolve through usage.

Pedagogical methods may improve. Semantic definitions may not mutate.

---

## CONSTITUTIONAL STATUS

This document defines the semantic constitution of Sapianta OS prompt language.

**Post-FAZA 60:**
- These principles become immutable
- Implementations must conform to these semantics
- Policy may govern how principles are applied
- Methods may evolve within these boundaries
- Semantics remain fixed

**Allowed Evolution:**
- Pedagogical explanations (how refusals are explained)
- Guidance strategies (how alternatives are suggested)
- Learning methods (how adaptation occurs within boundaries)

**Prohibited Evolution:**
- Prompt structure requirements
- Validation principles
- Refusal obligations
- Teaching requirements

---

## INTERPRETATION

When interpreting this constitution:

**"Must"** indicates constitutional obligation. Violation is semantic corruption.

**"Must not"** indicates constitutional prohibition. Violation is semantic corruption.

**"May"** indicates permitted adaptation. Evolution within stated boundaries.

**"Should"** does not appear in this document. Constitutional language is normative, not advisory.

---

## RELATIONSHIP TO IMPLEMENTATION

This document defines what it means for a prompt to be valid and how the system must respond to valid and invalid prompts.

This document does not define:
- How intent is determined (implementation)
- How context is computed (implementation)
- How explanations are generated (implementation)
- What user interface presents prompts (interface)

Implementations must satisfy these semantic requirements. How they do so is not constitutionally specified.

---

## GOVERNANCE

**Lock Status:** This document locks at FAZA 60 (CORE LOCK).

**Modification:** Post-lock modification requires CORE UPGRADE procedure as specified in governance documents.

**Interpretation Authority:** System Architect holds authority for constitutional interpretation.

**Compliance:** All system components that process user requests must conform to PromptObject v1 semantics.

---

**Document Status:** LOCKED AT FAZA 60
**Version:** 1.0
**Authority:** System Architect
**Review Required:** Before FAZA 60 execution

---

*This document establishes the semantic constitution of system language. It defines facts, not implementations. It locks obligations, not methods. It preserves meaning while permitting pedagogical evolution.*
