# FAZA 53 — FILE 3: Email Adapter SPEC

**Version:** 1.0
**Date:** 2025-12-15
**Status:** Specification (Implementation NOT started)
**Authority:** System Architecture & Governance Framework
**Depends on:**
- FAZA 53 — FILE 1 (Interface Stabilization SPEC)
- FAZA 53 — FILE 2 (Frontend Adapter SPEC)

---

## 1. Title & Scope

### What This Specification Covers

This specification defines the Email Adapter as a governance-aware, high-risk, read-only interface between external email-based inputs and the Control Layer. Due to email's inherent security characteristics, asynchronous nature, and lack of interactive verification capabilities, the Email Adapter operates under stricter constraints than the Frontend Adapter.

**Scope includes:**
- Email Adapter role and risk profile
- Governance and identity integration with email-specific restrictions
- Allowed and forbidden capabilities (more restrictive than Frontend)
- Intent construction rules from email inputs
- Error handling and transparency requirements
- Security posture and attack surface assumptions
- Stability and compatibility guarantees

### What This Specification Does NOT Cover

**Explicitly excluded from scope:**
- Email server configuration or mail transfer protocols
- SMTP, IMAP, or POP3 implementation details
- Email parsing libraries or formats (MIME, HTML, plain text)
- Spam filtering or email security infrastructure
- Email delivery mechanisms or retry logic
- Mailbox management or email storage
- Email template design or formatting
- Authentication protocols (SPF, DKIM, DMARC implementation)

This specification focuses exclusively on the Email Adapter's contract boundary with the Control Layer and governance framework, treating email input as untrusted external data requiring maximum constraint.

---

## 2. Role of the Email Adapter

### Email as an Untrusted, Asynchronous Input Channel

**Email Risk Profile:**
Email is fundamentally different from interactive interfaces:
- **Asynchronous:** No real-time feedback or verification
- **Untrusted:** Sender identity easily spoofed or ambiguous
- **Unstructured:** Free-form text requires parsing and interpretation
- **Delayed:** Processing may occur hours or days after sending
- **Non-interactive:** No opportunity for clarification or correction
- **Public:** Potentially intercepted, forwarded, or archived

**Consequence:**
The Email Adapter must operate under the assumption that email inputs are potentially hostile, ambiguous, or malformed, and must apply maximum constraint to prevent abuse, bypass, or unintended system behavior.

### Explicit Distinction from Interactive Interfaces

**Email Adapter is NOT equivalent to Frontend Adapter:**

**Frontend Adapter characteristics:**
- Real-time interactive session
- Authenticated user with verified identity
- Structured inputs with validation
- Immediate feedback and error correction
- Session-bound operations

**Email Adapter characteristics:**
- No session context
- Identity is metadata hint only (never trusted)
- Unstructured text inputs
- Delayed response (email reply)
- No opportunity for interactive correction

**Architectural Principle:**
The Email Adapter is a minimal, constrained interface for declarative intent submission only. It does NOT support administrative operations, governance decisions, or complex workflows. Email is strictly a low-privilege, high-latency notification and submission channel.

### Primary Use Cases

**Allowed Use Cases:**
- Submission of declarative intents for evaluation
- Query of decision status (read-only)
- Request for audit log information (read-only, subject to access control)
- Notification delivery (system to user, not user to system)

**Prohibited Use Cases:**
- Administrative operations
- ADMIN GOVERNANCE MODE activation
- Policy or budget modifications
- Multi-step workflows or conversations
- Execution triggering
- Automated or background processing

---

## 3. Governance & Identity Context

### Identity Reception (Metadata Only, Never Authentication)

**Identity Context from Email:**
The Email Adapter receives identity information from email metadata:
- Sender email address
- Email headers (From, Reply-To, etc.)
- Optional signed metadata (if cryptographically verified externally)

**Critical Principle: Email Identity is NOT Authentication**

The Email Adapter treats sender email address as a non-authoritative hint only. Email identity cannot be trusted for:
- Access control decisions
- Privilege escalation
- Administrative operations
- Governance decisions

**Identity Verification is External:**
If identity verification is required, it must occur OUTSIDE the Email Adapter through:
- Cryptographic signatures (verified before adapter processing)
- External authentication systems (email used as notification only)
- Out-of-band verification (human confirmation required)

The Email Adapter itself performs NO authentication and grants NO privileges based on sender address.

### Role Representation (Non-Authoritative Hints Only)

**Role Context in Email:**
Email may contain role information as:
- Explicit declaration in email body ("as user", "as viewer")
- Metadata from external authentication system
- Signature payload if cryptographically verified

**Role Treatment:**
Roles received via email are treated as non-authoritative hints. They are included in Intent metadata for Control Layer Policy evaluation but do NOT grant implicit privileges at the adapter level.

