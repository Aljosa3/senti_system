"""
FAZA 21 - Comprehensive Test Suite

Complete test coverage for FAZA 21 Persistence Layer.
Tests all modules with 70+ tests total.

Author: SENTI OS Core Team
License: Proprietary
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Import FAZA 21 modules
from senti_os.core.faza21 import *


class TestMasterKeyManager(unittest.TestCase):
    """Test cases for MasterKeyManager (10 tests)."""

    def setUp(self):
        self.manager = MasterKeyManager()

    def test_bootstrap_random_key(self):
        """Test bootstrapping with random key."""
        success = self.manager.bootstrap_key()
        self.assertTrue(success)
        self.assertTrue(self.manager.is_initialized())

    def test_bootstrap_with_passphrase(self):
        """Test bootstrapping with passphrase."""
        success = self.manager.bootstrap_key("test_passphrase_123")
        self.assertTrue(success)
        self.assertTrue(self.manager.is_initialized())

    def test_get_master_key(self):
        """Test getting master key."""
        self.manager.bootstrap_key()
        key = self.manager.get_master_key()
        self.assertIsNotNone(key)
        self.assertEqual(len(key), 32)  # 256 bits

    def test_key_version(self):
        """Test key versioning."""
        self.manager.bootstrap_key()
        self.assertEqual(self.manager.get_key_version(), 1)

    def test_key_rotation(self):
        """Test key rotation."""
        self.manager.bootstrap_key()
        old_key = self.manager.get_master_key()
        rotated_key = self.manager.rotate_key()
        new_key = self.manager.get_master_key()
        self.assertNotEqual(old_key, new_key)
        self.assertEqual(rotated_key, old_key)
        self.assertEqual(self.manager.get_key_version(), 2)

    def test_clear_key(self):
        """Test clearing key from memory."""
        self.manager.bootstrap_key()
        self.manager.clear_key()
        self.assertFalse(self.manager.is_initialized())

    def test_key_info(self):
        """Test getting key info."""
        self.manager.bootstrap_key("passphrase")
        info = self.manager.get_key_info()
        self.assertTrue(info["initialized"])
        self.assertEqual(info["key_version"], 1)
        self.assertTrue(info["derived_from_passphrase"])

    def test_not_initialized_before_bootstrap(self):
        """Test manager not initialized before bootstrap."""
        self.assertFalse(self.manager.is_initialized())
        self.assertIsNone(self.manager.get_master_key())

    def test_passphrase_derivation_deterministic(self):
        """Test that same passphrase produces same key."""
        manager1 = MasterKeyManager()
        manager2 = MasterKeyManager()
        manager1.bootstrap_key("same_passphrase")
        manager2.bootstrap_key("same_passphrase")
        self.assertEqual(manager1.get_master_key(), manager2.get_master_key())

    def test_different_passphrases_different_keys(self):
        """Test different passphrases produce different keys."""
        manager1 = MasterKeyManager()
        manager2 = MasterKeyManager()
        manager1.bootstrap_key("passphrase1")
        manager2.bootstrap_key("passphrase2")
        self.assertNotEqual(manager1.get_master_key(), manager2.get_master_key())


class TestEncryptedStorage(unittest.TestCase):
    """Test cases for EncryptedStorage (12 tests)."""

    def setUp(self):
        self.key_manager = MasterKeyManager()
        self.key_manager.bootstrap_key()
        self.storage = EncryptedStorage(self.key_manager)

    def test_encrypt_simple_data(self):
        """Test encrypting simple data."""
        data = {"key": "value"}
        encrypted = self.storage.encrypt(data)
        self.assertIsInstance(encrypted, bytes)
        self.assertGreater(len(encrypted), 0)

    def test_decrypt_encrypted_data(self):
        """Test decrypting encrypted data."""
        original = {"test": "data", "number": 42}
        encrypted = self.storage.encrypt(original)
        decrypted = self.storage.decrypt(encrypted)
        self.assertEqual(original, decrypted)

    def test_encrypt_without_key_fails(self):
        """Test encryption fails without key."""
        key_manager = MasterKeyManager()
        storage = EncryptedStorage(key_manager)
        with self.assertRaises(ValueError):
            storage.encrypt({"data": "test"})

    def test_decrypt_without_key_fails(self):
        """Test decryption fails without key."""
        data = {"key": "value"}
        encrypted = self.storage.encrypt(data)

        # Create new storage without key
        key_manager = MasterKeyManager()
        storage = EncryptedStorage(key_manager)
        with self.assertRaises(ValueError):
            storage.decrypt(encrypted)

    def test_tamper_detection(self):
        """Test tampered data detection."""
        data = {"secure": "data"}
        encrypted = self.storage.encrypt(data)

        # Tamper with data
        tampered = bytearray(encrypted)
        tampered[-1] ^= 1  # Flip last bit
        tampered = bytes(tampered)

        with self.assertRaises(ValueError):
            self.storage.decrypt(tampered)

    def test_verify_integrity_valid(self):
        """Test integrity verification of valid data."""
        data = {"test": "data"}
        encrypted = self.storage.encrypt(data)
        self.assertTrue(self.storage.verify_integrity(encrypted))

    def test_verify_integrity_tampered(self):
        """Test integrity verification of tampered data."""
        data = {"test": "data"}
        encrypted = self.storage.encrypt(data)

        # Tamper
        tampered = bytearray(encrypted)
        tampered[0] ^= 1
        tampered = bytes(tampered)

        self.assertFalse(self.storage.verify_integrity(tampered))

    def test_encrypt_complex_data(self):
        """Test encrypting complex nested data."""
        data = {
            "nested": {"key": "value"},
            "list": [1, 2, 3],
            "bool": True
        }
        encrypted = self.storage.encrypt(data)
        decrypted = self.storage.decrypt(encrypted)
        self.assertEqual(data, decrypted)

    def test_encrypt_empty_data(self):
        """Test encrypting empty data."""
        data = {}
        encrypted = self.storage.encrypt(data)
        decrypted = self.storage.decrypt(encrypted)
        self.assertEqual(data, decrypted)

    def test_multiple_encryptions_different_ciphertext(self):
        """Test same data produces different ciphertext (due to IV)."""
        data = {"same": "data"}
        encrypted1 = self.storage.encrypt(data)
        encrypted2 = self.storage.encrypt(data)
        self.assertNotEqual(encrypted1, encrypted2)  # Different IVs

    def test_decrypt_both_produce_same_plaintext(self):
        """Test different ciphertexts decrypt to same plaintext."""
        data = {"same": "data"}
        encrypted1 = self.storage.encrypt(data)
        encrypted2 = self.storage.encrypt(data)
        decrypted1 = self.storage.decrypt(encrypted1)
        decrypted2 = self.storage.decrypt(encrypted2)
        self.assertEqual(decrypted1, decrypted2)

    def test_decrypt_invalid_format_fails(self):
        """Test decryption of invalid format fails."""
        invalid = b"invalid_encrypted_data"
        with self.assertRaises(Exception):
            self.storage.decrypt(invalid)


class TestStorageBackendFS(unittest.TestCase):
    """Test cases for StorageBackendFS (10 tests)."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.backend = StorageBackendFS(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_write_file(self):
        """Test writing file."""
        data = b"test_data"
        success = self.backend.write("test.json", data)
        self.assertTrue(success)

    def test_read_file(self):
        """Test reading file."""
        data = b"test_data"
        self.backend.write("test.json", data)
        read_data = self.backend.read("test.json")
        self.assertEqual(data, read_data)

    def test_read_nonexistent_file(self):
        """Test reading nonexistent file."""
        data = self.backend.read("nonexistent.json")
        self.assertIsNone(data)

    def test_file_exists(self):
        """Test checking file existence."""
        self.assertFalse(self.backend.exists("test.json"))
        self.backend.write("test.json", b"data")
        self.assertTrue(self.backend.exists("test.json"))

    def test_delete_file(self):
        """Test deleting file."""
        self.backend.write("test.json", b"data")
        success = self.backend.delete("test.json")
        self.assertTrue(success)
        self.assertFalse(self.backend.exists("test.json"))

    def test_list_files(self):
        """Test listing files."""
        self.backend.write("file1.json", b"data1")
        self.backend.write("file2.json", b"data2")
        files = self.backend.list_files()
        self.assertIn("file1.json", files)
        self.assertIn("file2.json", files)

    def test_get_file_size(self):
        """Test getting file size."""
        data = b"test_data_123"
        self.backend.write("test.json", data)
        size = self.backend.get_file_size("test.json")
        self.assertEqual(size, len(data))

    def test_get_modified_time(self):
        """Test getting file modification time."""
        self.backend.write("test.json", b"data")
        mod_time = self.backend.get_modified_time("test.json")
        self.assertIsNotNone(mod_time)

    def test_atomic_write_safety(self):
        """Test atomic write creates temp file first."""
        self.backend.write("test.json", b"data")
        # If write was atomic, temp file should not exist
        self.assertFalse(self.backend.exists(".test.json.tmp"))

    def test_overwrite_existing_file(self):
        """Test overwriting existing file."""
        self.backend.write("test.json", b"old_data")
        self.backend.write("test.json", b"new_data")
        data = self.backend.read("test.json")
        self.assertEqual(data, b"new_data")


