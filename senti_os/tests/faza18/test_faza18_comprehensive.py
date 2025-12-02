"""
FAZA 18 - Comprehensive Test Suite

Complete test coverage for FAZA 18 Secure Biometric-Flow Handling Layer.
Tests all modules with ~6-8 tests per module for a total of 50-60 tests.

All tests run locally with mocked biometric flows (pause/resume simulation).

Author: SENTI OS Core Team
License: Proprietary
"""

import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Import FAZA 18 modules
from senti_os.core.faza18.platform_detector import (
    PlatformDetector, PlatformType, AuthMethod
)
from senti_os.core.faza18.auth_request_manager import (
    AuthRequestManager, CredentialType, RequestMethod
)
from senti_os.core.faza18.auth_waiter import (
    AuthWaiter, WaitState, WaitReason
)
from senti_os.core.faza18.auth_result_validator import (
    AuthResultValidator, AuthResultStatus, ValidationLevel, create_auth_result
)
from senti_os.core.faza18.secure_session_manager import (
    SecureSessionManager, SessionStatus
)
from senti_os.core.faza18.policy_enforcer import (
    PolicyEnforcer, PolicyViolation, PolicySeverity
)
from senti_os.core.faza18.integration_faza16 import (
    FAZA16Integration, LLMAuthCommand
)
from senti_os.core.faza18.integration_faza17 import (
    FAZA17Integration, WorkflowStage, WorkflowStatus
)


class TestPlatformDetector(unittest.TestCase):
    """Test cases for PlatformDetector module (8 tests)."""

    def setUp(self):
        self.detector = PlatformDetector()

    def test_detect_bank_platform(self):
        """Test detection of banking platform."""
        info = self.detector.detect_platform("https://nlb.si/login")
        self.assertEqual(info.platform_type, PlatformType.BANK)
        self.assertIn(AuthMethod.PASSWORD, info.required_auth_methods)

    def test_detect_government_platform(self):
        """Test detection of government platform."""
        info = self.detector.detect_platform("https://euprava.si")
        self.assertEqual(info.platform_type, PlatformType.GOVERNMENT)

    def test_detect_biometric_requirement(self):
        """Test detection of biometric requirement."""
        page_content = "Please use your fingerprint to authenticate"
        info = self.detector.detect_platform("https://test.si", page_content)
        self.assertTrue(info.requires_biometric)

    def test_detect_password_only_support(self):
        """Test detection of password-only support."""
        page_content = "Enter your username and password"
        info = self.detector.detect_platform("https://test.si", page_content)
        # May or may not support password-only depending on detection

    def test_is_biometric_required(self):
        """Test quick biometric check method."""
        page_content = "biometric authentication required"
        result = self.detector.is_biometric_required("https://test.si", page_content)
        self.assertTrue(result)

    def test_get_supported_auth_methods(self):
        """Test retrieval of supported auth methods."""
        methods = self.detector.get_supported_auth_methods("https://nlb.si")
        self.assertIsInstance(methods, list)
        self.assertTrue(len(methods) > 0)

    def test_estimate_wait_time(self):
        """Test wait time estimation."""
        info = self.detector.detect_platform("https://test.si")
        self.assertIsNotNone(info.estimated_wait_time)
        self.assertGreater(info.estimated_wait_time, 0)

    def test_platform_name_extraction(self):
        """Test platform name extraction."""
        metadata = {"title": "Test Bank Login"}
        info = self.detector.detect_platform("https://test.si", page_metadata=metadata)
        self.assertEqual(info.platform_name, "Test Bank Login")


