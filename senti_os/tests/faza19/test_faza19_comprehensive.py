"""
FAZA 19 - Comprehensive Test Suite

Complete test coverage for FAZA 19 Unified Interaction Layer.
Tests all modules with 70+ tests total.

Author: SENTI OS Core Team
License: Proprietary
"""

import unittest
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Import FAZA 19 modules
from senti_os.core.faza19 import *


class TestDeviceIdentityManager(unittest.TestCase):
    """Test cases for DeviceIdentityManager (7 tests)."""

    def setUp(self):
        self.manager = DeviceIdentityManager()

    def test_generate_device_id(self):
        """Test device ID generation."""
        device_id = self.manager.generate_device_id("Test Device", DeviceType.MOBILE)
        self.assertTrue(device_id.startswith("device_"))
        self.assertEqual(len(device_id), 31)

    def test_register_device(self):
        """Test device registration."""
        device = self.manager.register_device(
            "Test Phone",
            DeviceType.MOBILE,
            "user@example.com"
        )
        self.assertIsNotNone(device.device_id)
        self.assertEqual(device.device_name, "Test Phone")
        self.assertEqual(device.status, DeviceStatus.PENDING_VERIFICATION)

    def test_verify_device(self):
        """Test device verification."""
        device = self.manager.register_device("Device", DeviceType.DESKTOP)
        success = self.manager.verify_device(device.device_id)
        self.assertTrue(success)
        self.assertEqual(device.status, DeviceStatus.ACTIVE)

    def test_get_devices_for_user(self):
        """Test getting user devices."""
        self.manager.register_device("Dev1", DeviceType.MOBILE, "user1")
        self.manager.register_device("Dev2", DeviceType.TABLET, "user1")
        devices = self.manager.get_devices_for_user("user1")
        self.assertEqual(len(devices), 2)

    def test_revoke_device(self):
        """Test device revocation."""
        device = self.manager.register_device("Device", DeviceType.WEB)
        success = self.manager.revoke_device(device.device_id)
        self.assertTrue(success)
        self.assertEqual(device.status, DeviceStatus.REVOKED)

    def test_trust_score_update(self):
        """Test trust score updates."""
        device = self.manager.register_device("Device", DeviceType.CLI)
        initial_score = device.trust_score
        self.manager.update_trust_score(device.device_id, 0.2, "Good behavior")
        self.assertGreater(device.trust_score, initial_score)

    def test_is_device_trusted(self):
        """Test device trust checking."""
        device = self.manager.register_device("Device", DeviceType.MOBILE)
        self.manager.verify_device(device.device_id)
        self.assertTrue(self.manager.is_device_trusted(device.device_id, 0.6))


class TestDeviceLinkingService(unittest.TestCase):
    """Test cases for DeviceLinkingService (8 tests)."""

    def setUp(self):
        self.service = DeviceLinkingService()

    def test_initiate_linking(self):
        """Test linking initiation."""
        request = self.service.initiate_linking("device_1", "New Phone")
        self.assertIsNotNone(request.request_id)
        self.assertEqual(request.status, LinkingStatus.QR_GENERATED)

    def test_qr_code_generation(self):
        """Test QR code data generation."""
        request = self.service.initiate_linking("device_1")
        self.assertIn("senti_device_link", request.qr_code_data)

    def test_scan_qr_and_request_link(self):
        """Test QR code scanning."""
        request = self.service.initiate_linking("device_1")
        request_id = self.service.scan_qr_and_request_link(
            request.qr_code_data,
            "device_2"
        )
        self.assertEqual(request_id, request.request_id)
        self.assertEqual(request.status, LinkingStatus.PENDING_APPROVAL)

    def test_approve_linking(self):
        """Test linking approval."""
        request = self.service.initiate_linking("device_1")
        self.service.scan_qr_and_request_link(request.qr_code_data, "device_2")
        success = self.service.approve_linking(request.request_id)
        self.assertTrue(success)

    def test_complete_linking(self):
        """Test linking completion."""
        request = self.service.initiate_linking("device_1")
        self.service.scan_qr_and_request_link(request.qr_code_data, "device_2")
        self.service.approve_linking(request.request_id)
        success = self.service.complete_linking(request.request_id)
        self.assertTrue(success)

    def test_reject_linking(self):
        """Test linking rejection."""
        request = self.service.initiate_linking("device_1")
        success = self.service.reject_linking(request.request_id)
        self.assertTrue(success)

    def test_get_linked_devices(self):
        """Test getting linked devices."""
        request = self.service.initiate_linking("device_1")
        self.service.scan_qr_and_request_link(request.qr_code_data, "device_2")
        self.service.approve_linking(request.request_id)
        self.service.complete_linking(request.request_id)
        linked = self.service.get_linked_devices("device_1")
        self.assertIn("device_2", linked)

    def test_unlink_devices(self):
        """Test unlinking devices."""
        request = self.service.initiate_linking("device_1")
        self.service.scan_qr_and_request_link(request.qr_code_data, "device_2")
        self.service.approve_linking(request.request_id)
        self.service.complete_linking(request.request_id)
        success = self.service.unlink_devices("device_1", "device_2")
        self.assertTrue(success)