class TestStorageSchemas(unittest.TestCase):
    """Test cases for StorageSchemas (8 tests)."""

    def test_devices_schema(self):
        """Test devices schema."""
        schema = StorageSchemas.devices_schema()
        self.assertIn("schema_version", schema)
        self.assertIn("devices", schema)
        self.assertIsInstance(schema["devices"], list)

    def test_permissions_schema(self):
        """Test permissions schema."""
        schema = StorageSchemas.permissions_schema()
        self.assertIn("permissions", schema)
        self.assertIsInstance(schema["permissions"], dict)

    def test_sessions_schema(self):
        """Test sessions schema."""
        schema = StorageSchemas.sessions_schema()
        self.assertIn("sessions", schema)
        self.assertIsInstance(schema["sessions"], list)

    def test_settings_schema(self):
        """Test settings schema."""
        schema = StorageSchemas.settings_schema()
        self.assertIn("settings", schema)
        self.assertIsInstance(schema["settings"], dict)

    def test_get_all_schemas(self):
        """Test getting all schemas."""
        schemas = StorageSchemas.get_all_schemas()
        self.assertIn("devices.json", schemas)
        self.assertIn("permissions.json", schemas)
        self.assertIn("sessions.json", schemas)

    def test_validate_valid_schema(self):
        """Test validating valid schema."""
        schema = StorageSchemas.devices_schema()
        self.assertTrue(StorageSchemas.validate_schema("devices.json", schema))

    def test_validate_invalid_schema(self):
        """Test validating invalid schema."""
        invalid = {"invalid": "schema"}
        self.assertFalse(StorageSchemas.validate_schema("devices.json", invalid))

    def test_all_schemas_have_version(self):
        """Test all schemas have version field."""
        schemas = StorageSchemas.get_all_schemas()
        for filename, schema_func in schemas.items():
            schema = schema_func()
            self.assertIn("schema_version", schema)