**Policy Enforcement:**
If a sender claims a role, Policy evaluation within the Control Layer determines whether that role claim is valid. The Email Adapter does not enforce or verify role claims.

### Explicit Prohibition of Implicit ADMIN MODE Activation

**ADMIN GOVERNANCE MODE via Email is PROHIBITED:**

The Email Adapter must NEVER:
- Activate ADMIN GOVERNANCE MODE based on email input
- Accept governance decisions via email
- Allow policy modifications via email
- Enable CORE modifications via email
- Grant administrative privileges based on sender identity

**Rationale:**
ADMIN GOVERNANCE MODE requires explicit, interactive, verified authority as defined in ADMIN_GOVERNANCE_MODE_DEFINITION.md and IDENTITY_AUTHORITY_VERIFICATION_MODEL.md. Email's asynchronous, non-interactive, potentially spoofed nature makes it fundamentally unsuitable for administrative operations.

**Governance Operations Require Interactive Interfaces:**
Any operation requiring ADMIN MODE must occur through authenticated, interactive interfaces (Frontend Adapter with verified session) where identity can be confirmed and decisions can be audited in real-time.

---

## 4. Allowed Capabilities

### Intent Construction (Strictly Declarative)

**Capability:** Parse email content and construct canonical Intent

**Requirements:**
- Extract action, subject, and payload from email body
- Set source to "email"
- Include sender email address as user_id (non-authoritative)
- Ensure Intent conforms to Intent schema
- Apply strict parsing rules (fail on ambiguity)

**Constraints:**
- Intent must be declarative (describe request, not command execution)
- Parsing must be deterministic (same email produces same Intent)
- Ambiguous emails must result in validation error, not guessing
- No complex or multi-step intent sequences

**Email Parsing Principle:**
If email content is ambiguous, malformed, or requires interpretation, the adapter must reject the input with explicit error rather than attempting to infer intent.

### Evaluation Requests via Control Layer Only

**Capability:** Submit Intent to ControlEvaluator for evaluation

**Requirements:**
- Pass Intent to ControlEvaluator.evaluate()
- Receive ControlDecision with allowed, policy_reason, and budget_reason
- Handle IntentValidationError, PolicyDecision, BudgetStatus
- Return decision via email response

**Constraints:**
- No caching of decisions
- No retry logic or automatic resubmission
- No escalation or fallback paths
- Each email results in exactly one evaluation attempt

**Critical Principle:**
The Email Adapter is stateless. Each email is processed independently. No workflow, conversation, or multi-step interaction is supported.

### Read-Only Access to Decisions, Audit, and Explanations

**Capability:** Query governance infrastructure for read-only data

**Allowed Operations:**
- Query decision status for specific Intent ID
- Query audit log for sender's historical requests
- Query ExplanationView for decision explanations
- Receive governance summaries (if authorized by Policy)

**Constraints:**
- All queries subject to Policy-based access control
- No write operations permitted
- Results delivered asynchronously via email reply
- Access limits enforced by Policy (prevent abuse)

**Rate Limiting:**
Email-based queries must be subject to rate limiting to prevent abuse, spam, or denial-of-service via email interface.

---

## 5. Forbidden Capabilities

The following capabilities are strictly prohibited and must never be implemented in the Email Adapter:

### Execution of Any Action

**Prohibited:**
- Executing actions based on ControlDecision
- Triggering system operations
- Modifying system state
- Invoking Execution Layer components
- Automated action based on email receipt

**Rationale:**
Email is a notification and submission channel only. Execution requires explicit, interactive, verified authority that email cannot provide.

### Direct or Indirect CORE Access

**Prohibited:**
- Importing CORE modules directly
- Accessing Policy or Budget registries without ControlEvaluator
- Reading CORE state
- Bypassing Control Layer to access internal components

**Rationale:**
Email's untrusted nature makes it particularly dangerous for CORE access. All interaction must flow through Control Layer adapter contract.

### Control Layer Bypass

**Prohibited:**
- Skipping Intent validation
- Pre-approving requests without evaluation
- Caching decisions and reusing them
- Fast paths or shortcuts that bypass Policy or Budget evaluation

**Rationale:**
Email's high-risk profile requires maximum governance constraint. Every email-based request must be evaluated independently.

### Background or Autonomous Processing

**Prohibited:**
- Processing emails in background without explicit request
- Automated responses or reactions to email patterns
- Scheduled or recurring email processing
- Email-triggered workflows or orchestration
- Autonomous decision-making based on email content

**Rationale:**
Automation via email creates uncontrolled execution paths and potential for abuse. Email processing must be explicit, one-time, and audited.

### Implicit Admin Behavior

**Prohibited:**
- Granting privileges based on sender email address
- Activating ADMIN GOVERNANCE MODE
- Bypassing validation for "trusted" senders
- Creating administrative sessions
- Accepting governance decisions via email