class TestSessionController(unittest.TestCase):
    """Test cases for SessionController (10 tests)."""

    def setUp(self):
        self.controller = SessionController()

    def test_create_session(self):
        """Test session creation."""
        session = self.controller.create_session("device_1")
        self.assertIsNotNone(session.session_id)
        self.assertEqual(session.status, SessionStatus.ACTIVE)

    def test_validate_session(self):
        """Test session validation."""
        session = self.controller.create_session("device_1")
        validated = self.controller.validate_session(session.session_token)
        self.assertIsNotNone(validated)
        self.assertEqual(validated.session_id, session.session_id)

    def test_invalid_session_token(self):
        """Test validation with invalid token."""
        result = self.controller.validate_session("invalid_token")
        self.assertIsNone(result)

    def test_revoke_session(self):
        """Test session revocation."""
        session = self.controller.create_session("device_1")
        success = self.controller.revoke_session(session.session_id)
        self.assertTrue(success)
        self.assertEqual(session.status, SessionStatus.REVOKED)

    def test_revoke_all_device_sessions(self):
        """Test revoking all device sessions."""
        self.controller.create_session("device_1")
        self.controller.create_session("device_1")
        count = self.controller.revoke_all_device_sessions("device_1")
        self.assertEqual(count, 2)

    def test_get_active_sessions(self):
        """Test getting active sessions."""
        self.controller.create_session("device_1")
        self.controller.create_session("device_1")
        sessions = self.controller.get_active_sessions("device_1")
        self.assertEqual(len(sessions), 2)

    def test_session_expiration(self):
        """Test expired session detection."""
        session = self.controller.create_session("device_1", expiry_hours=1)
        # Manually expire the session
        session.expires_at = datetime.utcnow() - timedelta(hours=1)
        validated = self.controller.validate_session(session.session_token)
        self.assertIsNone(validated)

    def test_cleanup_expired_sessions(self):
        """Test cleanup of expired sessions."""
        session = self.controller.create_session("device_1", expiry_hours=-1)
        count = self.controller.cleanup_expired_sessions()
        self.assertGreaterEqual(count, 1)

    def test_session_activity_update(self):
        """Test session activity updates."""
        session = self.controller.create_session("device_1")
        initial_activity = session.last_activity
        validated = self.controller.validate_session(session.session_token)
        self.assertGreaterEqual(validated.last_activity, initial_activity)

    def test_multiple_devices(self):
        """Test sessions for multiple devices."""
        self.controller.create_session("device_1")
        self.controller.create_session("device_2")
        sessions1 = self.controller.get_active_sessions("device_1")
        sessions2 = self.controller.get_active_sessions("device_2")
        self.assertEqual(len(sessions1), 1)
        self.assertEqual(len(sessions2), 1)


