"""Unit tests for the AuthService.

Verifies user registration, credential authentication, logout,
and refresh token rotation/compromise-detection logic.
"""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ForbiddenException,
    UnauthorizedException,
    ValidationException,
)
from app.core.security import create_refresh_token
from app.database.models.refresh_token import RefreshToken
from app.database.models.user import UserRole
from app.schemas.auth import UserRegisterRequest
from app.services.auth.auth_service import AuthService


@pytest.mark.asyncio
async def test_register_user_success(db_session: AsyncSession) -> None:
    """Test successful user registration."""
    register_data = UserRegisterRequest(
        email="test_reg@example.com",
        password="Password123!",
        full_name="Test Register",
        role=UserRole.CANDIDATE,
    )

    user = await AuthService.register_user(db_session, register_data)
    assert user.id is not None
    assert user.email == "test_reg@example.com"
    assert user.full_name == "Test Register"
    assert user.role == UserRole.CANDIDATE
    assert user.is_active is True
    assert user.is_verified is False

    # Verify stored in DB
    db_user = await AuthService.get_user_by_id(db_session, user.id)
    assert db_user is not None
    assert db_user.email == "test_reg@example.com"


@pytest.mark.asyncio
async def test_register_duplicate_email(db_session: AsyncSession) -> None:
    """Test that registering duplicate email raises ValidationException."""
    register_data = UserRegisterRequest(
        email="dup@example.com",
        password="Password123!",
        full_name="Duplicate User",
        role=UserRole.CANDIDATE,
    )

    await AuthService.register_user(db_session, register_data)

    with pytest.raises(ValidationException) as exc_info:
        await AuthService.register_user(db_session, register_data)
    assert exc_info.value.status_code == 422
    assert "already registered" in exc_info.value.message


@pytest.mark.asyncio
async def test_authenticate_user_success(db_session: AsyncSession) -> None:
    """Test successful login credential validation."""
    register_data = UserRegisterRequest(
        email="login@example.com",
        password="Password123!",
        full_name="Login User",
        role=UserRole.RECRUITER,
    )
    user = await AuthService.register_user(db_session, register_data)
    assert user.last_login is None

    auth_user = await AuthService.authenticate_user(
        db_session,
        "login@example.com",
        "Password123!",
    )
    assert auth_user.id == user.id
    assert auth_user.last_login is not None


@pytest.mark.asyncio
async def test_authenticate_user_invalid_credentials(db_session: AsyncSession) -> None:
    """Test login failure with wrong password or email."""
    register_data = UserRegisterRequest(
        email="login_fail@example.com",
        password="Password123!",
        full_name="Fail User",
        role=UserRole.CANDIDATE,
    )
    await AuthService.register_user(db_session, register_data)

    # Wrong password
    with pytest.raises(UnauthorizedException) as exc_info:
        await AuthService.authenticate_user(
            db_session,
            "login_fail@example.com",
            "WrongPassword!",
        )
    assert exc_info.value.status_code == 401

    # Non-existent email
    with pytest.raises(UnauthorizedException) as exc_info:
        await AuthService.authenticate_user(
            db_session,
            "nonexistent@example.com",
            "Password123!",
        )
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_authenticate_inactive_user(db_session: AsyncSession) -> None:
    """Test that inactive users are blocked from logging in."""
    register_data = UserRegisterRequest(
        email="inactive@example.com",
        password="Password123!",
        full_name="Inactive User",
        role=UserRole.CANDIDATE,
    )
    user = await AuthService.register_user(db_session, register_data)

    # Deactivate user
    user.is_active = False
    db_session.add(user)
    await db_session.commit()

    with pytest.raises(ForbiddenException) as exc_info:
        await AuthService.authenticate_user(
            db_session,
            "inactive@example.com",
            "Password123!",
        )
    assert exc_info.value.status_code == 403
    assert "inactive" in exc_info.value.message


