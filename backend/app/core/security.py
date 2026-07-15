"""Cryptographic security utilities.

Handles password hashing/verification using BCrypt and JWT signing/decoding
using PyJWT to comply with security requirements (Architecture Section 10).
"""

import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.core.config import get_settings
from app.core.exceptions import UnauthorizedException


def hash_password(password: str) -> str:
    """Hash a password using BCrypt.

    Args:
        password: Plaintext password.

    Returns:
        Salted and hashed password string.
    """
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a BCrypt hash.

    BCrypt internally performs constant-time comparisons.

    Args:
        password: Plaintext password.
        hashed_password: Salted and hashed password to compare against.

    Returns:
        True if the password matches, False otherwise.
    """
    try:
        password_bytes = password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def create_access_token(
    subject: str | uuid.UUID,
    expires_delta: timedelta | None = None,
) -> str:
    """Generate a JWT Access Token.

    Args:
        subject: The unique identifier (UUID or email) of the user.
        expires_delta: Optional custom token expiration time window.

    Returns:
        A signed JWT access token.
    """
    settings = get_settings()
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    now = datetime.now(UTC)
    expire = now + expires_delta

    payload = {
        "sub": str(subject),
        "type": "access",
        "iat": now,
        "exp": expire,
        "jti": str(uuid.uuid4()),
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_refresh_token(
    subject: str | uuid.UUID,
    expires_delta: timedelta | None = None,
) -> str:
    """Generate a JWT Refresh Token.

    Args:
        subject: The unique identifier (UUID or email) of the user.
        expires_delta: Optional custom token expiration time window.

    Returns:
        A signed JWT refresh token.
    """
    settings = get_settings()
    if expires_delta is None:
        expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    now = datetime.now(UTC)
    expire = now + expires_delta

    payload = {
        "sub": str(subject),
        "type": "refresh",
        "iat": now,
        "exp": expire,
        "jti": str(uuid.uuid4()),
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_token(token: str, secret_key: str, algorithm: str) -> dict:
    """Decode and validate a JWT.

    Args:
        token: The signed JWT string.
        secret_key: Secret key used to verify token signature.
        algorithm: Hashing algorithm (e.g. HS256).

    Returns:
        The decoded token payload dict.

    Raises:
        UnauthorizedException: If signature validation fails or token is expired.
    """
    try:
        return jwt.decode(token, secret_key, algorithms=[algorithm])
    except jwt.ExpiredSignatureError as e:
        raise UnauthorizedException("Signature has expired") from e
    except jwt.InvalidTokenError as e:
        raise UnauthorizedException("Could not validate credentials") from e