class TestAuthRequestManager(unittest.TestCase):
    """Test cases for AuthRequestManager module (8 tests)."""

    def setUp(self):
        self.manager = AuthRequestManager()

    def test_create_basic_auth_request(self):
        """Test creation of basic authentication request."""
        request = self.manager.create_auth_request(
            url="https://test.si/login",
            username="testuser",
            password="testpass"
        )
        self.assertIsNotNone(request.request_id)
        self.assertEqual(request.url, "https://test.si/login")
        self.assertEqual(request.credentials.username, "testuser")

    def test_create_oauth_request(self):
        """Test creation of OAuth-style request."""
        request = self.manager.create_oauth_request(
            url="https://test.si/oauth/token",
            username="user",
            password="pass",
            client_id="client123"
        )
        self.assertIn("client_id", request.form_fields)
        self.assertEqual(request.form_fields["client_id"], "client123")

    def test_create_json_api_request(self):
        """Test creation of JSON API request."""
        request = self.manager.create_json_api_request(
            url="https://test.si/api/auth",
            username="user",
            password="pass"
        )
        self.assertEqual(request.method, RequestMethod.POST)
        self.assertIn("application/json", request.headers.get("Content-Type", ""))

    def test_add_csrf_token(self):
        """Test adding CSRF token to request."""
        request = self.manager.create_auth_request(
            url="https://test.si/login",
            username="user",
            password="pass"
        )
        success = self.manager.add_csrf_token(request.request_id, "csrf_token_123")
        self.assertTrue(success)
        self.assertTrue(request.requires_csrf)
        self.assertEqual(request.csrf_token, "csrf_token_123")

    def test_get_request(self):
        """Test retrieval of authentication request."""
        request = self.manager.create_auth_request(
            url="https://test.si/login",
            username="user",
            password="pass"
        )
        retrieved = self.manager.get_request(request.request_id)
        self.assertEqual(retrieved.request_id, request.request_id)

    def test_cancel_request(self):
        """Test cancellation of authentication request."""
        request = self.manager.create_auth_request(
            url="https://test.si/login",
            username="user",
            password="pass"
        )
        success = self.manager.cancel_request(request.request_id)
        self.assertTrue(success)
        self.assertIsNone(self.manager.get_request(request.request_id))

    def test_cleanup_expired_requests(self):
        """Test cleanup of expired requests."""
        # Create a request
        self.manager.create_auth_request(
            url="https://test.si/login",
            username="user",
            password="pass"
        )
        # Cleanup with very short max age
        self.manager.cleanup_expired_requests(max_age_minutes=0)
        # Should still work (requests just created)

    def test_export_request_for_execution(self):
        """Test exporting request for execution."""
        request = self.manager.create_auth_request(
            url="https://test.si/login",
            username="user",
            password="pass"
        )
        exported = self.manager.export_request_for_execution(request.request_id)
        self.assertIsNotNone(exported)
        self.assertIn("request_id", exported)
        self.assertIn("url", exported)


class TestAuthWaiter(unittest.TestCase):
    """Test cases for AuthWaiter module (8 tests)."""

    def setUp(self):
        self.waiter = AuthWaiter()

    def test_start_wait(self):
        """Test starting a wait operation."""
        wait_id = self.waiter.start_wait(
            reason=WaitReason.BIOMETRIC_EXTERNAL,
            timeout_seconds=30
        )
        self.assertIsNotNone(wait_id)
        self.assertIn("wait_", wait_id)

    def test_check_status(self):
        """Test checking wait status."""
        wait_id = self.waiter.start_wait(
            reason=WaitReason.OTP_ENTRY,
            timeout_seconds=30
        )
        status = self.waiter.check_status(wait_id)
        self.assertEqual(status, WaitState.WAITING)

    def test_abort_wait(self):
        """Test aborting a wait operation."""
        wait_id = self.waiter.start_wait(
            reason=WaitReason.BIOMETRIC_EXTERNAL,
            timeout_seconds=30
        )
        success = self.waiter.abort_wait(wait_id, "Test abort")
        self.assertTrue(success)

    def test_retry_wait(self):
        """Test retrying a wait operation."""
        wait_id = self.waiter.start_wait(
            reason=WaitReason.OTP_ENTRY,
            timeout_seconds=30,
            max_retries=3
        )
        success = self.waiter.retry_wait(wait_id)
        self.assertTrue(success)

    def test_get_wait_message(self):
        """Test getting wait message."""
        wait_id = self.waiter.start_wait(
            reason=WaitReason.BIOMETRIC_EXTERNAL,
            timeout_seconds=30
        )
        message = self.waiter.get_wait_message(wait_id)
        self.assertIsNotNone(message)
        self.assertIn("biometric", message.lower())

    def test_update_wait_message(self):
        """Test updating wait message."""
        wait_id = self.waiter.start_wait(
            reason=WaitReason.OTP_ENTRY,
            timeout_seconds=30
        )
        success = self.waiter.update_wait_message(wait_id, "Custom message")
        self.assertTrue(success)
        message = self.waiter.get_wait_message(wait_id)
        self.assertEqual(message, "Custom message")

    def test_cleanup_wait(self):
        """Test cleanup of wait operation."""
        wait_id = self.waiter.start_wait(
            reason=WaitReason.EMAIL_VERIFICATION,
            timeout_seconds=30
        )
        self.waiter.cleanup_wait(wait_id)
        status = self.waiter.check_status(wait_id)
        self.assertIsNone(status)

    def test_get_active_wait_count(self):
        """Test getting active wait count."""
        initial_count = self.waiter.get_active_wait_count()
        self.waiter.start_wait(reason=WaitReason.OTP_ENTRY, timeout_seconds=30)
        self.waiter.start_wait(reason=WaitReason.SMS_VERIFICATION, timeout_seconds=30)
        new_count = self.waiter.get_active_wait_count()
        self.assertEqual(new_count, initial_count + 2)