class TestSecretsManager(unittest.TestCase):
    """Test cases for SecretsManager (12 tests)."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.key_manager = MasterKeyManager()
        self.key_manager.bootstrap_key()
        self.storage = EncryptedStorage(self.key_manager)
        self.backend = StorageBackendFS(self.temp_dir)
        self.secrets = SecretsManager(self.storage, self.backend)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_store_secret(self):
        """Test storing secret."""
        success = self.secrets.store_secret(
            "token_1",
            "oauth_token",
            "secret_value_123"
        )
        self.assertTrue(success)

    def test_get_secret(self):
        """Test retrieving secret."""
        self.secrets.store_secret("token_1", "oauth_token", "value_123")
        value = self.secrets.get_secret("token_1")
        self.assertEqual(value, "value_123")

    def test_get_nonexistent_secret(self):
        """Test retrieving nonexistent secret."""
        value = self.secrets.get_secret("nonexistent")
        self.assertIsNone(value)

    def test_delete_secret(self):
        """Test deleting secret."""
        self.secrets.store_secret("token_1", "oauth_token", "value")
        success = self.secrets.delete_secret("token_1")
        self.assertTrue(success)
        self.assertIsNone(self.secrets.get_secret("token_1"))

    def test_list_secrets(self):
        """Test listing secrets."""
        self.secrets.store_secret("token_1", "oauth_token", "value1")
        self.secrets.store_secret("token_2", "oauth_token", "value2")
        secrets = self.secrets.list_secrets()
        self.assertIn("token_1", secrets)
        self.assertIn("token_2", secrets)

    def test_list_secrets_by_type(self):
        """Test listing secrets by type."""
        self.secrets.store_secret("token_1", "oauth_token", "value1")
        self.secrets.store_secret("session_1", "platform_session", "value2")
        oauth_secrets = self.secrets.list_secrets("oauth_token")
        self.assertIn("token_1", oauth_secrets)
        self.assertNotIn("session_1", oauth_secrets)

    def test_rotate_secret(self):
        """Test secret rotation."""
        self.secrets.store_secret("token_1", "oauth_token", "old_value")
        success = self.secrets.rotate_secret("token_1", "new_value")
        self.assertTrue(success)
        value = self.secrets.get_secret("token_1")
        self.assertEqual(value, "new_value")

    def test_expired_secret_auto_removed(self):
        """Test expired secrets are automatically removed."""
        self.secrets.store_secret(
            "token_1",
            "oauth_token",
            "value",
            expires_in_hours=-1  # Already expired
        )
        value = self.secrets.get_secret("token_1")
        self.assertIsNone(value)

    def test_password_storage_rejected(self):
        """Test password storage is rejected."""
        with self.assertRaises(ValueError):
            self.secrets.store_secret("pass_1", "password", "secret")

    def test_secrets_persist_across_instances(self):
        """Test secrets persist across manager instances."""
        self.secrets.store_secret("token_1", "oauth_token", "persisted_value")

        # Create new instance
        secrets2 = SecretsManager(self.storage, self.backend)
        value = secrets2.get_secret("token_1")
        self.assertEqual(value, "persisted_value")

    def test_secret_with_metadata(self):
        """Test storing secret with metadata."""
        success = self.secrets.store_secret(
            "token_1",
            "oauth_token",
            "value",
            metadata={"platform": "github"}
        )
        self.assertTrue(success)

    def test_cleanup_expired(self):
        """Test cleanup of expired secrets."""
        self.secrets.store_secret("token_1", "oauth_token", "value", expires_in_hours=-1)
        self.secrets.store_secret("token_2", "oauth_token", "value", expires_in_hours=1)
        count = self.secrets._cleanup_expired()
        self.assertGreaterEqual(count, 1)


class TestSnapshotEngine(unittest.TestCase):
    """Test cases for SnapshotEngine (10 tests)."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.backend = StorageBackendFS(self.temp_dir)
        self.backend.write("test1.json", b"data1")
        self.backend.write("test2.json", b"data2")
        self.snapshot = SnapshotEngine(self.backend)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_snapshot(self):
        """Test creating snapshot."""
        snapshot_id = self.snapshot.create_snapshot("manual")
        self.assertIsNotNone(snapshot_id)
        self.assertTrue(snapshot_id.startswith("snapshot_"))

    def test_list_snapshots(self):
        """Test listing snapshots."""
        self.snapshot.create_snapshot("manual")
        snapshots = self.snapshot.list_snapshots()
        self.assertEqual(len(snapshots), 1)

    def test_get_snapshot_info(self):
        """Test getting snapshot info."""
        snapshot_id = self.snapshot.create_snapshot("manual")
        info = self.snapshot.get_snapshot_info(snapshot_id)
        self.assertIsNotNone(info)
        self.assertEqual(info.snapshot_id, snapshot_id)

    def test_restore_snapshot(self):
        """Test restoring snapshot."""
        snapshot_id = self.snapshot.create_snapshot("manual")

        # Modify data
        self.backend.write("test1.json", b"modified_data")

        # Restore
        success = self.snapshot.restore_snapshot(snapshot_id)
        self.assertTrue(success)

        # Verify restoration
        data = self.backend.read("test1.json")
        self.assertEqual(data, b"data1")

    def test_delete_snapshot(self):
        """Test deleting snapshot."""
        snapshot_id = self.snapshot.create_snapshot("manual")
        success = self.snapshot.delete_snapshot(snapshot_id)
        self.assertTrue(success)
        snapshots = self.snapshot.list_snapshots()
        self.assertEqual(len(snapshots), 0)

    def test_cleanup_old_snapshots(self):
        """Test cleaning up old snapshots."""
        # Create multiple snapshots
        for i in range(15):
            self.snapshot.create_snapshot("automatic")

        # Cleanup, keep 5
        deleted = self.snapshot.cleanup_old_snapshots(keep_count=5)
        self.assertEqual(deleted, 10)
        snapshots = self.snapshot.list_snapshots()
        self.assertEqual(len(snapshots), 5)

    def test_snapshot_file_count(self):
        """Test snapshot tracks file count."""
        snapshot_id = self.snapshot.create_snapshot("manual")
        info = self.snapshot.get_snapshot_info(snapshot_id)
        self.assertEqual(info.file_count, 2)  # test1.json, test2.json

    def test_snapshot_type_recorded(self):
        """Test snapshot type is recorded."""
        snapshot_id = self.snapshot.create_snapshot("automatic")
        info = self.snapshot.get_snapshot_info(snapshot_id)
        self.assertEqual(info.snapshot_type, "automatic")

    def test_restore_nonexistent_snapshot_fails(self):
        """Test restoring nonexistent snapshot fails."""
        success = self.snapshot.restore_snapshot("nonexistent_snapshot")
        self.assertFalse(success)

    def test_snapshot_persists_across_instances(self):
        """Test snapshot index persists."""
        snapshot_id = self.snapshot.create_snapshot("manual")

        # Create new instance
        snapshot2 = SnapshotEngine(self.backend)
        snapshots = snapshot2.list_snapshots()
        self.assertEqual(len(snapshots), 1)
        self.assertEqual(snapshots[0].snapshot_id, snapshot_id)


