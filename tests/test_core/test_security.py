"""Tests for core/security module."""

from app.core.security import hash_password, verify_password, create_access_token, decode_access_token


class TestPasswordHashing:
    def test_hash_and_verify(self):
        password = "my_secure_password"
        hashed = hash_password(password)
        assert hashed != password
        assert verify_password(password, hashed) is True

    def test_wrong_password_fails(self):
        hashed = hash_password("correct")
        assert verify_password("wrong", hashed) is False

    def test_same_password_different_hashes(self):
        pwd = "test"
        h1 = hash_password(pwd)
        h2 = hash_password(pwd)
        assert h1 != h2  # bcrypt salts
        assert verify_password(pwd, h1) is True
        assert verify_password(pwd, h2) is True


class TestJWT:
    def test_create_and_decode(self):
        data = {"sub": "user@test.com"}
        token = create_access_token(data)
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "user@test.com"

    def test_expired_token_returns_none(self):
        from datetime import timedelta
        token = create_access_token({"sub": "test"}, expires_delta=timedelta(seconds=-1))
        payload = decode_access_token(token)
        assert payload is None

    def test_invalid_token_returns_none(self):
        assert decode_access_token("invalid.token.here") is None
        assert decode_access_token("") is None
