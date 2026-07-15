"""Integration tests for the Authentication API endpoints.

Tests /register, /login, /logout, /refresh, /me, and RoleChecker middleware.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import RoleChecker
from app.core.exceptions import ForbiddenException
from app.database.models.refresh_token import RefreshToken
from app.database.models.user import User, UserRole
from app.schemas.auth import UserRegisterRequest
from app.services.auth.auth_service import AuthService


@pytest.mark.asyncio
async def test_api_register_success(client: AsyncClient) -> None:
    """Test register endpoint success path."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "api_reg@example.com",
            "password": "Password123!",
            "full_name": "API Register",
            "role": "CANDIDATE",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "api_reg@example.com"
    assert data["full_name"] == "API Register"
    assert data["role"] == "CANDIDATE"
    assert "id" in data
    assert "password_hash" not in data  # Never expose password hashes!


@pytest.mark.asyncio
async def test_api_register_validation_error(client: AsyncClient) -> None:
    """Test register endpoint password strength and email validation."""
    # 1. Invalid email
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "invalid_email",
            "password": "Password123!",
            "full_name": "API Register",
        },
    )
    assert response.status_code == 422

    # 2. Weak password
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "weak@example.com",
            "password": "123",
            "full_name": "API Register",
        },
    )
    assert response.status_code == 422
    assert "at least 8 characters" in response.text


@pytest.mark.asyncio
async def test_api_login_success(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test login endpoint success path returning access/refresh tokens."""
    # Register user first
    await AuthService.register_user(
        db_session,
        UserRegisterRequest(
            email="api_login@example.com",
            password="Password123!",
            full_name="API Login User",
            role=UserRole.RECRUITER,
        ),
    )

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "api_login@example.com",
            "password": "Password123!",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_api_login_failure(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test login endpoint failure with incorrect credentials."""
    # Register user first
    await AuthService.register_user(
        db_session,
        UserRegisterRequest(
            email="api_login_fail@example.com",
            password="Password123!",
            full_name="API Login User",
            role=UserRole.CANDIDATE,
        ),
    )

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "api_login_fail@example.com",
            "password": "WrongPassword!",
        },
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["error"]


@pytest.mark.asyncio
async def test_api_logout_success(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test logout endpoint revokes refresh token."""
    user = await AuthService.register_user(
        db_session,
        UserRegisterRequest(
            email="api_logout@example.com",
            password="Password123!",
            full_name="API Logout User",
            role=UserRole.CANDIDATE,
        ),
    )
    tokens = await AuthService.create_tokens_for_user(db_session, user)

    response = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": tokens.refresh_token},
    )
    assert response.status_code == 200
    assert "Successfully logged out" in response.json()["message"]

    # Verify revoked in DB
    stmt = select(RefreshToken).where(RefreshToken.token == tokens.refresh_token)
    result = await db_session.execute(stmt)
    record = result.scalar_one()
    assert record.is_revoked is True


@pytest.mark.asyncio
async def test_api_refresh_success(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test refresh endpoint rotates access and refresh tokens."""
    user = await AuthService.register_user(
        db_session,
        UserRegisterRequest(
            email="api_refresh@example.com",
            password="Password123!",
            full_name="API Refresh User",
            role=UserRole.CANDIDATE,
        ),
    )
    tokens = await AuthService.create_tokens_for_user(db_session, user)

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens.refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["refresh_token"] != tokens.refresh_token


@pytest.mark.asyncio
async def test_api_get_me_success(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test GET /me returns current user details with authorization headers."""
    user = await AuthService.register_user(
        db_session,
        UserRegisterRequest(
            email="api_me@example.com",
            password="Password123!",
            full_name="API Me User",
            role=UserRole.ADMIN,
        ),
    )
    tokens = await AuthService.create_tokens_for_user(db_session, user)

    headers = {"Authorization": f"Bearer {tokens.access_token}"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "api_me@example.com"
    assert data["role"] == "ADMIN"


@pytest.mark.asyncio
async def test_api_get_me_unauthorized(client: AsyncClient) -> None:
    """Test GET /me returns 401 when Authorization header is missing/invalid."""
    # Missing token
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401

    # Invalid token
    headers = {"Authorization": "Bearer invalid_token"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401


def test_role_checker_middleware() -> None:
    """Test the RoleChecker dependency permissions validations."""
    admin_checker = RoleChecker([UserRole.ADMIN])
    recruiter_checker = RoleChecker([UserRole.RECRUITER])
    candidate_checker = RoleChecker([UserRole.CANDIDATE])

    admin_user = User(role=UserRole.ADMIN)
    recruiter_user = User(role=UserRole.RECRUITER)
    candidate_user = User(role=UserRole.CANDIDATE)

    # Admins should pass admin check
    assert admin_checker(admin_user) == admin_user

    # Candidates should fail admin check
    with pytest.raises(ForbiddenException) as exc_info:
        admin_checker(candidate_user)
    assert exc_info.value.status_code == 403

    # Recruiters should pass recruiter check
    assert recruiter_checker(recruiter_user) == recruiter_user

    # Candidates should fail recruiter check
    with pytest.raises(ForbiddenException):
        recruiter_checker(candidate_user)

    # Candidates should pass candidate check
    assert candidate_checker(candidate_user) == candidate_user
