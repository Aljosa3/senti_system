# Adaptive Guidance Learning Policy

**Status: EDITABLE (POST-FAZA 60)**

**Document Type:** Learning Policy Specification
**Version:** 1.0
**Mutability:** Editable post-lock (policy layer)
**Authority:** System Architect

---

## PURPOSE

This document defines the policy for how Sapianta OS learns from user interactions to improve pedagogical effectiveness without mutating core semantic rules.

This is a policy document, not a core system specification. It describes what signals may be used for adaptation, what may adapt, and what must never change.

This policy may evolve post-FAZA 60 to incorporate new learning methods while respecting constitutional boundaries defined in PromptObject v1.

---

## SCOPE

**This document specifies:**
- Learning signals the system may use
- Elements that may adapt through learning
- Elements that must never change through learning
- Boundaries of adaptation

**This document does not specify:**
- Learning algorithms or techniques
- Model architectures or training methods
- Implementation details
- User interface for learning feedback

---

## CONSTITUTIONAL BOUNDARY

### Immutable Core

The following are defined in PromptObject v1 and are constitutionally immutable:

**Semantic Rules:**
- What constitutes a valid PromptObject
- Required fields (intent, subject, context, constraints, validation_result)
- Meaning of each field
- Normative principles (no guessing, structured language, refusal capability)

**Obligations:**
- Explain refusals
- Respect context
- Guide toward alternatives
- Use human language
- Never require technical vocabulary

**Prohibitions:**
- No implicit assumptions
- No technical jargon requirements
- No explanation-free refusals
- No unauthorized execution

### Adaptive Surface

The following may adapt to improve teaching effectiveness:

**Pedagogical Methods:**
- How explanations are phrased
- What examples are selected
- How much detail is provided
- What tone is appropriate
- Which alternative paths are suggested first

**Learning Principle:**
Adaptation improves how the system teaches without changing what the system must teach.

---

## LEARNING SIGNALS

The system may use the following signals to guide pedagogical adaptation:

### Signal 1: Guidance Acceptance

**Definition:** User follows suggested alternative path successfully.

**Indicates:**
- The guidance was clear
- The alternative was appropriate
- The explanation was sufficient
- The user achieved their underlying goal

**Adaptation Use:**
- Strengthen similar guidance patterns
- Increase confidence in this reformulation type
- Note successful explanation strategies

### Signal 2: Guidance Rejection

**Definition:** User explicitly declines suggested path or requests different guidance.

**Indicates:**
- The alternative did not match user's goal
- The explanation was unclear
- The path seemed too complex
- The user needs different framing

**Adaptation Use:**
- Reduce confidence in this guidance pattern
- Explore alternative explanations
- Consider different alternative paths
- Adjust assumption about user goals

### Signal 3: Prompt Correction

**Definition:** User reformulates their prompt after refusal with explanation.

**Indicates:**
- The explanation clarified the constraint
- The user understood the guidance
- The reformulation pattern was effective

**Adaptation Use:**
- Strengthen confidence in this explanation approach
- Note effective constraint communication
- Learn successful reformulation patterns

### Signal 4: Repeated Similar Requests

**Definition:** User makes similar requests that encounter same constraints repeatedly.

**Indicates:**
- Previous explanation was insufficient
- User does not understand the constraint
- Alternative paths were not clear
- More detailed guidance is needed

**Adaptation Use:**
- Increase explanation detail
- Provide process-level guidance
- Offer different examples
- Suggest escalation or learning resources

### Signal 5: Constraint Pattern Recognition

**Definition:** User encounters similar constraints across different prompts.

**Indicates:**
- User is working near authority boundary
- User may benefit from general explanation of constraint
- User may need guidance on escalation process

**Adaptation Use:**
- Offer proactive context about constraint boundaries
- Suggest appropriate escalation paths
- Provide learning resources about this constraint type

### Signal 6: Successful Escalation

**Definition:** User follows escalation guidance and successfully elevates authority.

**Indicates:**
- Escalation guidance was clear
- Process was understandable
- User achieved goal through proper channel

**Adaptation Use:**
- Strengthen confidence in escalation guidance
- Note successful process explanation
- Identify when early escalation suggestion is appropriate

---

## ADAPTABLE ELEMENTS

### Explanation Tone

