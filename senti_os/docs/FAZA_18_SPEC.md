# FAZA 18 — Secure Biometric-Flow Handling Layer

## Technical Specification

**Version:** 1.0.0
**Status:** Production Ready
**Compliance:** GDPR, ZVOP, EU AI Act
**Author:** SENTI OS Core Team
**Date:** 2025-12-02

---

## Table of Contents

1. [Overview](#overview)
2. [Critical Privacy Rules](#critical-privacy-rules)
3. [Architecture](#architecture)
4. [Component Specifications](#component-specifications)
5. [Authentication Flow](#authentication-flow)
6. [Integration Points](#integration-points)
7. [Security & Compliance](#security--compliance)
8. [API Reference](#api-reference)

---

## Overview

FAZA 18 is the Secure Biometric-Flow Handling Layer for SENTI OS. It provides a privacy-first approach to authentication flows that may require biometric verification, while ensuring that SENTI OS itself NEVER processes biometric data.

### Design Philosophy

**Privacy-First Architecture:**
- SENTI OS acts as an orchestrator, not a processor
- Biometric verification is delegated to external platforms
- All operations are logged and auditable
- Explicit user consent is required for all flows

### Key Capabilities

✅ **Text credential handling** (username/password)
✅ **OAuth flow support**
✅ **External biometric wait mechanism**
✅ **Session token management**
✅ **Multi-platform detection**
✅ **FAZA 16 & 17 integration**

---

## Critical Privacy Rules

```
╔═══════════════════════════════════════════════════════════════════════╗
║                    SENTI OS MUST NEVER:                               ║
╠═══════════════════════════════════════════════════════════════════════╣
║  • Read biometric data                                                ║
║  • Collect biometric data                                             ║
║  • Store biometric data                                               ║
║  • Transmit biometric data                                            ║
║  • Process biometric data                                             ║
╚═══════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════╗
║                    SENTI OS MAY:                                      ║
╠═══════════════════════════════════════════════════════════════════════╣
║  • Fill in username + password (text credentials only)                ║
║  • Fill registration forms (without biometrics)                       ║
║  • Handle OAuth-like authentication steps                             ║
║  • Wait for external biometric validation to finish                   ║
║  • Resume execution AFTER external biometric step completes           ║
╚═══════════════════════════════════════════════════════════════════════╝
```

### Biometric Handling Protocol

**When external platform requires biometrics:**

```
┌─────────────────────────────────────────────────────────────────┐
│  SENTI OS pauses → hands control to platform → waits → resumes  │
└─────────────────────────────────────────────────────────────────┘
```

**Enforcement:**
- PolicyEnforcer module blocks ANY biometric operation attempts
- All operations are audited and logged
- Violations trigger immediate abort

---

## Architecture

### System Diagram

```
┌───────────────────────────────────────────────────────────────────────┐
│                           FAZA 18 LAYER                               │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────────┐      ┌──────────────────────┐              │
│  │  Platform Detector  │◄────►│  Policy Enforcer     │              │
│  └─────────────────────┘      └──────────────────────┘              │
│           │                             ▲                             │
│           ▼                             │                             │
│  ┌─────────────────────┐      ┌──────────────────────┐              │
│  │ Auth Request Mgr    │◄────►│  Audit Log           │              │
│  └─────────────────────┘      └──────────────────────┘              │
│           │                                                           │
│           ▼                                                           │
│  ┌─────────────────────┐                                             │
│  │   Auth Waiter       │ ◄─── EXTERNAL BIOMETRIC VERIFICATION        │
│  └─────────────────────┘      (Platform handles, SENTI waits)        │
│           │                                                           │
│           ▼                                                           │
│  ┌─────────────────────┐                                             │
│  │  Result Validator   │                                             │
│  └─────────────────────┘                                             │
│           │                                                           │
│           ▼                                                           │
│  ┌─────────────────────┐                                             │
│  │  Session Manager    │ ◄─── POST-AUTH TOKEN MANAGEMENT             │
│  └─────────────────────┘                                             │
│                                                                       │
├───────────────────────────────────────────────────────────────────────┤
│  INTEGRATION LAYER                                                    │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────────┐              ┌──────────────────┐             │
│  │  FAZA 16         │              │  FAZA 17         │             │
│  │  LLM Control     │              │  Orchestration   │             │
│  └──────────────────┘              └──────────────────┘             │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

### Component Hierarchy

```
senti_os/core/faza18/
├── platform_detector.py         # Detects platforms & auth requirements
├── auth_request_manager.py      # Manages credential submission
├── auth_waiter.py               # Waits for external auth
├── auth_result_validator.py     # Validates results
├── secure_session_manager.py    # Manages session tokens
├── policy_enforcer.py           # Enforces privacy rules
├── integration_faza16.py        # FAZA 16 integration
├── integration_faza17.py        # FAZA 17 integration
└── __init__.py                  # Module exports
```

---

## Component Specifications

### 1. Platform Detector

**Purpose:** Identifies external platforms and detects authentication requirements.

**Key Features:**
- Platform type detection (bank, government, payment, etc.)
- Authentication method detection (password, OTP, biometric, etc.)
- Biometric requirement detection
- Wait time estimation

**Classes:**
- `PlatformDetector`: Main detector class
- `PlatformInfo`: Platform information dataclass
- `PlatformType`: Enum of platform types
- `AuthMethod`: Enum of authentication methods

**Example:**
```python
detector = PlatformDetector()
info = detector.detect_platform("https://nlb.si")
if info.requires_biometric:
    print("External biometric verification required")
```

---

### 2. Auth Request Manager

**Purpose:** Manages creation of authentication requests (text credentials only).

**Key Features:**
- Username/password request creation
- OAuth request support
- JSON API request support
- CSRF token management
- Request templates

**Classes:**
- `AuthRequestManager`: Main manager class
- `AuthRequest`: Request dataclass
- `Credentials`: Credential container
- `RequestMethod`: HTTP methods enum

**Security:**
- No credential persistence
- In-memory only
- Automatic cleanup
- Secure destruction

**Example:**
```python
manager = AuthRequestManager()
request = manager.create_auth_request(
    url="https://example.com/login",
    username="user",
    password="pass"
)
```

---

### 3. Auth Waiter

**Purpose:** Waits for external authentication (including biometric) to complete.

**Key Features:**
- Configurable timeouts
- Retry logic
- Safe abort mechanisms
- Status checking
- Wait state machine

**Classes:**
- `AuthWaiter`: Main waiter class
- `WaitState`: Enum of wait states
- `WaitReason`: Enum of wait reasons
- `WaitResult`: Result dataclass

**Wait States:**
```
IDLE → WAITING → CHECKING → COMPLETED
                    ↓
                TIMEOUT / ABORTED / ERROR
```

**Example:**
```python
waiter = AuthWaiter()
wait_id = waiter.start_wait(
    reason=WaitReason.BIOMETRIC_EXTERNAL,
    timeout_seconds=120
)
# ... external auth happens ...
result = waiter.wait_for_completion(wait_id)
```

---

### 4. Auth Result Validator

**Purpose:** Validates authentication results (non-biometric only).

**Key Features:**
- Success/failure validation
- Session token validation
- Expiry checking
- Security indicator validation
- Configurable validation levels

**Classes:**
- `AuthResultValidator`: Main validator class
- `AuthResult`: Result dataclass
- `ValidationResult`: Validation outcome
- `AuthResultStatus`: Status enum
- `ValidationLevel`: Validation strictness enum

**Validation Levels:**
- **BASIC:** Status check only
- **STANDARD:** Status + session + timestamp
- **STRICT:** Full validation including security checks

**Example:**
```python
validator = AuthResultValidator()
result = create_auth_result(
    result_id="res_1",
    status=AuthResultStatus.SUCCESS,
    session_token="token_abc"
)
validation = validator.validate_result(result)
```

---

### 5. Secure Session Manager

**Purpose:** Manages session tokens after successful authentication.

**Key Features:**
- Session creation and tracking
- Expiration management
- Session renewal
- Session revocation
- Platform-based session lookup

**Classes:**
- `SecureSessionManager`: Main manager class
- `Session`: Session dataclass
- `SessionStatus`: Status enum

**Security:**
- Token-only storage (no passwords/biometrics)
- Automatic expiration
- Secure cleanup
- No disk persistence (memory only by default)

**Example:**
```python
manager = SecureSessionManager()
session = manager.create_session(
    platform_url="https://example.com",
    session_token="token_xyz",
    expires_in_seconds=3600
)
```

---

### 6. Policy Enforcer

**Purpose:** Enforces privacy and security policies.

**Key Features:**
- Operation blocking (biometric operations)
- User consent management
- Audit logging
- Violation tracking
- Compliance reporting

**Classes:**
- `PolicyEnforcer`: Main enforcer class
- `PolicyViolation`: Violation enum
- `PolicySeverity`: Severity enum
- `ConsentRecord`: Consent dataclass
- `AuditLogEntry`: Audit entry dataclass

**Critical Functions:**
```python
# Block biometric operations
enforcer.check_operation_allowed("process_biometric")  # → False

# Require consent
consent_id = enforcer.require_consent(
    operation_type="authentication",
    scope=["username", "password"]
)

# Log operations
enforcer.log_operation(
    operation="auth_attempt",
    operation_type="authentication",
    success=True
)

# Generate compliance report
report = enforcer.generate_compliance_report()
```

---

### 7. FAZA 16 Integration

**Purpose:** Integration with FAZA 16 LLM Control Layer.

**Key Features:**
- High-level LLM commands
- No credential exposure to LLM
- Workflow orchestration
- Status reporting

**Commands:**
- `DETECT_PLATFORM`
- `PREPARE_AUTH_REQUEST`
- `WAIT_FOR_EXTERNAL_AUTH`
- `VALIDATE_AUTH_RESULT`
- `GET_SESSION_STATUS`
- `REVOKE_SESSION`

**Example:**
```python
integration = FAZA16Integration()
response = integration.execute_llm_command(
    command=LLMAuthCommand.DETECT_PLATFORM,
    parameters={"url": "https://example.com"}
)
```

---

### 8. FAZA 17 Integration

**Purpose:** Integration with FAZA 17 Multi-Model Orchestration.

**Key Features:**
- Workflow creation and management
- Multi-stage authentication flows
- Stage callbacks
- Orchestration metrics

**Workflow Stages:**
```
DETECT → PREPARE → WAIT → VALIDATE → SESSION → COMPLETE
```

**Example:**
```python
integration = FAZA17Integration()
workflow_id = integration.create_workflow(
    platform_url="https://example.com"
)
result = integration.execute_workflow(
    workflow_id=workflow_id,
    username="user",
    password="pass"
)
```

---

## Authentication Flow

### Standard Flow (Password Only)

```
┌──────────┐
│  START   │
└────┬─────┘
     │
     ▼
┌─────────────────┐
│ Detect Platform │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│ Prepare Request │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│ Submit Creds    │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│ Validate Result │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│ Create Session  │
└────┬────────────┘
     │
     ▼
┌──────────┐
│   END    │
└──────────┘
```

### Biometric Flow (External Delegation)

```
┌──────────┐
│  START   │
└────┬─────┘
     │
     ▼
┌─────────────────┐
│ Detect Platform │
│ (bio required)  │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│ Prepare Request │
└────┬────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│  SENTI OS PAUSES                    │
│  ┌───────────────────────────────┐  │
│  │  EXTERNAL PLATFORM            │  │
│  │  handles biometric            │  │
│  │  verification                 │  │
│  └───────────────────────────────┘  │
│  SENTI OS WAITS                     │
└────┬────────────────────────────────┘
     │
     ▼
┌─────────────────┐
│ Resume          │
│ Validate Result │
└────┬────────────┘
     │
     ▼
┌─────────────────┐
│ Create Session  │
└────┬────────────┘
     │
     ▼
┌──────────┐
│   END    │
└──────────┘
```

---

## Integration Points

### FAZA 16 Integration (LLM Control)

```python
# LLM orchestrates authentication
integration = FAZA16Integration()

# Step 1: Detect
detect_response = integration.execute_llm_command(
    LLMAuthCommand.DETECT_PLATFORM,
    {"url": "https://bank.example.com"}
)

# Step 2: Prepare
prep_response = integration.execute_llm_command(
    LLMAuthCommand.PREPARE_AUTH_REQUEST,
    {"url": "https://bank.example.com/login",
     "username": "user",
     "password": "pass"}
)

# Step 3: Wait (if needed)
if detect_response.requires_user_action:
    wait_response = integration.execute_llm_command(
        LLMAuthCommand.WAIT_FOR_EXTERNAL_AUTH,
        {"reason": "biometric_external"}
    )
```

### FAZA 17 Integration (Orchestration)

```python
# Multi-model workflow orchestration
integration = FAZA17Integration()

# Create workflow
workflow_id = integration.create_workflow(
    platform_url="https://example.com"
)

# Execute complete workflow
result = integration.execute_workflow(
    workflow_id=workflow_id,
    username="user",
    password="pass"
)

# Monitor status
status = integration.get_workflow_status(workflow_id)
```

---

## Security & Compliance

### GDPR Compliance

✅ **Right to be forgotten:** No biometric data stored
✅ **Data minimization:** Only essential data processed
✅ **Purpose limitation:** Clear purpose for each operation
✅ **Transparency:** Full audit trail
✅ **Consent:** Explicit user consent required

### ZVOP Compliance (Slovenia)

✅ **Personal data protection:** Text credentials only, in-memory
✅ **Sensitive data:** Biometrics delegated externally
✅ **Security measures:** Encryption, secure handling

### EU AI Act Compliance

✅ **Transparency:** Explainable wait states
✅ **Human oversight:** User consent framework
✅ **Privacy:** No biometric processing
✅ **Safety:** Policy enforcement with abort mechanisms

### Audit Trail

All operations logged:
```python
{
    "entry_id": "audit_123",
    "timestamp": "2025-12-02T10:30:00Z",
    "operation": "auth_attempt",
    "operation_type": "authentication",
    "success": true,
    "details": {...},
    "user_identifier": "user@example.com",
    "platform_url": "https://example.com"
}
```

---

## API Reference

### Platform Detector API

```python
detector = PlatformDetector()

# Detect platform
info = detector.detect_platform(url, page_content, page_metadata)

# Check if biometric required
is_bio = detector.is_biometric_required(url, page_content)

# Get auth methods
methods = detector.get_supported_auth_methods(url)

# Check password-only support
password_only = detector.can_use_password_only(url)
```

### Auth Request Manager API

```python
manager = AuthRequestManager()

# Create request
request = manager.create_auth_request(url, username, password)

# OAuth request
oauth_req = manager.create_oauth_request(url, username, password, client_id)

# JSON API request
json_req = manager.create_json_api_request(url, username, password)

# Add CSRF token
manager.add_csrf_token(request_id, csrf_token)

# Cancel request
manager.cancel_request(request_id)
```

### Auth Waiter API

```python
waiter = AuthWaiter()

# Start wait
wait_id = waiter.start_wait(reason, timeout_seconds)

# Check status
status = waiter.check_status(wait_id)

# Abort wait
waiter.abort_wait(wait_id, reason)

# Retry wait
waiter.retry_wait(wait_id)
```

### Session Manager API

```python
manager = SecureSessionManager()

# Create session
session = manager.create_session(platform_url, session_token, expires_in_seconds)

# Get session
session = manager.get_session(session_id)

# Renew session
manager.renew_session(session_id, new_token, expires_in_seconds)

# Revoke session
manager.revoke_session(session_id)
```

### Policy Enforcer API

```python
enforcer = PolicyEnforcer()

# Check operation
allowed = enforcer.check_operation_allowed(operation)

# Require consent
consent_id = enforcer.require_consent(operation_type, scope)

# Check consent
is_valid = enforcer.check_consent(consent_id, required_scope)

# Log operation
entry_id = enforcer.log_operation(operation, operation_type, success)

# Get violations
violations = enforcer.get_violations(severity)

# Compliance report
report = enforcer.generate_compliance_report()
```

---

## Conclusion

FAZA 18 provides a comprehensive, privacy-first approach to handling authentication flows that may involve biometric verification. By strictly delegating biometric processing to external platforms and maintaining a robust audit trail, FAZA 18 ensures full compliance with GDPR, ZVOP, and EU AI Act requirements.

**Key Achievements:**
- ✅ Zero biometric data processing
- ✅ Complete audit trail
- ✅ Multi-platform support
- ✅ LLM and orchestration integration
- ✅ Full regulatory compliance

---

**Document Version:** 1.0.0
**Last Updated:** 2025-12-02
**Status:** Production Ready