@pytest.mark.asyncio
async def test_create_tokens_and_rotation(db_session: AsyncSession) -> None:
    """Test normal refresh token rotation (RTR) workflow."""
    register_data = UserRegisterRequest(
        email="rotate@example.com",
        password="Password123!",
        full_name="Rotate User",
        role=UserRole.CANDIDATE,
    )
    user = await AuthService.register_user(db_session, register_data)

    # 1. Generate tokens
    tokens = await AuthService.create_tokens_for_user(db_session, user)
    assert tokens.access_token is not None
    assert tokens.refresh_token is not None

    # Verify refresh token in DB
    stmt = select(RefreshToken).where(RefreshToken.token == tokens.refresh_token)
    result = await db_session.execute(stmt)
    token_record = result.scalar_one_or_none()
    assert token_record is not None
    assert token_record.is_revoked is False

    # 2. Perform rotation
    rotated_tokens = await AuthService.refresh_tokens(
        db_session,
        tokens.refresh_token,
    )
    assert rotated_tokens.access_token is not None
    assert rotated_tokens.refresh_token is not None
    assert rotated_tokens.refresh_token != tokens.refresh_token

    # Verify old token is revoked in DB
    await db_session.refresh(token_record)
    assert token_record.is_revoked is True

    # Verify new token is active in DB
    stmt_new = select(RefreshToken).where(
        RefreshToken.token == rotated_tokens.refresh_token,
    )
    result_new = await db_session.execute(stmt_new)
    new_record = result_new.scalar_one_or_none()
    assert new_record is not None
    assert new_record.is_revoked is False


@pytest.mark.asyncio
async def test_refresh_token_replay_attack_detection(db_session: AsyncSession) -> None:
    """Test that reuse of a rotated refresh token revokes all user sessions."""
    register_data = UserRegisterRequest(
        email="replay@example.com",
        password="Password123!",
        full_name="Replay User",
        role=UserRole.CANDIDATE,
    )
    user = await AuthService.register_user(db_session, register_data)

    # Generate first pair
    tokens1 = await AuthService.create_tokens_for_user(db_session, user)

    # Generate second pair (normal rotation)
    await AuthService.refresh_tokens(db_session, tokens1.refresh_token)

    # Generate an extra unrelated token record to verify if it gets swept
    await AuthService.create_tokens_for_user(db_session, user)

    # Replay attack: attempt to use tokens1.refresh_token again!
    with pytest.raises(UnauthorizedException) as exc_info:
        await AuthService.refresh_tokens(db_session, tokens1.refresh_token)
    assert exc_info.value.status_code == 401
    assert "Security breach detected" in exc_info.value.message

    # Verify all tokens for the user are now revoked
    stmt = select(RefreshToken).where(RefreshToken.user_id == user.id)
    result = await db_session.execute(stmt)
    records = result.scalars().all()

    assert len(records) == 3
    assert all(r.is_revoked for r in records)


@pytest.mark.asyncio
async def test_refresh_token_expired(db_session: AsyncSession) -> None:
    """Test that refreshing with an expired token raises UnauthorizedException."""
    register_data = UserRegisterRequest(
        email="expired_token@example.com",
        password="Password123!",
        full_name="Expired User",
        role=UserRole.CANDIDATE,
    )
    user = await AuthService.register_user(db_session, register_data)

    # Create an expired token record
    expired_token_str = create_refresh_token(user.id, expires_delta=timedelta(days=-1))

    # Save to DB
    token_record = RefreshToken(
        user_id=user.id,
        token=expired_token_str,
        expires_at=datetime.now(UTC) - timedelta(days=1),
        is_revoked=False,
    )
    db_session.add(token_record)
    await db_session.commit()

    with pytest.raises(UnauthorizedException) as exc_info:
        await AuthService.refresh_tokens(db_session, expired_token_str)
    assert exc_info.value.status_code == 401
    assert "expired" in exc_info.value.message


@pytest.mark.asyncio
async def test_revoke_refresh_token_logout(db_session: AsyncSession) -> None:
    """Test revoking token (logout path)."""
    register_data = UserRegisterRequest(
        email="logout@example.com",
        password="Password123!",
        full_name="Logout User",
        role=UserRole.CANDIDATE,
    )
    user = await AuthService.register_user(db_session, register_data)

    tokens = await AuthService.create_tokens_for_user(db_session, user)

    await AuthService.revoke_refresh_token(db_session, tokens.refresh_token)

    # Verify revoked in DB
    stmt = select(RefreshToken).where(RefreshToken.token == tokens.refresh_token)
    result = await db_session.execute(stmt)
    record = result.scalar_one()
    assert record.is_revoked is True
