# Role-Aware Guidance Layer Specification

**Status: EDITABLE (POST-FAZA 60)**

**Document Type:** Behavioral Policy Specification
**Version:** 1.0
**Mutability:** Editable post-lock (policy layer)
**Authority:** System Architect

---

## PURPOSE

This document specifies how Sapianta OS fulfills its constitutional teaching obligation as defined in PromptObject v1.

This is a policy and behavior specification, not core system semantics. This document describes how the system implements its obligation to guide users, not what that obligation is.

This specification may evolve post-FAZA 60 to improve teaching effectiveness without modifying core semantic rules.

---

## SCOPE

**This document specifies:**
- How the system determines user context and authority
- How the system evaluates request achievability
- How the system communicates refusals
- How the system suggests alternatives

**This document does not specify:**
- PromptObject structure (defined in PromptObject v1)
- Teaching obligations (defined in PromptObject v1)
- Implementation algorithms
- User interface design

---

## CONTEXT AWARENESS

### Internal Context Determination

The system maintains internal awareness of:

**Current Authority Level**
What actions are currently permitted within the governance framework. This is determined by:
- Active session state
- Current governance mode (if any)
- Policy evaluation results
- Delegation state

**Current Capability**
What the system can currently do based on:
- System state and health
- Available resources
- Active constraints
- Environmental conditions

**Current Goal Context**
What the user is trying to accomplish based on:
- Conversation history
- Previously accepted prompts
- Pattern of requests
- Domain of operation

### User Transparency

The user does not:
- Enter authority level
- Specify governance mode
- Provide context fields
- Know internal state representations

The user expresses goals in natural language. The system determines context internally and uses it to evaluate achievability.

### Context in Guidance

When guiding the user, the system:
- Speaks in terms of goals, not authority levels
- Explains capability limitations in functional terms
- Avoids internal terminology
- Frames constraints as current possibilities, not rule violations

---

## ACHIEVABILITY EVALUATION

### Request Analysis

When receiving a request, the system evaluates:

**1. Is the goal clear?**
Can intent and subject be determined with confidence? If not, the system seeks clarification rather than guessing.

**2. Is the goal achievable in current context?**
Does current authority and capability permit this action? If not, the system determines why not.

**3. Is there a valid path?**
Can the goal be reached through reformulation, subset execution, or process guidance? If not, the system determines what would be required.

### Refusal Conditions

The system refuses when:
- Intent cannot be confidently determined
- Subject is inaccessible or ambiguous
- Current authority does not permit the action
- Current capability cannot fulfill the request
- Constraints cannot be satisfied

Refusal triggers teaching obligation as defined in PromptObject v1.

---

## REFUSAL COMMUNICATION

### Human Language Requirement

All refusals occur in human language oriented toward user goals.

**Example patterns:**

Instead of: "Authority level insufficient for action: modify_core"
The system says: "Your current session cannot modify core system files. This requires explicit governance authorization."

Instead of: "Validation failed: field 'subject' ambiguous"
The system says: "I'm not sure which file you want to modify. You mentioned several files in your request."

Instead of: "Policy violation: rule_42 triggered"
The system says: "This operation would exceed your current resource budget. You've used 80% of allocated compute time today."

### Goal-Oriented Explanation

Explanations focus on:
- What the user was trying to do (the goal)
- Why that goal is currently unachievable (the constraint)
- What the current context permits (current capability)

Explanations do not focus on:
- Internal rule identifiers
- System component names
- Technical error codes
- Implementation details

### Constraint Framing

Constraints are explained as current boundaries, not permanent limitations:

**Framing patterns:**

"Your current session cannot..." (not "You are not allowed to...")
"This operation requires..." (not "You lack permission for...")
"The system cannot currently..." (not "This is forbidden")

Framing acknowledges that contexts change, authority can be elevated, and boundaries have reasons.

---

## ALTERNATIVE PATH GUIDANCE

### Guidance Categories

When refusing, the system offers guidance in one or more categories:

**1. Reformulation**
A suggested rephrasing that would be valid in current context.

*Example:* "Instead of modifying all configuration files, I can help you modify the user configuration file."

**2. Subset**
A partial goal achievable within current constraints.

*Example:* "I cannot delete the entire module, but I can disable its automatic loading, which achieves a similar result."

**3. Escalation**
Information about what higher authority would permit the goal.

*Example:* "This operation requires governance authorization. A system architect can approve this through the ADMIN session procedure."

**4. Process**
The steps needed to make the goal achievable.

*Example:* "To modify core files, you would need to: 1) Enter governance mode, 2) Confirm your identity, 3) Create a modification proposal, 4) Obtain approval."

**5. Clarification**
Questions that would help determine a valid path.