**Rationale:**
Administrative operations require identity verification, session management, and interactive confirmation that email fundamentally cannot provide.

### Stateful or Long-Lived Workflows

**Prohibited:**
- Multi-step conversations or workflows
- Session state across multiple emails
- Context retention between email messages
- Email-based approval flows or multi-party interactions
- Conversational or interactive patterns

**Rationale:**
Email is asynchronous and unreliable for stateful interactions. Each email must be processed independently as a complete, self-contained request.

---

## 6. Intent Construction Rules

### Mandatory Fields

Every Intent constructed by the Email Adapter must include:

**source:**
- Must be set to "email"
- Identifies origin as email interface
- Enables source-specific Policy evaluation (stricter for email)

**action:**
- Extracted from email body via deterministic parsing
- Must be explicitly stated in email
- No inference or guessing allowed

**subject:**
- Extracted from email body via deterministic parsing
- Must be explicitly stated in email
- No inference or guessing allowed

**payload:**
- Contains structured data extracted from email
- Must be deterministic (same email produces same payload)
- Subject to size limits and keyword restrictions

**user_id:**
- Set to sender email address (non-authoritative)
- Marked as unverified in metadata
- Subject to Policy-based validation

### Inclusion of Identity Metadata

**Required Metadata:**
- sender_email: Email address from "From" header (untrusted)
- email_subject: Subject line of email
- email_timestamp: Time email was received
- verification_status: "unverified" (always)

**Optional Metadata:**
- Cryptographic signature verification result (if applicable)
- External authentication correlation (if available)
- Email headers (for audit purposes)

**Metadata Constraints:**
- Metadata must clearly indicate untrusted nature of email identity
- No metadata may grant implicit privileges
- All metadata subject to Policy evaluation

### Deterministic Mapping from Email Input to Intent

**Parsing Requirements:**

**Determinism:**
The same email content must always produce the same Intent. Parsing logic must be:
- Reproducible
- Non-random
- Time-independent (except for timestamps)
- Locale-independent

**Explicitness:**
Email must explicitly state action and subject. Examples:

**Acceptable:**
"ACTION: view STATUS: system"

**Unacceptable (ambiguous):**
"Can you show me the system?" (requires interpretation)

**Failure on Ambiguity:**
If email content is ambiguous, the adapter must return validation error with explanation of required format rather than attempting to guess intent.

### Immutability Guarantees Once Intent is Constructed

**Intent Immutability:**
Once Intent is constructed from email, it must not be modified. The Intent passed to ControlEvaluator must match the Intent logged in audit.

**Decision Immutability:**
ControlDecision received from ControlEvaluator must not be modified before logging or returning via email reply.

**Audit Correlation:**
Email input, constructed Intent, and resulting decision must be correlated in audit log for complete traceability.

---

## 7. Error Handling & Failure Transparency

### Invalid Input Handling

**Condition:** Email content cannot be parsed into valid Intent

**Required Behavior:**
- Reject email with explicit error message
- Explain required email format
- Provide example of valid email structure
- Log rejection to audit with reason
- Do NOT attempt to guess or infer intent
- Do NOT process partial or ambiguous inputs

**Transparency Requirement:**
Sender must understand exactly why email was rejected and what format is required.

### Identity Ambiguity Handling

**Condition:** Sender identity cannot be determined or is ambiguous

**Examples:**
- Multiple "From" addresses
- Spoofed or malformed headers
- Conflicting identity claims in email body

**Required Behavior:**
- Reject email with identity ambiguity error
- Log rejection to audit with ambiguity details
- Do NOT proceed with evaluation
- Do NOT default to anonymous or guest identity
- Require explicit, unambiguous sender identification

**Transparency Requirement:**
Sender must be informed of identity ambiguity and required correction.

### Policy/Budget Denial Surfacing

**Condition:** ControlDecision has allowed=False

**Required Behavior:**
- Log decision (including denial) to audit
- Send email reply with policy_reason or budget_reason
- Ensure reason is human-readable and specific
- Do NOT suppress or obfuscate denial reason
- Do NOT offer retry or escalation paths

**Transparency Requirement:**
Sender must understand exactly why request was denied and which constraint was violated.

### Explicit Failure Reporting Without Retries or Automation

**Failure Transparency Principle:**
Every failure must be explicitly reported to sender with:
- Clear description of what failed
- Specific reason for failure
- Required corrective action (if applicable)
- No automated retry or recovery

**Prohibited Behaviors:**
- Silent failures
- Automatic retry of failed requests
- Escalation to "fallback" paths
- Automated error recovery
- Background processing of failed emails

**Rationale:**
Email's asynchronous nature makes automated retry dangerous. Failures must be explicit and require human decision to retry.

---

## 8. Stability & Compatibility Guarantees