class TestPersistenceManager(unittest.TestCase):
    """Test cases for PersistenceManager (8 tests)."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.key_manager = MasterKeyManager()
        self.storage = EncryptedStorage(self.key_manager)
        self.backend = StorageBackendFS(self.temp_dir)
        self.snapshot = SnapshotEngine(self.backend)
        self.secrets = SecretsManager(self.storage, self.backend)
        self.persistence = PersistenceManager(
            self.key_manager,
            self.storage,
            self.backend,
            self.snapshot,
            self.secrets
        )
        self.persistence.initialize()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_and_load(self):
        """Test saving and loading data."""
        data = {"key": "value", "number": 42}
        success = self.persistence.save("devices", data)
        self.assertTrue(success)

        loaded = self.persistence.load("devices")
        self.assertEqual(data, loaded)

    def test_load_nonexistent_category(self):
        """Test loading nonexistent category."""
        loaded = self.persistence.load("nonexistent")
        self.assertIsNone(loaded)

    def test_delete_category(self):
        """Test deleting data category."""
        self.persistence.save("devices", {"data": "test"})
        success = self.persistence.delete("devices")
        self.assertTrue(success)
        loaded = self.persistence.load("devices")
        self.assertIsNone(loaded)

    def test_create_snapshot(self):
        """Test creating snapshot via persistence manager."""
        self.persistence.save("devices", {"data": "test"})
        snapshot_id = self.persistence.create_snapshot("manual")
        self.assertIsNotNone(snapshot_id)

    def test_restore_snapshot(self):
        """Test restoring snapshot."""
        # Save initial data
        self.persistence.save("devices", {"version": 1})
        snapshot_id = self.persistence.create_snapshot("manual")

        # Modify data
        self.persistence.save("devices", {"version": 2})

        # Restore
        success = self.persistence.restore_snapshot(snapshot_id)
        self.assertTrue(success)

        # Verify restoration
        loaded = self.persistence.load("devices")
        self.assertEqual(loaded["version"], 1)

    def test_get_status(self):
        """Test getting persistence status."""
        status = self.persistence.get_status()
        self.assertTrue(status["initialized"])
        self.assertTrue(status["master_key_initialized"])

    def test_verify_integrity(self):
        """Test verifying data integrity."""
        self.persistence.save("devices", {"data": "test"})
        integrity = self.persistence.verify_integrity("devices")
        self.assertTrue(integrity)

    def test_audit_log(self):
        """Test audit logging."""
        self.persistence.save("devices", {"data": "test"})
        audit_log = self.persistence.get_audit_log()
        self.assertGreater(len(audit_log), 0)


class TestFAZA21Stack(unittest.TestCase):
    """Test cases for FAZA21Stack integration (10 tests)."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.stack = FAZA21Stack(self.temp_dir)
        self.stack.initialize()

    def tearDown(self):
        self.stack.shutdown()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialize_stack(self):
        """Test stack initialization."""
        status = self.stack.get_status()
        self.assertTrue(status["initialized"])

    def test_save_load_integration(self):
        """Test save and load integration."""
        data = {"test": "data"}
        self.stack.save("devices", data)
        loaded = self.stack.load("devices")
        self.assertEqual(data, loaded)

    def test_snapshot_integration(self):
        """Test snapshot functionality."""
        self.stack.save("devices", {"version": 1})
        snapshot_id = self.stack.create_snapshot("manual")
        self.assertIsNotNone(snapshot_id)

    def test_restore_integration(self):
        """Test restore functionality."""
        self.stack.save("devices", {"version": 1})
        snapshot_id = self.stack.create_snapshot()
        self.stack.save("devices", {"version": 2})
        success = self.stack.restore_snapshot(snapshot_id)
        self.assertTrue(success)
        loaded = self.stack.load("devices")
        self.assertEqual(loaded["version"], 1)

    def test_store_secret_integration(self):
        """Test storing secret."""
        success = self.stack.store_secret(
            "token_1",
            "oauth_token",
            "secret_value"
        )
        self.assertTrue(success)

    def test_get_secret_integration(self):
        """Test retrieving secret."""
        self.stack.store_secret("token_1", "oauth_token", "value_123")
        value = self.stack.get_secret("token_1")
        self.assertEqual(value, "value_123")

    def test_multiple_categories(self):
        """Test multiple data categories."""
        self.stack.save("devices", {"devices": []})
        self.stack.save("permissions", {"permissions": {}})
        self.stack.save("sessions", {"sessions": []})

        devices = self.stack.load("devices")
        permissions = self.stack.load("permissions")
        sessions = self.stack.load("sessions")

        self.assertEqual(devices, {"devices": []})
        self.assertEqual(permissions, {"permissions": {}})
        self.assertEqual(sessions, {"sessions": []})

    def test_stack_status(self):
        """Test getting complete stack status."""
        status = self.stack.get_status()
        self.assertIn("initialized", status)
        self.assertIn("master_key_initialized", status)
        self.assertIn("cached_categories", status)

    def test_shutdown_clears_keys(self):
        """Test shutdown clears master key."""
        self.stack.shutdown()
        self.assertFalse(self.stack.master_key_manager.is_initialized())

    def test_data_persists_across_stack_instances(self):
        """Test data persists across stack instances."""
        # Shutdown first stack and re-initialize with passphrase
        self.stack.shutdown()
        self.stack.initialize(passphrase="test_passphrase")
        self.stack.save("devices", {"persisted": "data"})
        self.stack.shutdown()

        # Create new stack instance with same directory and passphrase
        stack2 = FAZA21Stack(self.temp_dir)
        stack2.initialize(passphrase="test_passphrase")
        loaded = stack2.load("devices")
        self.assertEqual(loaded, {"persisted": "data"})
        stack2.shutdown()


def run_tests():
    """Run all FAZA 21 tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestMasterKeyManager))
    suite.addTests(loader.loadTestsFromTestCase(TestEncryptedStorage))
    suite.addTests(loader.loadTestsFromTestCase(TestStorageBackendFS))
    suite.addTests(loader.loadTestsFromTestCase(TestStorageSchemas))
    suite.addTests(loader.loadTestsFromTestCase(TestSecretsManager))
    suite.addTests(loader.loadTestsFromTestCase(TestSnapshotEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestPersistenceManager))
    suite.addTests(loader.loadTestsFromTestCase(TestFAZA21Stack))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("FAZA 21 TEST SUITE SUMMARY")
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