class TestPermissionManager(unittest.TestCase):
    """Test cases for PermissionManager (10 tests)."""

    def setUp(self):
        self.manager = PermissionManager()

    def test_default_permissions(self):
        """Test default permissions."""
        has_read = self.manager.has_permission("device_1", Permission.READ_STATUS)
        self.assertTrue(has_read)

    def test_grant_permission(self):
        """Test granting permission."""
        success = self.manager.grant_permission("device_1", Permission.EXECUTE_TASK)
        self.assertTrue(success)
        self.assertTrue(self.manager.has_permission("device_1", Permission.EXECUTE_TASK))

    def test_revoke_permission(self):
        """Test revoking permission."""
        self.manager.grant_permission("device_1", Permission.WRITE_FILES)
        success = self.manager.revoke_permission("device_1", Permission.WRITE_FILES)
        self.assertTrue(success)
        self.assertFalse(self.manager.has_permission("device_1", Permission.WRITE_FILES))

    def test_admin_has_all_permissions(self):
        """Test admin permission grants all."""
        self.manager.grant_permission("device_1", Permission.ADMIN)
        self.assertTrue(self.manager.has_permission("device_1", Permission.WRITE_FILES))
        self.assertTrue(self.manager.has_permission("device_1", Permission.VIEW_LOGS))

    def test_get_permissions(self):
        """Test getting all permissions."""
        self.manager.grant_permission("device_1", Permission.READ_FILES)
        perms = self.manager.get_permissions("device_1")
        self.assertIn(Permission.READ_FILES, perms)

    def test_set_permissions(self):
        """Test setting permissions."""
        perms = {Permission.READ_STATUS, Permission.VIEW_LOGS}
        self.manager.set_permissions("device_1", perms)
        self.assertTrue(self.manager.has_permission("device_1", Permission.VIEW_LOGS))

    def test_reset_to_default(self):
        """Test resetting to default permissions."""
        self.manager.grant_permission("device_1", Permission.ADMIN)
        self.manager.reset_to_default("device_1")
        self.assertFalse(self.manager.has_permission("device_1", Permission.ADMIN))

    def test_is_admin(self):
        """Test admin check."""
        self.assertFalse(self.manager.is_admin("device_1"))
        self.manager.grant_permission("device_1", Permission.ADMIN)
        self.assertTrue(self.manager.is_admin("device_1"))

    def test_multiple_devices_independent_permissions(self):
        """Test that device permissions are independent."""
        self.manager.grant_permission("device_1", Permission.ADMIN)
        self.assertFalse(self.manager.has_permission("device_2", Permission.ADMIN))

    def test_permission_persistence(self):
        """Test that permissions persist across checks."""
        self.manager.grant_permission("device_1", Permission.EXECUTE_TASK)
        self.assertTrue(self.manager.has_permission("device_1", Permission.EXECUTE_TASK))
        self.assertTrue(self.manager.has_permission("device_1", Permission.EXECUTE_TASK))


class TestUILEventBus(unittest.TestCase):
    """Test cases for UILEventBus (10 tests)."""

    def setUp(self):
        self.event_bus = UILEventBus()

    def test_subscribe(self):
        """Test event subscription."""
        called = []
        def callback(event):
            called.append(event)

        sub_id = self.event_bus.subscribe(EventCategory.OS_STATUS, callback)
        self.assertIsNotNone(sub_id)

    def test_publish(self):
        """Test event publishing."""
        called = []
        def callback(event):
            called.append(event)

        self.event_bus.subscribe(EventCategory.TASK_PROGRESS, callback)
        event_id = self.event_bus.publish(
            EventCategory.TASK_PROGRESS,
            "task_complete",
            {"task_id": "task_1"}
        )
        self.assertEqual(len(called), 1)

    def test_event_history(self):
        """Test event history."""
        self.event_bus.publish(EventCategory.WARNING, "warning_1", {})
        history = self.event_bus.get_event_history()
        self.assertGreaterEqual(len(history), 1)

    def test_filtered_history(self):
        """Test filtered event history."""
        self.event_bus.publish(EventCategory.ERROR, "error_1", {})
        self.event_bus.publish(EventCategory.WARNING, "warning_1", {})
        errors = self.event_bus.get_event_history(category=EventCategory.ERROR)
        self.assertEqual(len(errors), 1)

    def test_clear_history(self):
        """Test clearing event history."""
        self.event_bus.publish(EventCategory.OS_STATUS, "status", {})
        self.event_bus.clear_history()
        history = self.event_bus.get_event_history()
        self.assertEqual(len(history), 0)

    def test_multiple_subscribers(self):
        """Test multiple subscribers to same category."""
        called1 = []
        called2 = []

        self.event_bus.subscribe(EventCategory.LLM_ROUTING, lambda e: called1.append(e))
        self.event_bus.subscribe(EventCategory.LLM_ROUTING, lambda e: called2.append(e))

        self.event_bus.publish(EventCategory.LLM_ROUTING, "route", {})
        self.assertEqual(len(called1), 1)
        self.assertEqual(len(called2), 1)

    def test_event_data(self):
        """Test event data integrity."""
        called = []
        self.event_bus.subscribe(EventCategory.EXPLAINABILITY, lambda e: called.append(e))

        data = {"explanation": "Test explanation", "confidence": 0.95}
        self.event_bus.publish(EventCategory.EXPLAINABILITY, "explain", data)

        self.assertEqual(called[0].data, data)

    def test_source_device_tracking(self):
        """Test source device tracking in events."""
        called = []
        self.event_bus.subscribe(EventCategory.AUTH_FLOW, lambda e: called.append(e))

        self.event_bus.publish(
            EventCategory.AUTH_FLOW,
            "auth_start",
            {},
            source_device_id="device_1"
        )
        self.assertEqual(called[0].source_device_id, "device_1")

    def test_subscriber_error_isolation(self):
        """Test that subscriber errors don't break event bus."""
        def bad_callback(event):
            raise Exception("Test error")

        good_called = []
        def good_callback(event):
            good_called.append(event)

        self.event_bus.subscribe(EventCategory.ERROR, bad_callback)
        self.event_bus.subscribe(EventCategory.ERROR, good_callback)

        self.event_bus.publish(EventCategory.ERROR, "error", {})
        self.assertEqual(len(good_called), 1)

    def test_event_timestamp(self):
        """Test event timestamp generation."""
        self.event_bus.publish(EventCategory.OS_STATUS, "status", {})
        history = self.event_bus.get_event_history()
        self.assertIsInstance(history[0].timestamp, datetime)