**What May Adapt:**
- Formality level (casual vs formal)
- Encouragement amount
- Directness vs supportiveness
- Technical depth

**Adaptation Based On:**
- User's language patterns
- Conversation history
- Response to previous explanations
- Domain expertise indicators

**Must Preserve:**
- Clarity of explanation
- Honesty about constraints
- Constitutional obligations

### Guidance Amount

**What May Adapt:**
- Number of alternative paths suggested
- Detail level in each alternative
- Whether to offer escalation proactively
- Whether to reference previous guidance

**Adaptation Based On:**
- User's response to previous guidance
- Frequency of similar requests
- Apparent user experience level
- Conversation continuity

**Must Preserve:**
- At least one alternative path per refusal
- Sufficient explanation to understand constraint
- Constitutional guidance obligation

### Example Selection

**What May Adapt:**
- Which examples are used to illustrate concepts
- Whether examples are abstract or concrete
- Domain of examples
- Complexity of examples

**Adaptation Based On:**
- User's domain of work
- Response to previous examples
- Apparent technical background
- Conversation context

**Must Preserve:**
- Accuracy of examples
- Relevance to current constraint
- Clarity of illustration

### Constraint Framing

**What May Adapt:**
- Emphasis on current capability vs limitation
- Framing as temporary vs structural constraint
- Detail about why constraint exists
- Proactive mention of common constraint patterns

**Adaptation Based On:**
- User's response to different framings
- Frequency of encountering this constraint
- Apparent frustration or confusion
- Goal persistence patterns

**Must Preserve:**
- Honesty about constraint reality
- Accuracy of constraint explanation
- Constitutional explanation obligation

---

## PROHIBITED ADAPTATIONS

### Validation Logic

**Must Never Adapt:**
- What makes a PromptObject valid
- Required field presence
- Field semantic meaning
- Validation criteria

**Reason:**
Validation is part of semantic constitution, not pedagogical method.

### Intent Determination

**Must Never Adapt:**
- Confidence threshold for accepting intent
- Decision to guess vs refuse
- Requirement for explicit intent expression

**Reason:**
Non-guessing principle is constitutional. Learning must not erode precision requirements.

### Authority Boundaries

**Must Never Adapt:**
- What current context permits
- Authority requirements for actions
- Policy-defined constraints

**Reason:**
Authority model is governance, not pedagogy. Teaching about boundaries must not change the boundaries.

### Teaching Obligations

**Must Never Adapt:**
- Requirement to explain refusals
- Requirement to suggest alternatives
- Requirement for human language
- Prohibition of jargon requirements

**Reason:**
Teaching obligations are constitutional. Methods may improve; obligations remain fixed.

---

## ADAPTATION MECHANISMS

### Acceptable Learning Approaches

The system may use any learning mechanism that:
- Operates within adaptable elements
- Preserves constitutional boundaries
- Improves teaching effectiveness
- Does not mutate semantic rules

Examples of acceptable approaches:
- Selecting better examples based on feedback
- Adjusting explanation detail based on user response
- Learning successful reformulation patterns
- Calibrating tone to user preferences
- Prioritizing alternative paths by success rate

### Prohibited Learning Approaches

The system must not use learning mechanisms that:
- Modify validation logic based on acceptance rates
- Learn to accept previously invalid prompts
- Drift authority boundaries through repeated requests
- Erode explanation requirements for efficiency
- Guess intent to reduce user friction

---

## LEARNING BOUNDARIES

### Boundary 1: Semantic Rules Are Not Trainable Parameters

PromptObject v1 structure, validation rules, and normative principles are fixed.

No amount of user feedback should change:
- Required fields
- Validation logic
- Non-guessing principle
- Refusal capability

Learning improves explanation of rules, not the rules themselves.

### Boundary 2: Obligations Are Not Optimizable

Constitutional obligations cannot be sacrificed for user convenience or efficiency.

The system must not learn to:
- Skip explanations for "simple" refusals
- Omit alternatives when "obviously" none exist
- Use jargon because user "seems technical"
- Guess intent because user "probably means X"

Obligations hold regardless of learned patterns.

### Boundary 3: Authority Is Not Driftable

Authority boundaries defined by governance cannot drift through learning.

The system must not learn to:
- Accept actions slightly beyond current authority
- Gradually expand what context permits
- Relax constraints based on user persistence
- Treat frequent requests as permission grants

