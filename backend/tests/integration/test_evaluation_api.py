"""Integration tests for capability evaluation APIs and background tasks."""

import uuid
from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.candidate_profile import CandidateProfile
from app.database.models.enums import JobStatus, PlatformType, ProficiencyLevel
from app.database.models.user import User
from app.database.models.capability_score import CapabilityScore
from app.database.models.readiness_report import ReadinessReport


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

    # 3. Get user_id
    stmt = select(User).where(User.email == email)
    result = await db_session.execute(stmt)
    user = result.scalars().first()
    assert user is not None

    return token, user.id


async def _ensure_candidate_profile(
    db_session: AsyncSession, user_id: uuid.UUID
) -> uuid.UUID:
    """Create a CandidateProfile for the given user."""
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


# ── API Integration Tests ─────────────────────────────────────────────────────

class TestEvaluationAPI:
    @pytest.mark.asyncio
    async def test_trigger_pipeline_success(self, client: AsyncClient, db_session: AsyncSession):
        token, user_id = await _get_auth_token_and_user_id(client, db_session)
        candidate_id = await _ensure_candidate_profile(db_session, user_id)

        # Mock Celery send_task to bypass redis execution
        with patch("app.api.v1.evaluation.celery_app.send_task") as mock_send:
            mock_send.return_value = MagicMock(id="celery-pipeline-job-456")

            resp = await client.post(
                "/api/v1/analyze/skills",
                headers={"Authorization": f"Bearer {token}"},
                json={"candidate_id": str(candidate_id)},
            )

        assert resp.status_code == 202
        data = resp.json()
        assert "job_id" in data
        assert data["celery_task_id"] == "celery-pipeline-job-456"
        assert data["status"] == "QUEUED"

    @pytest.mark.asyncio
    async def test_get_scores_not_found(self, client: AsyncClient, db_session: AsyncSession):
        token, user_id = await _get_auth_token_and_user_id(client, db_session)
        candidate_id = await _ensure_candidate_profile(db_session, user_id)

        resp = await client.get(
            f"/api/v1/scores/{candidate_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_scores_success(self, client: AsyncClient, db_session: AsyncSession):
        token, user_id = await _get_auth_token_and_user_id(client, db_session)
        candidate_id = await _ensure_candidate_profile(db_session, user_id)

        # Seed database with a CapabilityScore record
        score = CapabilityScore(
            candidate_profile_id=candidate_id,
            category="Programming Languages",
            confidence_score=85.0,
            experience_score=70.0,
            depth_score=65.0,
            breadth_score=40.0,
            proficiency=ProficiencyLevel.ADVANCED,
            explanation={"summary": "Expert level"},
        )
        db_session.add(score)
        await db_session.flush()

        resp = await client.get(
            f"/api/v1/scores/{candidate_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["scores"]) == 1
        assert data["scores"][0]["category"] == "Programming Languages"
        assert data["scores"][0]["confidence_score"] == 85.0

    @pytest.mark.asyncio
    async def test_get_readiness_success(self, client: AsyncClient, db_session: AsyncSession):
        token, user_id = await _get_auth_token_and_user_id(client, db_session)
        candidate_id = await _ensure_candidate_profile(db_session, user_id)

        # Seed readiness report
        report = ReadinessReport(
            candidate_profile_id=candidate_id,
            backend_score=75.0,
            frontend_score=50.0,
            fullstack_score=65.0,
            ai_score=0.0,
            data_score=0.0,
            devops_score=0.0,
            cloud_score=0.0,
            cybersecurity_score=0.0,
            embedded_score=0.0,
            explanation={"Backend": {}},
        )
        db_session.add(report)
        await db_session.flush()

        resp = await client.get(
            f"/api/v1/readiness/{candidate_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["backend_score"] == 75.0
        assert data["frontend_score"] == 50.0
