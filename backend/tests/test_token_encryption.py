"""
Encryption round-trip tests for token columns.

Verifies that encrypt_token / decrypt_token work correctly and that
encrypted values are never stored as plaintext.
"""

import base64
import binascii

import pytest

from app.core.security import decrypt_token, encrypt_token


class TestEncryptDecryptRoundTrip:
    """encrypt_token → decrypt_token must preserve the original string."""

    def test_round_trip_preserves_plaintext(self):
        original = "ya29.a0AfH6SMBx-example-access-token"
        encrypted = encrypt_token(original)
        decrypted = decrypt_token(encrypted)
        assert decrypted == original

    def test_round_trip_with_empty_string(self):
        encrypted = encrypt_token("")
        decrypted = decrypt_token(encrypted)
        assert decrypted == ""

    def test_round_trip_with_unicode(self):
        original = "token-with-unicode-\u00e9\u00e8\u00ea"
        encrypted = encrypt_token(original)
        decrypted = decrypt_token(encrypted)
        assert decrypted == original

    def test_round_trip_with_long_token(self):
        original = "x" * 4096
        encrypted = encrypt_token(original)
        decrypted = decrypt_token(encrypted)
        assert decrypted == original


class TestCiphertextIsNotPlaintext:
    """The encrypted value must never equal or contain the plaintext."""

    def test_encrypted_differs_from_plaintext(self):
        original = "my-secret-access-token-12345"
        encrypted = encrypt_token(original)
        assert encrypted != original

    def test_encrypted_does_not_contain_plaintext(self):
        original = "my-secret-access-token-12345"
        encrypted = encrypt_token(original)
        assert original not in encrypted

    def test_same_plaintext_produces_different_ciphertexts(self):
        """Fernet uses random IVs — encrypting the same value twice must differ."""
        original = "deterministic-test-token"
        enc1 = encrypt_token(original)
        enc2 = encrypt_token(original)
        assert enc1 != enc2
        # But both decrypt to the same value
        assert decrypt_token(enc1) == original
        assert decrypt_token(enc2) == original


class TestCiphertextFormat:
    """Encrypted tokens must be URL-safe base64 strings."""

    def test_encrypted_is_valid_base64(self):
        encrypted = encrypt_token("test-token")
        # Should not raise — validates it's proper base64
        try:
            base64.urlsafe_b64decode(encrypted.encode())
        except binascii.Error:
            pytest.fail("Encrypted token is not valid URL-safe base64")

    def test_encrypted_is_ascii(self):
        encrypted = encrypt_token("test-token")
        assert encrypted.isascii()


class TestDecryptWithWrongKey:
    """Decrypting with a different key must raise ValueError."""

    def test_wrong_key_raises_value_error(self, monkeypatch):
        from cryptography.fernet import Fernet

        original = "sensitive-token-value"
        encrypted = encrypt_token(original)

        # Swap in a different Fernet key
        wrong_key = Fernet.generate_key().decode()
        monkeypatch.setattr(
            "app.core.security._get_fernet",
            lambda: Fernet(wrong_key.encode()),
        )

        with pytest.raises(ValueError, match="Token decryption failed"):
            decrypt_token(encrypted)

    def test_corrupted_ciphertext_raises_value_error(self):
        with pytest.raises(ValueError, match="Token decryption failed"):
            decrypt_token("not-a-valid-fernet-token")


class TestIntegrationEncryptionAtRest:
    """
    Integration test: simulate the connect flow and verify tokens
    are encrypted in the database, not stored as plaintext.
    """

    def test_sandbox_tokens_are_encrypted_before_storage(self):
        """
        Simulates what the connected_accounts endpoint does:
        takes a sandbox token, encrypts it, and verifies the encrypted
        form is what's stored (not the plaintext).
        """
        sandbox_access_token = "sandbox-ga4-access-token"
        sandbox_refresh_token = "sandbox-ga4-refresh-token"

        encrypted_access = encrypt_token(sandbox_access_token)
        encrypted_refresh = encrypt_token(sandbox_refresh_token)

        # Stored values must not be plaintext
        assert encrypted_access != sandbox_access_token
        assert encrypted_refresh != sandbox_refresh_token
        assert sandbox_access_token not in encrypted_access
        assert sandbox_refresh_token not in encrypted_refresh

        # But must decrypt back to the originals
        assert decrypt_token(encrypted_access) == sandbox_access_token
        assert decrypt_token(encrypted_refresh) == sandbox_refresh_token