class TestUILProtocol(unittest.TestCase):
    """Test cases for UILProtocol (8 tests)."""

    def setUp(self):
        self.protocol = UILProtocol()

    def test_create_request(self):
        """Test request message creation."""
        msg = self.protocol.create_request("execute_task", {"task": "test"})
        self.assertEqual(msg.message_type, MessageType.REQUEST)
        self.assertIn("action", msg.payload)

    def test_create_response(self):
        """Test response message creation."""
        msg = self.protocol.create_response("req_1", {"status": "success"})
        self.assertEqual(msg.message_type, MessageType.RESPONSE)
        self.assertEqual(msg.request_id, "req_1")

    def test_create_event(self):
        """Test event message creation."""
        msg = self.protocol.create_event("status_update", {"uptime": "24h"})
        self.assertEqual(msg.message_type, MessageType.EVENT)

    def test_message_to_json(self):
        """Test message serialization to JSON."""
        msg = self.protocol.create_request("test", {})
        json_str = msg.to_json()
        self.assertIsInstance(json_str, str)
        self.assertIn("message_id", json_str)

    def test_message_from_json(self):
        """Test message deserialization from JSON."""
        msg1 = self.protocol.create_request("test", {})
        json_str = msg1.to_json()
        msg2 = UILMessage.from_json(json_str)
        self.assertEqual(msg1.message_id, msg2.message_id)

    def test_device_id_tracking(self):
        """Test device ID tracking in messages."""
        msg = self.protocol.create_request("test", {}, device_id="device_1")
        self.assertEqual(msg.device_id, "device_1")

    def test_message_counter(self):
        """Test message ID counter."""
        msg1 = self.protocol.create_request("test1", {})
        msg2 = self.protocol.create_request("test2", {})
        self.assertNotEqual(msg1.message_id, msg2.message_id)

    def test_timestamp_generation(self):
        """Test message timestamp."""
        msg = self.protocol.create_request("test", {})
        self.assertIsInstance(msg.timestamp, datetime)