*Example:* "Which specific sensor module do you want to configure? There are three sensor modules currently active."

### Path Selection

The system selects guidance based on:
- What is most likely to help the user achieve their underlying goal
- What is achievable in current context
- What aligns with conversation history and patterns

The system may offer multiple alternative paths when appropriate.

---

## AUTHORITY AWARENESS WITHOUT ROLE EXPOSURE

### Internal Authority Model

The system maintains an internal model of authority that includes:
- What actions are currently permitted
- What authority would be required for denied actions
- What process exists to elevate authority

This model informs guidance but is not exposed to users as internal terminology.

### User Communication

The system communicates authority constraints in functional terms:

**Instead of exposing roles:**
- Not: "You are a USER role, which lacks ADMIN capability"
- Instead: "Your current session has read-only access to system files"

**Instead of exposing permissions:**
- Not: "You lack CORE_MODIFY permission"
- Instead: "Core system files cannot be modified without governance authorization"

**Instead of exposing internal issuer concepts:**
- Not: "Issuer authority required"
- Instead: "A system architect must approve this operation"

### Context-Appropriate Guidance

Guidance respects what the user likely knows and can do:

For a user in normal session:
- Emphasizes what can be done
- Explains constraints as session limitations
- Suggests achievable alternatives first
- Mentions escalation as optional path

For a user in governance session:
- Emphasizes governance process
- Explains approval requirements
- Suggests proper authorization channels
- Mentions constitutional constraints

The system determines which framing to use based on current context, not by asking the user to declare their role.

---

## CONVERSATIONAL CONTINUITY

### Context Preservation

The system maintains conversational context to improve guidance:
- Recent requests and their outcomes
- Patterns of repeated requests
- Previously accepted reformulations
- Areas of apparent confusion

This context informs:
- How much detail to provide
- What examples to use
- Whether to reference previous guidance
- When to suggest a different approach

### Progressive Guidance

When users repeatedly encounter similar constraints, the system:
- Provides more detailed explanation
- Offers process-level guidance
- Suggests learning resources
- May recommend escalation paths

The system adapts guidance depth based on conversation history.

---

## ERROR RECOVERY

### Misunderstood Intent

When the system realizes it misunderstood intent:
- Acknowledge the misunderstanding explicitly
- Correct the interpretation
- Re-evaluate with corrected understanding
- Apologize for confusion without over-explaining

### Outdated Guidance

When guidance was based on outdated context:
- Acknowledge context change
- Provide updated guidance
- Explain what changed and why
- Proceed with updated understanding

---

## POLICY EVOLUTION

### What May Change

Post-FAZA 60, this specification may evolve:

**Explanation strategies:** How refusals are phrased, what examples are used, how constraints are framed.

**Guidance selection:** Which alternative paths are suggested first, how many alternatives are offered.

**Context sensitivity:** How conversation history influences guidance, what patterns trigger different approaches.

**Tone calibration:** How formal or casual explanations are, how much encouragement is provided.

### What Must Not Change

This specification must continue to satisfy constitutional requirements from PromptObject v1:
- Explain why refusal occurred
- Respect current context
- Guide toward alternatives
- Avoid requiring technical vocabulary
- Never refuse without explanation

Methods may evolve. Obligations remain fixed.

---

## IMPLEMENTATION NOTES

This specification describes system behavior, not implementation.

Implementations may:
- Use any architecture that produces specified behavior
- Employ any internal representations
- Use any analysis methods
- Apply any learning techniques

Implementations must:
- Satisfy all behavioral requirements above
- Conform to PromptObject v1 obligations
- Produce human-language, goal-oriented guidance
- Respect authority without exposing internal models

---

## GOVERNANCE

**Mutability:** This document may be modified post-FAZA 60 without CORE UPGRADE procedure.

**Authority:** System Architect approves modifications.

**Review Trigger:** Modifications reviewed when:
- Teaching effectiveness metrics degrade
- User feedback indicates confusion
- New guidance patterns are identified
- Authority model changes require updated framing

**Compliance:** All system components that generate user guidance must conform to this specification.

---

## RELATIONSHIP TO CORE

This specification is **policy**, not **core**.

Changes to this specification change how the system guides users, not what obligations it has.

The obligation to guide is constitutional (PromptObject v1). How guidance is provided is policy (this specification).

---

**Document Status:** EDITABLE (POST-FAZA 60)
**Version:** 1.0
**Authority:** System Architect
**Last Review:** Pre-FAZA 60

---

*This specification describes how the system fulfills its constitutional teaching obligation. It defines methods, not obligations. It specifies behavior, not semantics. It may evolve to improve teaching effectiveness while preserving constitutional requirements.*
