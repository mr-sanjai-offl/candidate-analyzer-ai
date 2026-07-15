"""Integration tests for collection and profile API routes."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.candidate_profile import CandidateProfile
from app.database.models.platform_sync import PlatformSync
from app.database.models.user import User
from app.database.models.enums import PlatformType, JobStatus


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _get_auth_token_and_user_id(client: AsyncClient, db_session: AsyncSession) -> tuple[str, uuid.UUID]:
    """Register, login, and return (access_token, user_id)."""
    email = f"user_{uuid.uuid4().hex[:6]}@test.com"
    password = "SecurePassword123!"

    # 1. Register
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": "Test User",
            "role": "CANDIDATE",
        },
    )
    assert reg.status_code == 201

    # 2. Login
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    # 3. Get user_id via DB (uses same session as the app due to override)
    stmt = select(User).where(User.email == email)
    result = await db_session.execute(stmt)
    user = result.scalars().first()
    assert user is not None

    return token, user.id


async def _ensure_candidate_profile(
    db_session: AsyncSession, user_id: uuid.UUID
) -> uuid.UUID:
    """Create a CandidateProfile for the given user if one doesn't exist."""
    stmt = select(CandidateProfile).where(CandidateProfile.user_id == user_id)
    result = await db_session.execute(stmt)
    existing = result.scalars().first()
    if existing:
        return existing.id

    candidate = CandidateProfile(
        user_id=user_id,
        bio="Test Bio",
        location="USA",
    )
    db_session.add(candidate)
    await db_session.flush()
    return candidate.id


# ── Collection triggers ───────────────────────────────────────────────────────

class TestCollectionTriggers:
    @pytest.mark.asyncio
    async def test_trigger_github_requires_auth(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/collect/github",
            json={"candidate_id": str(uuid.uuid4()), "username": "test_user"},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_trigger_github_success(self, client: AsyncClient, db_session: AsyncSession):
        token, user_id = await _get_auth_token_and_user_id(client, db_session)
        candidate_id = await _ensure_candidate_profile(db_session, user_id)

        # Mock Celery delay call
        with patch("app.tasks.collectors.sync_platform_data") as mock_task:
            mock_task.delay.return_value = MagicMock(id="celery-task-123")

            resp = await client.post(
                "/api/v1/collect/github",
                headers={"Authorization": f"Bearer {token}"},
                json={"candidate_id": str(candidate_id), "username": "octocat"},
            )

        assert resp.status_code == 202
        data = resp.json()
        assert "job_id" in data
        assert data["celery_task_id"] == "celery-task-123"
        assert data["status"] == "QUEUED"


# ── Query Status ──────────────────────────────────────────────────────────────

class TestQueryStatus:
    @pytest.mark.asyncio
    async def test_status_nonexistent_returns_404(self, client: AsyncClient, db_session: AsyncSession):
        token, _ = await _get_auth_token_and_user_id(client, db_session)
        random_job_id = uuid.uuid4()
        resp = await client.get(
            f"/api/v1/collect/status/{random_job_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 404


# ── Get Profiles ──────────────────────────────────────────────────────────────

class TestGetProfiles:
    @pytest.mark.asyncio
    async def test_profile_not_found(self, client: AsyncClient, db_session: AsyncSession):
        token, _ = await _get_auth_token_and_user_id(client, db_session)
        resp = await client.get(
            "/api/v1/profile/github/non_existent_user_abc",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_profile_success(self, client: AsyncClient, db_session: AsyncSession):
        token, user_id = await _get_auth_token_and_user_id(client, db_session)
        candidate_id = await _ensure_candidate_profile(db_session, user_id)

        # Seed database with a successful PlatformSync record
        sync = PlatformSync(
            candidate_profile_id=candidate_id,
            platform=PlatformType.GITHUB,
            username="octocat_profile_test",
            sync_status=JobStatus.SUCCESS,
            normalized_payload={"username": "octocat_profile_test", "followers": 1500},
        )
        db_session.add(sync)
        await db_session.flush()

        resp = await client.get(
            "/api/v1/profile/github/octocat_profile_test",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "octocat_profile_test"
        assert data["followers"] == 1500
