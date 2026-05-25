"""
Tests for auth utilities: JWT token creation/verification, password hashing.
"""
import pytest
from datetime import timedelta
from auth_utils import (
    hash_password, verify_password, create_access_token,
    verify_token, generate_reset_token, generate_verification_token
)


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_hash_password_returns_bcrypt_hash(self):
        hashed = hash_password("TestPassword123!")
        assert hashed.startswith("$2b$")

    def test_verify_password_correct(self):
        password = "SecurePassword123!"
        hashed = hash_password(password)
        assert verify_password(hashed, password) is True

    def test_verify_password_incorrect(self):
        hashed = hash_password("CorrectPassword")
        assert verify_password(hashed, "WrongPassword") is False

    def test_hash_password_unique_salts(self):
        password = "SamePassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2  # Different salts

    def test_verify_password_empty_string(self):
        hashed = hash_password("ValidPassword")
        assert verify_password(hashed, "") is False


class TestJWTTokens:
    """Test JWT token creation and verification."""

    def test_create_token_success(self):
        token = create_access_token({"user_id": "test_001", "email": "test@example.com"})
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_valid_token(self):
        data = {"user_id": "test_001", "email": "test@example.com"}
        token = create_access_token(data)
        payload = verify_token(token)
        assert payload is not None
        assert payload["user_id"] == "test_001"
        assert payload["email"] == "test@example.com"

    def test_verify_expired_token(self):
        data = {"user_id": "test_001"}
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        payload = verify_token(token)
        assert payload is None

    def test_verify_invalid_token(self):
        payload = verify_token("invalid.token.string")
        assert payload is None

    def test_token_contains_exp_and_iat(self):
        token = create_access_token({"user_id": "test"})
        payload = verify_token(token)
        assert "exp" in payload
        assert "iat" in payload

    def test_custom_expiry(self):
        token = create_access_token(
            {"user_id": "test"},
            expires_delta=timedelta(hours=2)
        )
        payload = verify_token(token)
        assert payload is not None


class TestTokenGeneration:
    """Test reset and verification token generation."""

    def test_reset_token_is_string(self):
        token = generate_reset_token()
        assert isinstance(token, str)
        assert len(token) > 20

    def test_reset_tokens_are_unique(self):
        token1 = generate_reset_token()
        token2 = generate_reset_token()
        assert token1 != token2

    def test_verification_token_is_string(self):
        token = generate_verification_token()
        assert isinstance(token, str)
        assert len(token) > 20
