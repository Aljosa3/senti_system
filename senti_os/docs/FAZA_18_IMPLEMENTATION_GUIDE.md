# FAZA 18 — Implementation Guide

## Quick Start & Best Practices

**Version:** 1.0.0
**Audience:** Developers
**Last Updated:** 2025-12-02

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Basic Examples](#basic-examples)
3. [Advanced Usage](#advanced-usage)
4. [Integration Examples](#integration-examples)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)
7. [Performance Tips](#performance-tips)

---

## Quick Start

### Installation & Setup

FAZA 18 is part of SENTI OS core. No additional installation required.

```python
# Import FAZA 18 components
from senti_os.core.faza18 import (
    PlatformDetector,
    AuthRequestManager,
    AuthWaiter,
    AuthResultValidator,
    SecureSessionManager,
    PolicyEnforcer
)
```

### Verify Installation

```python
from senti_os.core import faza18

# Get module info
info = faza18.get_info()
print(f"FAZA 18 v{info['version']}")
print(f"Privacy Compliant: {info['privacy_compliant']}")
print(f"Processes Biometrics: {info['processes_biometrics']}")  # Always 'false'
```

### 30-Second Example

```python
from senti_os.core.faza18 import PlatformDetector, PolicyEnforcer

# Initialize components
detector = PlatformDetector()
enforcer = PolicyEnforcer()

# Detect platform
info = detector.detect_platform("https://nlb.si")
print(f"Platform: {info.platform_name}")
print(f"Requires Biometric: {info.requires_biometric}")

# Ensure no biometric processing
if not enforcer.check_operation_allowed("process_biometric"):
    print("✓ Biometric processing correctly blocked")
```

---

## Basic Examples

### Example 1: Platform Detection

```python
from senti_os.core.faza18 import PlatformDetector, AuthMethod

detector = PlatformDetector()

# Detect a banking platform
bank_info = detector.detect_platform("https://nlb.si/netbanking")

print(f"Platform Type: {bank_info.platform_type.value}")
print(f"Platform Name: {bank_info.platform_name}")
print(f"Requires Biometric: {bank_info.requires_biometric}")

# Check supported authentication methods
for method in bank_info.required_auth_methods:
    print(f"  - {method.value}")

# Estimated wait time
if bank_info.estimated_wait_time:
    print(f"Estimated wait: {bank_info.estimated_wait_time}s")
```

**Output:**
```
Platform Type: bank
Platform Name: NLB
Requires Biometric: True
  - password
  - biometric
  - otp
Estimated wait: 30s
```

---

### Example 2: Simple Authentication Request

```python
from senti_os.core.faza18 import AuthRequestManager

manager = AuthRequestManager()

# Create authentication request
request = manager.create_auth_request(
    url="https://example.com/login",
    username="john.doe@example.com",
    password="SecurePass123!"
)

print(f"Request ID: {request.request_id}")
print(f"Method: {request.method.value}")
print(f"URL: {request.url}")

# Export for execution (e.g., by browser automation)
execution_data = manager.export_request_for_execution(request.request_id)
# execution_data can now be passed to execution layer
```

---

### Example 3: Waiting for External Authentication

```python
from senti_os.core.faza18 import AuthWaiter, WaitReason

waiter = AuthWaiter()

# Start waiting for biometric authentication
wait_id = waiter.start_wait(
    reason=WaitReason.BIOMETRIC_EXTERNAL,
    timeout_seconds=120,
    wait_message="Please complete biometric verification on your device"
)

print(f"Wait ID: {wait_id}")
print(f"Message: {waiter.get_wait_message(wait_id)}")

# In a real scenario, you'd register a completion checker
def check_auth_complete():
    # Check if external auth is complete
    # (implementation depends on your execution layer)
    return False  # Replace with actual check

waiter.register_completion_checker(wait_id, check_auth_complete)

# Non-blocking status check
status = waiter.check_status(wait_id)
print(f"Status: {status.value}")

# Abort if needed
# waiter.abort_wait(wait_id, "User cancelled")
```

---

### Example 4: Validating Authentication Results

```python
from senti_os.core.faza18 import (
    AuthResultValidator,
    create_auth_result,
    AuthResultStatus
)

validator = AuthResultValidator()

# Create result (from external auth)
result = create_auth_result(
    result_id="auth_result_123",
    status=AuthResultStatus.SUCCESS,
    session_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
)

# Validate
validation = validator.validate_result(result)

if validation.is_valid:
    print("✓ Authentication result is valid")

    # Extract session info
    session_info = validator.extract_session_info(result)
    print(f"Session Token: {session_info['session_token'][:20]}...")
else:
    print("✗ Validation failed")
    for error in validation.errors:
        print(f"  Error: {error}")
```

---

### Example 5: Session Management

```python
from senti_os.core.faza18 import SecureSessionManager

manager = SecureSessionManager()

# Create session after successful authentication
session = manager.create_session(
    platform_url="https://example.com",
    session_token="token_abc123xyz",
    expires_in_seconds=3600,  # 1 hour
    user_identifier="john.doe@example.com"
)

print(f"Session ID: {session.session_id}")
print(f"Expires At: {session.expires_at}")

# Later, retrieve session
retrieved = manager.get_session(session.session_id)
if retrieved and not retrieved.is_expired():
    print("✓ Session is active")
else:
    print("✗ Session expired or not found")

# Check if renewal needed
if manager.check_session_renewal_needed(session.session_id):
    print("⚠ Session nearing expiry, renewal recommended")

# Extend session
manager.extend_session(session.session_id, additional_seconds=1800)

# Revoke when done
# manager.revoke_session(session.session_id)
```

---

### Example 6: Policy Enforcement

```python
from senti_os.core.faza18 import PolicyEnforcer

enforcer = PolicyEnforcer(strict_mode=True)

# Require user consent
consent_id = enforcer.require_consent(
    operation_type="authentication",
    scope=["username", "password", "session_management"],
    user_identifier="john.doe@example.com"
)

print(f"Consent ID: {consent_id}")

# Check consent before operation
if enforcer.check_consent(consent_id, "username"):
    print("✓ User consent granted for operation")
else:
    print("✗ No consent, operation blocked")

# Check if operation is allowed
if enforcer.check_operation_allowed("fill_password_form"):
    print("✓ Operation allowed")

if not enforcer.check_operation_allowed("process_biometric_data"):
    print("✓ Biometric operation correctly blocked")

# Log operation
enforcer.log_operation(
    operation="authentication_attempt",
    operation_type="authentication",
    success=True,
    platform_url="https://example.com"
)

# Generate compliance report
report = enforcer.generate_compliance_report()
print(f"\nCompliance Status: {report['compliance_status']}")
print(f"Total Operations: {report['total_operations']}")
print(f"Critical Violations: {report['critical_violations']}")
```

---

### Example 7: Complete Authentication Flow

```python
from senti_os.core.faza18 import (
    PlatformDetector,
    AuthRequestManager,
    AuthWaiter,
    AuthResultValidator,
    SecureSessionManager,
    PolicyEnforcer,
    WaitReason,
    create_auth_result,
    AuthResultStatus
)

def authenticate_user(platform_url, username, password):
    """Complete authentication flow with all FAZA 18 components."""

    # Initialize components
    detector = PlatformDetector()
    request_manager = AuthRequestManager()
    waiter = AuthWaiter()
    validator = AuthResultValidator()
    session_manager = SecureSessionManager()
    enforcer = PolicyEnforcer()

    # Step 1: Require user consent
    consent_id = enforcer.require_consent(
        operation_type="authentication",
        scope=["username", "password"]
    )

    if not enforcer.check_consent(consent_id):
        return {"error": "User consent required"}

    # Step 2: Detect platform
    platform_info = detector.detect_platform(platform_url)
    print(f"Platform: {platform_info.platform_name}")

    # Step 3: Create authentication request
    auth_request = request_manager.create_auth_request(
        url=platform_url,
        username=username,
        password=password
    )

    enforcer.log_operation(
        operation="auth_request_created",
        operation_type="authentication",
        success=True
    )

    # Step 4: If biometric required, wait
    if platform_info.requires_biometric:
        print("⚠ Biometric authentication required externally")

        wait_id = waiter.start_wait(
            reason=WaitReason.BIOMETRIC_EXTERNAL,
            timeout_seconds=platform_info.estimated_wait_time or 120
        )

        print(waiter.get_wait_message(wait_id))

        # In real implementation, wait for completion
        # For this example, we simulate immediate completion

    # Step 5: Validate result (from external auth)
    # In real scenario, this comes from execution layer
    auth_result = create_auth_result(
        result_id=f"result_{auth_request.request_id}",
        status=AuthResultStatus.SUCCESS,
        session_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    )

    validation = validator.validate_result(auth_result)

    if not validation.is_valid:
        enforcer.log_operation(
            operation="auth_validation_failed",
            operation_type="authentication",
            success=False
        )
        return {"error": "Validation failed", "details": validation.errors}

    # Step 6: Create session
    session = session_manager.create_session(
        platform_url=platform_url,
        session_token=auth_result.session_token,
        expires_in_seconds=3600,
        user_identifier=username
    )

    enforcer.log_operation(
        operation="session_created",
        operation_type="session_management",
        success=True
    )

    # Cleanup
    request_manager.cancel_request(auth_request.request_id)

    return {
        "success": True,
        "session_id": session.session_id,
        "expires_at": session.expires_at.isoformat()
    }

# Use the function
result = authenticate_user(
    platform_url="https://example-bank.com",
    username="john.doe@example.com",
    password="SecurePass123!"
)

print(result)
```

---

### Example 8: OAuth Flow

```python
from senti_os.core.faza18 import AuthRequestManager

manager = AuthRequestManager()

# Create OAuth authentication request
oauth_request = manager.create_oauth_request(
    url="https://example.com/oauth/token",
    username="john.doe@example.com",
    password="SecurePass123!",
    client_id="senti_os_client_id",
    client_secret="client_secret_xyz",
    scope="read write"
)

print(f"OAuth Request ID: {oauth_request.request_id}")
print(f"Form Fields: {oauth_request.form_fields.keys()}")

# Export for execution
oauth_data = manager.export_request_for_execution(oauth_request.request_id)
```

---

## Advanced Usage

### Custom Platform Detection

```python
from senti_os.core.faza18 import PlatformDetector

detector = PlatformDetector()

# Register custom template
detector._request_templates["custom_bank"] = {
    "method": RequestMethod.POST,
    "headers": {
        "Content-Type": "application/json",
        "X-Custom-Header": "value"
    },
    "form_fields": {
        "user": "{username}",
        "pass": "{password}",
        "custom_field": "value"
    }
}

# Detect with custom page content
page_content = """
<form>
    <input type="text" name="username">
    <input type="password" name="password">
    <button>Login with Fingerprint</button>
</form>
"""

info = detector.detect_platform(
    url="https://custom-bank.com",
    page_content=page_content
)

# Will detect biometric due to "Fingerprint" keyword
print(f"Biometric Required: {info.requires_biometric}")
```

---

## Integration Examples

### FAZA 16 Integration (LLM Control)

```python
from senti_os.core.faza18 import FAZA16Integration, LLMAuthCommand

# Initialize integration
integration = FAZA16Integration()

# Get capabilities for LLM
capabilities = integration.get_llm_capabilities()
print("Available Commands:", capabilities['available_commands'])
print("Privacy Guarantees:", capabilities['privacy_guarantees'])

# Execute commands via LLM
# Command 1: Detect platform
response1 = integration.execute_llm_command(
    command=LLMAuthCommand.DETECT_PLATFORM,
    parameters={"url": "https://nlb.si"}
)

if response1.success:
    print(f"Platform: {response1.data['platform_name']}")
    if response1.requires_user_action:
        print(f"Action Required: {response1.user_action_description}")

# Command 2: Prepare authentication
response2 = integration.execute_llm_command(
    command=LLMAuthCommand.PREPARE_AUTH_REQUEST,
    parameters={
        "url": "https://nlb.si/login",
        "username": "john.doe@example.com",
        "password": "SecurePass123!"
    }
)

if response2.success:
    request_id = response2.data['request_id']
    print(f"Request Prepared: {request_id}")

# Command 3: Wait for external auth (if needed)
if response1.data.get('requires_biometric'):
    response3 = integration.execute_llm_command(
        command=LLMAuthCommand.WAIT_FOR_EXTERNAL_AUTH,
        parameters={"reason": "biometric_external"}
    )
    print(f"Waiting: {response3.data['wait_message']}")
```

---

### FAZA 17 Integration (Orchestration)

```python
from senti_os.core.faza18 import FAZA17Integration, WorkflowStage

# Initialize integration
integration = FAZA17Integration()

# Register callbacks for workflow stages
def on_detect_complete(workflow):
    print(f"Platform detected for workflow {workflow.workflow_id}")

def on_prepare_complete(workflow):
    print(f"Authentication prepared for workflow {workflow.workflow_id}")

integration.register_stage_callback(WorkflowStage.DETECT, on_detect_complete)
integration.register_stage_callback(WorkflowStage.PREPARE, on_prepare_complete)

# Create workflow
workflow_id = integration.create_workflow(
    platform_url="https://example.com",
    metadata={"user": "john.doe@example.com"}
)

print(f"Workflow Created: {workflow_id}")

# Execute workflow
result = integration.execute_workflow(
    workflow_id=workflow_id,
    username="john.doe@example.com",
    password="SecurePass123!"
)

if result['success']:
    print(f"✓ Authentication successful")
    print(f"Session ID: {result['session_id']}")
else:
    print(f"✗ Authentication failed: {result['error']}")

# Get workflow status
status = integration.get_workflow_status(workflow_id)
print(f"Status: {status['status']}")
print(f"Current Stage: {status['current_stage']}")

# Get metrics
metrics = integration.get_orchestration_metrics()
print(f"Total Workflows: {metrics['total_workflows']}")
print(f"Success Rate: {metrics['success_rate']:.1f}%")
```

---

## Best Practices

### 1. Always Require User Consent

```python
enforcer = PolicyEnforcer()

# GOOD: Explicit consent
consent_id = enforcer.require_consent(
    operation_type="authentication",
    scope=["username", "password"]
)

if enforcer.check_consent(consent_id):
    # Proceed with operation
    pass

# BAD: No consent check
# Never skip consent!
```

### 2. Log All Operations

```python
enforcer = PolicyEnforcer()

# Log all significant operations
enforcer.log_operation(
    operation="auth_attempt",
    operation_type="authentication",
    success=True,
    details={"platform": "example.com"},
    user_identifier="john.doe@example.com"
)

# Later, audit trail is available
audit_log = enforcer.get_audit_log(limit=100)
```

### 3. Handle Timeouts Gracefully

```python
waiter = AuthWaiter()

wait_id = waiter.start_wait(
    reason=WaitReason.BIOMETRIC_EXTERNAL,
    timeout_seconds=120,
    max_retries=3
)

# Implement retry logic
result = waiter.wait_for_completion(wait_id)

if result.state == WaitState.TIMEOUT:
    # Retry if possible
    if waiter.retry_wait(wait_id):
        result = waiter.wait_for_completion(wait_id)
    else:
        # Max retries exceeded, inform user
        print("Authentication timeout, please try again")
```

### 4. Clean Up Resources

```python
# Clean up old sessions
session_manager.cleanup_expired_sessions()

# Clean up old requests
request_manager.cleanup_expired_requests(max_age_minutes=5)

# Clean up old waits
auth_waiter.cleanup_old_waits(max_age_minutes=30)

# Clean up old workflows
faza17_integration.cleanup_completed_workflows(max_age_hours=24)
```

### 5. Validate All Results

```python
validator = AuthResultValidator(validation_level=ValidationLevel.STRICT)

result = create_auth_result(...)
validation = validator.validate_result(result)

if not validation.is_valid:
    # Log errors
    for error in validation.errors:
        print(f"Error: {error}")

    # Don't create session if validation fails
    return

# Check warnings
for warning in validation.warnings:
    print(f"Warning: {warning}")
```

### 6. Use HTTPS Only

```python
enforcer = PolicyEnforcer(strict_mode=True)

# This will be blocked in strict mode
enforcer.enforce_secure_transmission(
    url="http://insecure-site.com",  # HTTP not HTTPS
    operation="auth_attempt"
)
# Result: False, violation logged
```

### 7. Never Store Passwords

```python
# GOOD: Request manager handles credentials in-memory only
manager = AuthRequestManager()
request = manager.create_auth_request(url, username, password)
# Credentials are in memory, will be cleaned up

# When done, cancel request
manager.cancel_request(request.request_id)
# Credentials are securely destroyed

# BAD: Storing password
# password_file = open("passwords.txt", "w")
# password_file.write(password)  # NEVER DO THIS!
```

### 8. Monitor Compliance

```python
enforcer = PolicyEnforcer()

# Periodically check compliance
report = enforcer.generate_compliance_report()

if report['compliance_status'] != 'COMPLIANT':
    print(f"⚠ Compliance issue detected!")
    print(f"Critical Violations: {report['critical_violations']}")

    # Review violations
    violations = enforcer.get_critical_violations()
    for violation in violations:
        print(f"  - {violation.violation_type.value}")
        print(f"    {violation.details}")
```

---

## Troubleshooting

### Issue: Platform Not Detected Correctly

```python
detector = PlatformDetector()

# Provide more context
info = detector.detect_platform(
    url="https://unknown-platform.com",
    page_content=full_page_html,  # Pass page content
    page_metadata={"title": "Platform Login Page"}  # Pass metadata
)

# Check detection
print(f"Type: {info.platform_type.value}")
print(f"Methods: {[m.value for m in info.required_auth_methods]}")
```

### Issue: Wait Timing Out

```python
waiter = AuthWaiter()

# Increase timeout
wait_id = waiter.start_wait(
    reason=WaitReason.BIOMETRIC_EXTERNAL,
    timeout_seconds=300,  # 5 minutes instead of default
    max_retries=5  # More retries
)

# Update message for user
waiter.update_wait_message(
    wait_id,
    "Biometric verification taking longer than expected, please wait..."
)
```

### Issue: Session Expiring Too Quickly

```python
manager = SecureSessionManager()

session = manager.create_session(
    platform_url=url,
    session_token=token,
    expires_in_seconds=7200  # 2 hours instead of 1
)

# Enable auto-renewal
manager_with_renewal = SecureSessionManager(
    auto_renew=True,
    renewal_threshold_minutes=10  # Renew 10 min before expiry
)
```

### Issue: Validation Failing

```python
# Use less strict validation for troubleshooting
validator = AuthResultValidator(validation_level=ValidationLevel.BASIC)

result = create_auth_result(...)
validation = validator.validate_result(result)

# Get detailed summary
summary = validator.get_validation_summary(result)
print(summary)
```

---

## Performance Tips

### 1. Reuse Components

```python
# GOOD: Create once, reuse
detector = PlatformDetector()
manager = AuthRequestManager()

for url in urls:
    info = detector.detect_platform(url)
    # Process...

# BAD: Creating new instances every time
for url in urls:
    detector = PlatformDetector()  # Wasteful
    info = detector.detect_platform(url)
```

### 2. Batch Cleanup

```python
import threading
import time

def cleanup_task():
    while True:
        # Clean up every 5 minutes
        time.sleep(300)

        session_manager.cleanup_expired_sessions()
        request_manager.cleanup_expired_requests()
        waiter.cleanup_old_waits()

# Run in background
cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
cleanup_thread.start()
```

### 3. Use Appropriate Validation Levels

```python
# For most use cases, STANDARD is sufficient
validator = AuthResultValidator(validation_level=ValidationLevel.STANDARD)

# Only use STRICT for high-security scenarios
validator_strict = AuthResultValidator(validation_level=ValidationLevel.STRICT)
```

---

## Conclusion

FAZA 18 provides a comprehensive, privacy-first authentication framework. By following these examples and best practices, you can implement secure, compliant authentication flows while maintaining full privacy boundaries.

**Key Takeaways:**
- ✅ Always require user consent
- ✅ Log all operations
- ✅ Never process biometric data
- ✅ Clean up resources
- ✅ Validate all results
- ✅ Use HTTPS only
- ✅ Monitor compliance regularly

**Need Help?**
- Review the FAZA_18_SPEC.md for technical details
- Check test suite for more examples
- Consult PolicyEnforcer audit logs for debugging

---

**Document Version:** 1.0.0
**Last Updated:** 2025-12-02