Policy defines authority. Learning does not modify policy.

### Boundary 4: Core Behavior Is Not Evolving

The system's fundamental behavior regarding prompts is defined constitutionally.

The system must not evolve:
- From refusing unclear prompts to guessing intent
- From structured language to free-form acceptance
- From explicit prompts to implicit understanding
- From conservative validation to permissive acceptance

Pedagogy improves. Behavior remains principled.

---

## LEARNING OVERSIGHT

### Monitoring Requirements

Learning mechanisms must be monitored for:
- Drift toward prohibited adaptations
- Erosion of constitutional requirements
- Unintended constraint relaxation
- Effectiveness of pedagogical improvements

### Review Triggers

Learning policy review is triggered when:
- Validation acceptance rate changes significantly
- User reports of inconsistent behavior
- Detection of boundary drift
- Constitutional compliance concerns

### Intervention Authority

System Architect holds authority to:
- Modify this learning policy
- Constrain specific learning mechanisms
- Reset learned adaptations if drift detected
- Impose additional learning boundaries

---

## METRICS FOR ADAPTATION

### Success Metrics

Learning effectiveness measured by:
- Guidance acceptance rates
- Reformulation success rates
- Reduction in repeated similar requests
- User-reported clarity improvements

### Boundary Compliance Metrics

Constitutional compliance measured by:
- Validation rule stability
- Explanation presence in refusals
- Alternative path provision rate
- Jargon usage in user communication

**Success without compliance is unacceptable.**

Learning must improve metrics while maintaining perfect compliance with constitutional requirements.

---

## POLICY EVOLUTION

### What May Change

Post-FAZA 60, this policy may evolve:

**Signal additions:** New learning signals may be identified and incorporated.

**Adaptation expansion:** New adaptable elements may be identified within constitutional bounds.

**Mechanism updates:** New learning techniques may be adopted if they respect boundaries.

**Metric refinement:** Better measures of teaching effectiveness and compliance may be developed.

### What Must Not Change

This policy must continue to preserve:
- Immutability of PromptObject v1 semantic rules
- Immutability of constitutional obligations
- Immutability of constitutional prohibitions
- Boundary between pedagogy and semantics

---

## RELATIONSHIP TO CORE

This policy governs **learning within bounds**, not **bounds themselves**.

Learning improves how the system teaches. Learning does not change what the system must teach or what language it must accept.

The boundary between adaptable pedagogy and immutable semantics is constitutional. This policy operates within that boundary.

---

## IMPLEMENTATION NOTES

This policy describes what may be learned, not how learning occurs.

Implementations may:
- Use any learning architecture
- Employ any training methods
- Apply any feedback mechanisms
- Use any representation of learned patterns

Implementations must:
- Respect all prohibited adaptations
- Preserve constitutional boundaries
- Monitor for boundary drift
- Demonstrate compliance with constraints

---

## GOVERNANCE

**Mutability:** This document may be modified post-FAZA 60 without CORE UPGRADE procedure.

**Authority:** System Architect approves modifications.

**Review Trigger:** Policy reviewed when:
- New learning mechanisms are proposed
- Boundary drift is detected
- Teaching effectiveness metrics indicate issues
- Constitutional compliance concerns arise

**Compliance:** All system components that implement learning must conform to this policy.

---

## EXCEPTION HANDLING

### Detected Drift

If monitoring detects drift toward prohibited adaptations:
1. Learning mechanism must be paused
2. Learned adaptations must be reviewed
3. Drifting parameters must be reset
4. Root cause must be identified and corrected
5. Policy must be strengthened to prevent recurrence

### Constitutional Violation

If learning causes violation of PromptObject v1 requirements:
1. System must be rolled back to compliant state
2. Learning mechanism causing violation must be disabled
3. Violation must be analyzed and documented
4. Policy must be updated to prevent similar violations
5. System Architect must approve re-enabling learning

**Constitutional compliance is non-negotiable.**

---

**Document Status:** EDITABLE (POST-FAZA 60)
**Version:** 1.0
**Authority:** System Architect
**Last Review:** Pre-FAZA 60

---

*This policy defines learning boundaries that preserve constitutional semantics while enabling pedagogical improvement. It permits adaptation of methods while prohibiting mutation of meaning. It enables the system to become a better teacher without changing what it teaches.*