class TestUILWebSocketServer(unittest.TestCase):
    """Test cases for UILWebSocketServer (10 tests)."""

    def setUp(self):
        self.server = UILWebSocketServer()

    def test_server_start(self):
        """Test server start."""
        self.server.start()
        self.assertTrue(self.server._running)
        self.server.stop()

    def test_connect_device(self):
        """Test device connection."""
        conn_id = self.server.connect("device_1")
        self.assertIsNotNone(conn_id)

    def test_disconnect_device(self):
        """Test device disconnection."""
        conn_id = self.server.connect("device_1")
        self.server.disconnect(conn_id)
        self.assertNotIn(conn_id, self.server._connections)

    def test_send_to_device(self):
        """Test sending message to device."""
        self.server.connect("device_1")
        self.server.send_to_device("device_1", "test_message")
        # Message should be queued

    def test_broadcast(self):
        """Test broadcasting to all devices."""
        self.server.connect("device_1")
        self.server.connect("device_2")
        self.server.broadcast("broadcast_message")
        # Messages should be queued for all

    def test_get_active_connections(self):
        """Test getting active connections."""
        self.server.connect("device_1")
        self.server.connect("device_2")
        connections = self.server.get_active_connections()
        self.assertEqual(len(connections), 2)

    def test_register_message_handler(self):
        """Test registering message handler."""
        def handler(msg):
            pass
        self.server.register_message_handler(handler)
        self.assertIn(handler, self.server._message_handlers)

    def test_connection_object(self):
        """Test connection object properties."""
        conn_id = self.server.connect("device_1")
        conn = self.server._connections[conn_id]
        self.assertEqual(conn.device_id, "device_1")
        self.assertTrue(conn.connected)

    def test_message_queue(self):
        """Test message queuing."""
        conn_id = self.server.connect("device_1")
        conn = self.server._connections[conn_id]
        conn.send("msg1")
        conn.send("msg2")
        self.assertEqual(len(conn.message_queue), 2)

    def test_server_stop(self):
        """Test server stop."""
        self.server.start()
        self.server.connect("device_1")
        self.server.stop()
        self.assertFalse(self.server._running)


class TestIsolationAdapter(unittest.TestCase):
    """Test cases for IsolationAdapter (5 tests)."""

    def setUp(self):
        self.adapter = IsolationAdapter()

    def test_default_mode(self):
        """Test default isolation mode."""
        self.assertEqual(self.adapter.mode, IsolationMode.RELAY)

    def test_set_mode(self):
        """Test setting isolation mode."""
        self.adapter.set_mode(IsolationMode.ISOLATED)
        self.assertEqual(self.adapter.mode, IsolationMode.ISOLATED)

    def test_endpoint_allowed_in_relay_mode(self):
        """Test endpoint checking in relay mode."""
        self.adapter.set_mode(IsolationMode.RELAY)
        self.assertTrue(self.adapter.is_endpoint_allowed("https://relay.example.com"))
        self.assertFalse(self.adapter.is_endpoint_allowed("https://direct.example.com"))

    def test_endpoint_blocked_in_isolated_mode(self):
        """Test all endpoints blocked in isolated mode."""
        self.adapter.set_mode(IsolationMode.ISOLATED)
        self.assertFalse(self.adapter.is_endpoint_allowed("https://any.example.com"))

    def test_relay_queue(self):
        """Test relay message queuing."""
        self.adapter.queue_relay_message({"type": "test"})
        queue = self.adapter.get_relay_queue()
        self.assertEqual(len(queue), 1)