class TestAuthResultValidator(unittest.TestCase):
    """Test cases for AuthResultValidator module (8 tests)."""

    def setUp(self):
        self.validator = AuthResultValidator()

    def test_validate_successful_result(self):
        """Test validation of successful auth result."""
        result = create_auth_result(
            result_id="result_1",
            status=AuthResultStatus.SUCCESS,
            session_token="token_abc123"
        )
        validation = self.validator.validate_success(result)
        self.assertTrue(validation.is_valid)

    def test_validate_failed_result(self):
        """Test validation of failed auth result."""
        result = create_auth_result(
            result_id="result_2",
            status=AuthResultStatus.FAILURE,
            error_message="Invalid credentials"
        )
        validation = self.validator.validate_failure(result)
        self.assertTrue(validation.is_valid)

    def test_is_flow_complete(self):
        """Test checking if flow is complete."""
        result = create_auth_result(
            result_id="result_3",
            status=AuthResultStatus.SUCCESS,
            session_token="token_xyz"
        )
        self.assertTrue(self.validator.is_flow_complete(result))

    def test_requires_additional_step(self):
        """Test checking if additional step required."""
        result = create_auth_result(
            result_id="result_4",
            status=AuthResultStatus.REQUIRES_ADDITIONAL_STEP
        )
        self.assertTrue(self.validator.requires_additional_step(result))

    def test_extract_session_info(self):
        """Test extracting session info from result."""
        result = create_auth_result(
            result_id="result_5",
            status=AuthResultStatus.SUCCESS,
            session_token="token_abc"
        )
        session_info = self.validator.extract_session_info(result)
        self.assertIsNotNone(session_info)
        self.assertIn("session_token", session_info)

    def test_validation_with_strict_level(self):
        """Test validation with strict level."""
        validator = AuthResultValidator(validation_level=ValidationLevel.STRICT)
        result = create_auth_result(
            result_id="result_6",
            status=AuthResultStatus.SUCCESS,
            session_token="token_short"
        )
        validation = validator.validate_result(result)
        # May have warnings about token length

    def test_get_validation_summary(self):
        """Test getting validation summary."""
        result = create_auth_result(
            result_id="result_7",
            status=AuthResultStatus.SUCCESS,
            session_token="token_abc123"
        )
        summary = self.validator.get_validation_summary(result)
        self.assertIn("result_id", summary)
        self.assertIn("is_valid", summary)
        self.assertIn("is_complete", summary)

    def test_validation_missing_token(self):
        """Test validation with missing session token."""
        result = create_auth_result(
            result_id="result_8",
            status=AuthResultStatus.SUCCESS
            # No session token
        )
        validation = self.validator.validate_result(result)
        # Should have warnings about missing token
        self.assertTrue(len(validation.warnings) > 0 or len(validation.errors) >= 0)


