"""
FAZA 21 - Encrypted Storage

Simulated AES256 encryption with integrity checks and tamper detection.

CRITICAL SECURITY RULE:
    Never store plaintext data to disk.
    All encryption simulated (no actual crypto library).

Author: SENTI OS Core Team
License: Proprietary
GDPR/ZVOP/EU AI Act Compliant
"""

import hashlib
import json
import secrets
from typing import Optional, Any
from datetime import datetime


class EncryptedStorage:
    """
    Provides encrypted storage with simulated AES256 encryption.

    SECURITY GUARANTEE:
        - All data encrypted before writing to disk
        - Integrity checks via HMAC (simulated)
        - Tamper detection
        - Never stores plaintext
    """

    def __init__(self, master_key_manager):
        """
        Initialize encrypted storage.

        Args:
            master_key_manager: MasterKeyManager instance.
        """
        self.master_key_manager = master_key_manager

    def encrypt(self, data: Any) -> bytes:
        """
        Encrypt data using master key.

        Args:
            data: Data to encrypt (will be JSON-serialized).

        Returns:
            Encrypted bytes with IV and integrity tag.

        Raises:
            ValueError: If master key not initialized.
        """
        if not self.master_key_manager.is_initialized():
            raise ValueError("Master key not initialized")

        master_key = self.master_key_manager.get_master_key()

        # Serialize data to JSON
        plaintext = json.dumps(data, default=str).encode()

        # Simulate AES256-GCM encryption
        encrypted_data = self._simulate_aes_encrypt(plaintext, master_key)

        return encrypted_data

    def decrypt(self, encrypted_data: bytes) -> Any:
        """
        Decrypt data using master key.

        Args:
            encrypted_data: Encrypted bytes.

        Returns:
            Decrypted and deserialized data.

        Raises:
            ValueError: If master key not initialized or data tampered.
        """
        if not self.master_key_manager.is_initialized():
            raise ValueError("Master key not initialized")

        master_key = self.master_key_manager.get_master_key()

        # Simulate AES256-GCM decryption
        plaintext = self._simulate_aes_decrypt(encrypted_data, master_key)

        # Deserialize JSON
        data = json.loads(plaintext.decode())

        return data

    def _simulate_aes_encrypt(self, plaintext: bytes, key: bytes) -> bytes:
        """
        Simulate AES256-GCM encryption.

        In production, would use actual AES256-GCM from cryptography library.
        For FAZA 21, we simulate the encryption process.

        Structure: IV (16 bytes) | Ciphertext | Tag (16 bytes)

        Args:
            plaintext: Data to encrypt.
            key: Encryption key.

        Returns:
            Encrypted data with IV and authentication tag.
        """
        # Generate IV
        iv = secrets.token_bytes(16)

        # Simulate encryption (XOR with key-derived stream)
        key_stream = self._generate_key_stream(key, iv, len(plaintext))
        ciphertext = bytes(a ^ b for a, b in zip(plaintext, key_stream))

        # Generate authentication tag (HMAC simulation)
        tag = self._generate_auth_tag(iv, ciphertext, key)

        # Combine: IV | Ciphertext | Tag
        return iv + ciphertext + tag

    def _simulate_aes_decrypt(self, encrypted_data: bytes, key: bytes) -> bytes:
        """
        Simulate AES256-GCM decryption with integrity verification.

        Args:
            encrypted_data: Encrypted data with IV and tag.
            key: Decryption key.

        Returns:
            Decrypted plaintext.

        Raises:
            ValueError: If data tampered or invalid.
        """
        if len(encrypted_data) < 32:  # Min: 16 IV + 16 tag
            raise ValueError("Invalid encrypted data")

        # Extract components
        iv = encrypted_data[:16]
        tag = encrypted_data[-16:]
        ciphertext = encrypted_data[16:-16]

        # Verify authentication tag
        expected_tag = self._generate_auth_tag(iv, ciphertext, key)
        if tag != expected_tag:
            raise ValueError("Data integrity check failed - possible tampering")

        # Simulate decryption
        key_stream = self._generate_key_stream(key, iv, len(ciphertext))
        plaintext = bytes(a ^ b for a, b in zip(ciphertext, key_stream))

        return plaintext

    def _generate_key_stream(self, key: bytes, iv: bytes, length: int) -> bytes:
        """
        Generate key stream for encryption/decryption (simulated).

        Args:
            key: Master key.
            iv: Initialization vector.
            length: Required stream length.

        Returns:
            Key stream bytes.
        """
        stream = b''
        counter = 0

        while len(stream) < length:
            # Simulate counter mode
            block_input = key + iv + counter.to_bytes(4, 'big')
            block = hashlib.sha256(block_input).digest()
            stream += block
            counter += 1

        return stream[:length]

    def _generate_auth_tag(self, iv: bytes, ciphertext: bytes, key: bytes) -> bytes:
        """
        Generate authentication tag (HMAC simulation).

        Args:
            iv: Initialization vector.
            ciphertext: Encrypted data.
            key: Master key.

        Returns:
            Authentication tag (16 bytes).
        """
        # Simulate HMAC-SHA256
        data = iv + ciphertext
        tag_full = hashlib.sha256(key + data + key).digest()
        return tag_full[:16]

    def verify_integrity(self, encrypted_data: bytes) -> bool:
        """
        Verify data integrity without decrypting.

        Args:
            encrypted_data: Encrypted data to verify.

        Returns:
            True if integrity check passes.
        """
        try:
            if len(encrypted_data) < 32:
                return False

            key = self.master_key_manager.get_master_key()
            if not key:
                return False

            iv = encrypted_data[:16]
            tag = encrypted_data[-16:]
            ciphertext = encrypted_data[16:-16]

            expected_tag = self._generate_auth_tag(iv, ciphertext, key)
            return tag == expected_tag
        except Exception:
            return False


def get_info() -> dict:
    """Get module information."""
    return {
        "module": "encrypted_storage",
        "faza": "21",
        "version": "1.0.0",
        "description": "Simulated AES256-GCM encryption with integrity checks",
        "encryption": "simulated_aes256_gcm",
        "stores_plaintext": "false"
    }