class TestIntegration(unittest.TestCase):
    """Integration tests with FAZA 16/17/18 (7 tests)."""

    def test_complete_device_flow(self):
        """Test complete device registration and session flow."""
        # Initialize components
        device_manager = DeviceIdentityManager()
        session_controller = SessionController()
        permission_manager = PermissionManager()

        # Register device
        device = device_manager.register_device("Test Device", DeviceType.MOBILE)
        device_manager.verify_device(device.device_id)

        # Create session
        session = session_controller.create_session(device.device_id)

        # Grant permissions
        permission_manager.grant_permission(device.device_id, Permission.EXECUTE_TASK)

        # Verify flow
        self.assertTrue(device_manager.is_device_trusted(device.device_id))
        self.assertIsNotNone(session_controller.validate_session(session.session_token))
        self.assertTrue(permission_manager.has_permission(device.device_id, Permission.EXECUTE_TASK))

    def test_multi_device_linking(self):
        """Test linking multiple devices."""
        device_manager = DeviceIdentityManager()
        linking_service = DeviceLinkingService()

        # Register devices
        dev1 = device_manager.register_device("Device 1", DeviceType.DESKTOP)
        dev2 = device_manager.register_device("Device 2", DeviceType.MOBILE)

        # Link devices
        request = linking_service.initiate_linking(dev1.device_id)
        linking_service.scan_qr_and_request_link(request.qr_code_data, dev2.device_id)
        linking_service.approve_linking(request.request_id)
        linking_service.complete_linking(request.request_id)

        # Verify linking
        linked = linking_service.get_linked_devices(dev1.device_id)
        self.assertIn(dev2.device_id, linked)

    def test_event_bus_integration(self):
        """Test event bus with device events."""
        event_bus = UILEventBus()
        device_manager = DeviceIdentityManager()

        # Register device
        device = device_manager.register_device("Device", DeviceType.MOBILE)

        # Publish device event
        event_id = event_bus.publish(
            EventCategory.OS_STATUS,
            "device_registered",
            {"device_id": device.device_id},
            source_device_id=device.device_id
        )

        # Verify event
        history = event_bus.get_event_history(category=EventCategory.OS_STATUS)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].data["device_id"], device.device_id)

    def test_protocol_message_flow(self):
        """Test protocol message creation and parsing."""
        protocol = UILProtocol()

        # Create request
        request = protocol.create_request("execute_task", {"task_id": "task_1"}, device_id="device_1")

        # Serialize and deserialize
        json_str = request.to_json()
        parsed = UILMessage.from_json(json_str)

        # Create response
        response = protocol.create_response(parsed.message_id, {"status": "success"})

        # Verify flow
        self.assertEqual(parsed.payload["action"], "execute_task")
        self.assertEqual(response.request_id, request.message_id)

    def test_websocket_with_sessions(self):
        """Test WebSocket server with session validation."""
        websocket = UILWebSocketServer()
        session_controller = SessionController()

        # Create session
        session = session_controller.create_session("device_1")

        # Connect via WebSocket
        conn_id = websocket.connect("device_1")

        # Validate session
        validated = session_controller.validate_session(session.session_token)

        # Verify
        self.assertIsNotNone(validated)
        self.assertEqual(validated.device_id, "device_1")
        self.assertIn(conn_id, websocket.get_active_connections())

    def test_mobile_bridge_with_permissions(self):
        """Test mobile bridge with permission enforcement."""
        permission_manager = PermissionManager()
        session_controller = SessionController()
        bridge = MobileBridgeController(permission_manager, session_controller)

        # Create session
        session = session_controller.create_session("device_1")

        # Grant permission
        permission_manager.grant_permission("device_1", Permission.EXECUTE_TASK)

        # Execute command
        result = bridge.validate_and_execute(
            session.session_token,
            "execute_task",
            {"task": "test"}
        )

        # Verify
        self.assertTrue(result["success"])

    def test_full_stack_initialization(self):
        """Test complete FAZA 19 stack initialization."""
        stack = FAZA19Stack()

        # Start stack
        stack.start()

        # Register device
        device = stack.device_identity_manager.register_device(
            "Test Device",
            DeviceType.MOBILE
        )

        # Create session
        session = stack.session_controller.create_session(device.device_id)

        # Grant permissions
        stack.permission_manager.grant_permission(device.device_id, Permission.EXECUTE_TASK)

        # Publish event
        event_id = stack.event_bus.publish(
            EventCategory.OS_STATUS,
            "system_ready",
            {}
        )

        # Get status
        status = stack.get_stack_status()

        # Verify
        self.assertEqual(status["device_manager"]["total_devices"], 1)
        self.assertEqual(status["session_controller"]["total_sessions"], 1)

        # Stop stack
        stack.stop()


def run_tests():
    """Run all FAZA 19 tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestDeviceIdentityManager))
    suite.addTests(loader.loadTestsFromTestCase(TestDeviceLinkingService))
    suite.addTests(loader.loadTestsFromTestCase(TestSessionController))
    suite.addTests(loader.loadTestsFromTestCase(TestPermissionManager))
    suite.addTests(loader.loadTestsFromTestCase(TestUILEventBus))
    suite.addTests(loader.loadTestsFromTestCase(TestUILProtocol))
    suite.addTests(loader.loadTestsFromTestCase(TestUILWebSocketServer))
    suite.addTests(loader.loadTestsFromTestCase(TestIsolationAdapter))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("FAZA 19 TEST SUITE SUMMARY")
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