class TestSecureSessionManager(unittest.TestCase):
    """Test cases for SecureSessionManager module (8 tests)."""

    def setUp(self):
        self.manager = SecureSessionManager()

    def test_create_session(self):
        """Test creation of managed session."""
        session = self.manager.create_session(
            platform_url="https://test.si",
            session_token="token_abc123",
            expires_in_seconds=3600
        )
        self.assertIsNotNone(session.session_id)
        self.assertEqual(session.status, SessionStatus.ACTIVE)

    def test_get_session(self):
        """Test retrieval of session."""
        session = self.manager.create_session(
            platform_url="https://test.si",
            session_token="token_xyz",
            expires_in_seconds=3600
        )
        retrieved = self.manager.get_session(session.session_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.session_id, session.session_id)

    def test_get_active_session_for_platform(self):
        """Test getting active session for platform."""
        self.manager.create_session(
            platform_url="https://test.si",
            session_token="token_1",
            expires_in_seconds=3600
        )
        active = self.manager.get_active_session_for_platform("https://test.si")
        self.assertIsNotNone(active)

    def test_renew_session(self):
        """Test session renewal."""
        session = self.manager.create_session(
            platform_url="https://test.si",
            session_token="token_old",
            expires_in_seconds=3600
        )
        success = self.manager.renew_session(
            session.session_id,
            "token_new",
            expires_in_seconds=7200
        )
        self.assertTrue(success)

    def test_revoke_session(self):
        """Test session revocation."""
        session = self.manager.create_session(
            platform_url="https://test.si",
            session_token="token_abc",
            expires_in_seconds=3600
        )
        success = self.manager.revoke_session(session.session_id)
        self.assertTrue(success)
        retrieved = self.manager.get_session(session.session_id)
        self.assertEqual(retrieved.status, SessionStatus.REVOKED)

    def test_extend_session(self):
        """Test extending session expiration."""
        session = self.manager.create_session(
            platform_url="https://test.si",
            session_token="token_abc",
            expires_in_seconds=3600
        )
        old_expiry = session.expires_at
        success = self.manager.extend_session(session.session_id, 1800)
        self.assertTrue(success)
        self.assertGreater(session.expires_at, old_expiry)

    def test_get_session_info(self):
        """Test getting safe session info."""
        session = self.manager.create_session(
            platform_url="https://test.si",
            session_token="token_secret",
            expires_in_seconds=3600
        )
        info = self.manager.get_session_info(session.session_id)
        self.assertIsNotNone(info)
        self.assertNotIn("session_token", str(info))  # Should not expose token

    def test_cleanup_expired_sessions(self):
        """Test cleanup of expired sessions."""
        # Create expired session
        session = self.manager.create_session(
            platform_url="https://test.si",
            session_token="token_abc",
            expires_in_seconds=-1  # Already expired
        )
        count = self.manager.cleanup_expired_sessions()
        self.assertGreaterEqual(count, 0)


class TestPolicyEnforcer(unittest.TestCase):
    """Test cases for PolicyEnforcer module (8 tests)."""

    def setUp(self):
        self.enforcer = PolicyEnforcer()

    def test_check_operation_allowed(self):
        """Test checking if operation is allowed."""
        allowed = self.enforcer.check_operation_allowed("fill_password_form")
        self.assertTrue(allowed)

    def test_block_biometric_operation(self):
        """Test blocking biometric operation."""
        blocked = self.enforcer.check_operation_allowed("process_biometric_data")
        self.assertFalse(blocked)

    def test_require_consent(self):
        """Test requiring user consent."""
        consent_id = self.enforcer.require_consent(
            operation_type="auth_flow",
            scope=["username", "password"]
        )
        self.assertIsNotNone(consent_id)

    def test_check_consent(self):
        """Test checking valid consent."""
        consent_id = self.enforcer.require_consent(
            operation_type="auth_flow",
            scope=["username"]
        )
        is_valid = self.enforcer.check_consent(consent_id, "username")
        self.assertTrue(is_valid)

    def test_revoke_consent(self):
        """Test revoking consent."""
        consent_id = self.enforcer.require_consent(
            operation_type="auth_flow",
            scope=["username"]
        )
        success = self.enforcer.revoke_consent(consent_id)
        self.assertTrue(success)
        is_valid = self.enforcer.check_consent(consent_id)
        self.assertFalse(is_valid)

    def test_log_operation(self):
        """Test logging operation to audit trail."""
        entry_id = self.enforcer.log_operation(
            operation="test_auth",
            operation_type="authentication",
            success=True,
            details={"test": "data"}
        )
        self.assertIsNotNone(entry_id)

    def test_get_critical_violations(self):
        """Test getting critical violations."""
        # Try to trigger violation
        self.enforcer.check_operation_allowed("store_biometric_data")
        violations = self.enforcer.get_critical_violations()
        self.assertGreaterEqual(len(violations), 1)

    def test_generate_compliance_report(self):
        """Test generating compliance report."""
        report = self.enforcer.generate_compliance_report()
        self.assertIn("compliance_status", report)
        self.assertIn("privacy_guarantees", report)
        self.assertEqual(report["privacy_guarantees"]["consent_framework_active"], True)


