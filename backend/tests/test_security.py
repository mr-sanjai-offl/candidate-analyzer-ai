"""Unit tests for security utilities.

Verifies password hashing, comparison, token creation, and parsing.
"""

from datetime import timedelta

import pytest

from app.core.exceptions import UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hashing() -> None:
    """Test that passwords are hashed and validated successfully."""
    password = "SuperSecretPassword123!"
    hashed = hash_password(password)

    assert hashed != password
    assert hashed.startswith("$2b$")  # standard bcrypt prefix

    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False
    assert verify_password(password, "InvalidHash") is False


def test_jwt_generation_and_decoding() -> None:
    """Test JWT creation and decoding of access/refresh tokens."""
    from app.core.config import get_settings

    settings = get_settings()
    subject = "user-1234"

    # Test Access Token
    access_token = create_access_token(subject)
    decoded_access = decode_token(
        access_token,
        settings.JWT_SECRET_KEY,
        settings.JWT_ALGORITHM,
    )
    assert decoded_access["sub"] == subject
    assert decoded_access["type"] == "access"

    # Test Refresh Token
    refresh_token = create_refresh_token(subject)
    decoded_refresh = decode_token(
        refresh_token,
        settings.JWT_SECRET_KEY,
        settings.JWT_ALGORITHM,
    )
    assert decoded_refresh["sub"] == subject
    assert decoded_refresh["type"] == "refresh"


def test_jwt_invalid_token() -> None:
    """Test that invalid tokens raise UnauthorizedException."""
    from app.core.config import get_settings

    settings = get_settings()

    with pytest.raises(UnauthorizedException) as exc_info:
        decode_token(
            "invalid.jwt.token",
            settings.JWT_SECRET_KEY,
            settings.JWT_ALGORITHM,
        )
    assert exc_info.value.status_code == 401
    assert "Could not validate credentials" in exc_info.value.message


def test_jwt_expired_token() -> None:
    """Test that expired tokens raise UnauthorizedException."""
    from app.core.config import get_settings

    settings = get_settings()
    subject = "user-123"

    # Create a token that expired 5 minutes ago
    expired_token = create_access_token(subject, expires_delta=timedelta(minutes=-5))

    with pytest.raises(UnauthorizedException) as exc_info:
        decode_token(
            expired_token,
            settings.JWT_SECRET_KEY,
            settings.JWT_ALGORITHM,
        )
    assert exc_info.value.status_code == 401
    assert "Signature has expired" in exc_info.value.message