### Backward Compatibility Expectations

**Commitment:**
Email format requirements and response formats must remain stable. Changes to email parsing rules or required email structure are breaking changes requiring major version increment.

**Compatibility Requirements:**
- Existing valid email formats continue to be accepted
- Intent construction produces valid Intents under existing schema
- Decision responses remain parseable
- Error message formats remain consistent

**Deprecation:**
If email format changes are required, existing formats must be supported during deprecation period (minimum 6 months) with clear migration guidance.

### Allowed Evolution Boundaries

**Post-CORE-LOCK Evolution:**
The Email Adapter may evolve to support:
- Additional email format variants (backward compatible)
- Enhanced parsing for structured email content
- Improved error messages (non-breaking)
- New read-only query types (additive)

**Evolution Constraints:**
- Cannot add execution capabilities
- Cannot reduce security constraints
- Cannot bypass Control Layer
- Cannot enable stateful workflows or conversations

### Explicit Non-Goals

The Email Adapter explicitly does NOT and will NEVER:
- Support conversational or multi-step interactions
- Enable administrative operations
- Provide real-time or low-latency responses
- Support rich media or attachments as executable inputs
- Act as primary interface (email is secondary, notification-focused)

**Email as Notification Channel:**
Email's primary role is notification delivery (system to user), not command submission (user to system). Command submission via email is supported only for simple, declarative, stateless intents.

---

## 9. Security Posture (Email-Specific)

### Attack Surface Assumptions

**Email Adapter operates under the assumption that:**
- Any email may be spoofed or forged
- Sender identity is untrusted by default
- Email content may be malicious or crafted to exploit parsing
- Email may be intercepted, modified, or replayed
- Email metadata (headers, timestamps) may be falsified

**Defense Posture:**
The Email Adapter is designed to operate safely even under complete compromise of email infrastructure. No email input should be able to:
- Execute code
- Bypass Control Layer
- Access CORE components
- Escalate privileges
- Create sessions or persistent state

### Spoofing, Replay, and Ambiguity Considerations

**Spoofing:**
Email sender addresses can be trivially spoofed. The adapter must:
- Treat all sender identities as untrusted
- Rely on Policy evaluation to enforce access control
- Never grant privileges based on email address alone
- Log all requests for forensic analysis

**Replay:**
Emails can be replayed or forwarded. The adapter must:
- Process each email independently
- Not assume temporal context
- Not create long-lived state based on email
- Log timestamps for replay detection analysis

**Ambiguity:**
Email content can be ambiguous or malformed. The adapter must:
- Fail explicitly on ambiguous input
- Not attempt to infer or guess intent
- Require structured, explicit email formats
- Provide clear error messages for malformed emails

### Explicit Limits on Trust

**Zero Trust Principle:**
The Email Adapter trusts NOTHING from email input:
- Sender identity: Untrusted
- Email content: Untrusted
- Headers and metadata: Untrusted
- Timestamps: Untrusted (may be spoofed)
- Attachments: Not processed (ignored or rejected)

**Trust Boundary:**
Trust is established ONLY through:
- Control Layer Policy evaluation
- External cryptographic verification (if applicable)
- Out-of-band human confirmation (if required)

The adapter itself establishes no trust based on email properties.

### Rate Limiting and Abuse Prevention

**Required Protections:**
- Per-sender rate limits (prevent spam abuse)
- Per-action rate limits (prevent specific attack patterns)
- Global rate limits (prevent DoS via email flood)
- Audit log monitoring for abuse patterns

**Abuse Response:**
Repeated abuse or attack patterns must result in:
- Temporary or permanent sender blocking
- Escalation to human review
- Audit trail for forensic analysis
- No automated unblocking or forgiveness

---

## 10. Summary

This specification defines the Email Adapter as a high-risk, strictly constrained, read-only interface between untrusted email inputs and the Control Layer, treating email as an asynchronous, potentially hostile submission channel unsuitable for administrative operations, stateful workflows, or privileged access. The adapter operates under zero-trust assumptions, treating sender identity as non-authoritative metadata, rejecting ambiguous or malformed inputs explicitly, and subjecting every request to independent Control Layer evaluation with complete audit trail, thereby protecting CORE integrity, preventing email-based privilege escalation or bypass, and ensuring that email remains a minimal, declarative notification and submission interface subordinate to governance constraints and incapable of triggering execution or administrative actions. The Email Adapter's security posture assumes complete email infrastructure compromise, defending against spoofing, replay, ambiguity, and abuse through deterministic parsing, stateless processing, explicit failure reporting, and Policy-enforced access control, ensuring that no email-based input can compromise system integrity regardless of email content or claimed sender identity.

---

**Status:** Specification complete. Implementation NOT started. FAZA 53 — FILE 3 requires explicit approval before proceeding to implementation phase.