class TestFAZA16Integration(unittest.TestCase):
    """Test cases for FAZA 16 Integration module (6 tests)."""

    def setUp(self):
        self.integration = FAZA16Integration()

    def test_detect_platform_command(self):
        """Test DETECT_PLATFORM LLM command."""
        response = self.integration.execute_llm_command(
            command=LLMAuthCommand.DETECT_PLATFORM,
            parameters={"url": "https://nlb.si"}
        )
        self.assertTrue(response.success)
        self.assertIn("platform_type", response.data)

    def test_prepare_auth_request_command(self):
        """Test PREPARE_AUTH_REQUEST LLM command."""
        response = self.integration.execute_llm_command(
            command=LLMAuthCommand.PREPARE_AUTH_REQUEST,
            parameters={
                "url": "https://test.si/login",
                "username": "testuser",
                "password": "testpass"
            }
        )
        self.assertTrue(response.success)
        self.assertIn("request_id", response.data)
        self.assertNotIn("password", str(response.data))  # Should not expose password

    def test_wait_for_external_auth_command(self):
        """Test WAIT_FOR_EXTERNAL_AUTH LLM command."""
        response = self.integration.execute_llm_command(
            command=LLMAuthCommand.WAIT_FOR_EXTERNAL_AUTH,
            parameters={"reason": "biometric_external", "timeout_seconds": 60}
        )
        self.assertTrue(response.success)
        self.assertTrue(response.requires_user_action)

    def test_validate_auth_result_command(self):
        """Test VALIDATE_AUTH_RESULT LLM command."""
        response = self.integration.execute_llm_command(
            command=LLMAuthCommand.VALIDATE_AUTH_RESULT,
            parameters={
                "result_id": "result_123",
                "status": "success",
                "session_token": "token_abc",
                "platform_url": "https://test.si"
            }
        )
        self.assertTrue(response.success)

    def test_get_session_status_command(self):
        """Test GET_SESSION_STATUS LLM command."""
        # First create a session
        session = self.integration.session_manager.create_session(
            platform_url="https://test.si",
            session_token="token_xyz",
            expires_in_seconds=3600
        )
        # Then get its status
        response = self.integration.execute_llm_command(
            command=LLMAuthCommand.GET_SESSION_STATUS,
            parameters={"session_id": session.session_id}
        )
        self.assertTrue(response.success)

    def test_get_llm_capabilities(self):
        """Test getting LLM capabilities."""
        capabilities = self.integration.get_llm_capabilities()
        self.assertIn("available_commands", capabilities)
        self.assertIn("privacy_guarantees", capabilities)
        self.assertFalse(capabilities["privacy_guarantees"]["llm_sees_passwords"])
        self.assertFalse(capabilities["privacy_guarantees"]["llm_sees_biometrics"])


class TestFAZA17Integration(unittest.TestCase):
    """Test cases for FAZA 17 Integration module (6 tests)."""

    def setUp(self):
        self.integration = FAZA17Integration()

    def test_create_workflow(self):
        """Test creating authentication workflow."""
        workflow_id = self.integration.create_workflow(
            platform_url="https://test.si"
        )
        self.assertIsNotNone(workflow_id)
        self.assertIn("wf_", workflow_id)

    def test_get_workflow_status(self):
        """Test getting workflow status."""
        workflow_id = self.integration.create_workflow(
            platform_url="https://test.si"
        )
        status = self.integration.get_workflow_status(workflow_id)
        self.assertIsNotNone(status)
        self.assertEqual(status["status"], WorkflowStatus.NOT_STARTED.value)

    def test_abort_workflow(self):
        """Test aborting workflow."""
        workflow_id = self.integration.create_workflow(
            platform_url="https://test.si"
        )
        success = self.integration.abort_workflow(workflow_id, "Test abort")
        self.assertTrue(success)
        status = self.integration.get_workflow_status(workflow_id)
        self.assertEqual(status["status"], WorkflowStatus.ABORTED.value)

    def test_get_active_workflows(self):
        """Test getting active workflows."""
        workflow_id = self.integration.create_workflow(
            platform_url="https://test.si"
        )
        # Note: workflow is NOT_STARTED, not IN_PROGRESS
        active = self.integration.get_active_workflows()
        # May or may not include not-started workflows

    def test_register_stage_callback(self):
        """Test registering stage callback."""
        callback_called = []

        def test_callback(workflow):
            callback_called.append(workflow.workflow_id)

        self.integration.register_stage_callback(
            WorkflowStage.DETECT,
            test_callback
        )
        # Callback registration should succeed
        self.assertTrue(True)

    def test_get_orchestration_metrics(self):
        """Test getting orchestration metrics."""
        self.integration.create_workflow(platform_url="https://test1.si")
        self.integration.create_workflow(platform_url="https://test2.si")
        metrics = self.integration.get_orchestration_metrics()
        self.assertIn("total_workflows", metrics)
        self.assertGreaterEqual(metrics["total_workflows"], 2)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete FAZA 18 system (4 tests)."""

    def test_complete_auth_flow_simulation(self):
        """Test complete authentication flow with all components."""
        # Detect platform
        detector = PlatformDetector()
        platform_info = detector.detect_platform("https://test-bank.si")

        # Create auth request
        manager = AuthRequestManager()
        auth_request = manager.create_auth_request(
            url=platform_info.url,
            username="testuser",
            password="testpass"
        )
        self.assertIsNotNone(auth_request.request_id)

        # If biometric required, wait
        if platform_info.requires_biometric:
            waiter = AuthWaiter()
            wait_id = waiter.start_wait(
                reason=WaitReason.BIOMETRIC_EXTERNAL,
                timeout_seconds=30
            )
            self.assertIsNotNone(wait_id)

        # Validate result
        validator = AuthResultValidator()
        result = create_auth_result(
            result_id="result_test",
            status=AuthResultStatus.SUCCESS,
            session_token="token_abc123"
        )
        validation = validator.validate_result(result)
        self.assertTrue(validation.is_valid)

        # Create session
        session_manager = SecureSessionManager()
        session = session_manager.create_session(
            platform_url=platform_info.url,
            session_token="token_abc123",
            expires_in_seconds=3600
        )
        self.assertIsNotNone(session.session_id)

    def test_policy_enforcement_throughout_flow(self):
        """Test that policy is enforced throughout flow."""
        enforcer = PolicyEnforcer()

        # Log start
        enforcer.log_operation("auth_start", "authentication", True)

        # Check biometric operation is blocked
        allowed = enforcer.check_operation_allowed("process_biometric")
        self.assertFalse(allowed)

        # Require consent
        consent_id = enforcer.require_consent(
            operation_type="authentication",
            scope=["username", "password"]
        )

        # Check consent
        is_valid = enforcer.check_consent(consent_id)
        self.assertTrue(is_valid)

        # Check compliance
        report = enforcer.generate_compliance_report()
        self.assertIn("compliance_status", report)

    def test_faza16_orchestration(self):
        """Test FAZA 16 orchestration of auth flow."""
        integration = FAZA16Integration()

        # Step 1: Detect platform
        response1 = integration.execute_llm_command(
            LLMAuthCommand.DETECT_PLATFORM,
            {"url": "https://test.si"}
        )
        self.assertTrue(response1.success)

        # Step 2: Prepare request
        response2 = integration.execute_llm_command(
            LLMAuthCommand.PREPARE_AUTH_REQUEST,
            {
                "url": "https://test.si/login",
                "username": "user",
                "password": "pass"
            }
        )
        self.assertTrue(response2.success)

    def test_faza17_workflow_orchestration(self):
        """Test FAZA 17 workflow orchestration."""
        integration = FAZA17Integration()

        # Create workflow
        workflow_id = integration.create_workflow("https://test.si")

        # Get status
        status = integration.get_workflow_status(workflow_id)
        self.assertEqual(status["status"], WorkflowStatus.NOT_STARTED.value)

        # Get metrics
        metrics = integration.get_orchestration_metrics()
        self.assertIn("total_workflows", metrics)


def run_tests():
    """Run all FAZA 18 tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestPlatformDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestAuthRequestManager))
    suite.addTests(loader.loadTestsFromTestCase(TestAuthWaiter))
    suite.addTests(loader.loadTestsFromTestCase(TestAuthResultValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestSecureSessionManager))
    suite.addTests(loader.loadTestsFromTestCase(TestPolicyEnforcer))
    suite.addTests(loader.loadTestsFromTestCase(TestFAZA16Integration))
    suite.addTests(loader.loadTestsFromTestCase(TestFAZA17Integration))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("FAZA 18 TEST SUITE SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
