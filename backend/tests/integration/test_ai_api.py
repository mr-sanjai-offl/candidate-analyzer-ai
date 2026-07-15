"""Integration tests for the AI Layer APIs and endpoints."""

import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import User
from app.database.models.candidate_profile import CandidateProfile
from app.database.models.analysis import Analysis, AnalysisState


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _get_auth_token_and_user_id(client: AsyncClient, db_session: AsyncSession) -> tuple[str, uuid.UUID]:
    """Register, login, and return (access_token, user_id)."""
    email = f"recruiter_{uuid.uuid4().hex[:6]}@test.com"
    password = "SecurePassword123!"

    # 1. Register
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": "Test Recruiter",
            "role": "RECRUITER",
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


async def _ensure_candidate_profile_and_analysis(
    db_session: AsyncSession, user_id: uuid.UUID
) -> tuple[uuid.UUID, uuid.UUID]:
    """Create a CandidateProfile and Analysis record."""
    candidate = CandidateProfile(
        user_id=user_id,
        bio="Integration Bio",
        location="USA",
    )
    db_session.add(candidate)
    await db_session.flush()

    analysis = Analysis(
        candidate_profile_id=candidate.id,
        state=AnalysisState.PENDING,
    )
    db_session.add(analysis)
    await db_session.flush()

    return candidate.id, analysis.id


# ── API Integration Tests ─────────────────────────────────────────────────────

class TestAILayerAPI:
    @pytest.mark.asyncio
    async def test_generate_recruiter_report(self, client: AsyncClient, db_session: AsyncSession):
        token, user_id = await _get_auth_token_and_user_id(client, db_session)
        candidate_id, analysis_id = await _ensure_candidate_profile_and_analysis(db_session, user_id)

        resp = await client.post(
            "/api/v1/reports/recruiter",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "candidate_id": str(candidate_id),
                "analysis_id": str(analysis_id),
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "Executive Summary" in data
        assert "Strengths" in data

    @pytest.mark.asyncio
    async def test_generate_candidate_feedback(self, client: AsyncClient, db_session: AsyncSession):
        token, user_id = await _get_auth_token_and_user_id(client, db_session)
        candidate_id, analysis_id = await _ensure_candidate_profile_and_analysis(db_session, user_id)

        resp = await client.post(
            "/api/v1/reports/candidate",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "candidate_id": str(candidate_id),
                "analysis_id": str(analysis_id),
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "Learning roadmap" in data
        assert "Resume improvements" in data

    @pytest.mark.asyncio
    async def test_chat_message_session(self, client: AsyncClient, db_session: AsyncSession):
        token, user_id = await _get_auth_token_and_user_id(client, db_session)
        candidate_id, _ = await _ensure_candidate_profile_and_analysis(db_session, user_id)

        resp = await client.post(
            "/api/v1/chat/message",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "candidate_id": str(candidate_id),
                "message": "Why is the backend readiness only 72%?",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "session_id" in data
        assert "reply" in data
        assert "72%" in data["reply"]["content"]

    @pytest.mark.asyncio
    async def test_job_match_score(self, client: AsyncClient, db_session: AsyncSession):
        token, user_id = await _get_auth_token_and_user_id(client, db_session)
        candidate_id, _ = await _ensure_candidate_profile_and_analysis(db_session, user_id)

        resp = await client.post(
            "/api/v1/jobs/match",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "candidate_id": str(candidate_id),
                "job_title": "Python Engineer",
                "job_description": "We need a Senior Backend Developer with Python and Docker experience.",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "match_score" in data
        assert data["match_score"] == 85.0

    @pytest.mark.asyncio
    async def test_search_candidates(self, client: AsyncClient, db_session: AsyncSession):
        token, user_id = await _get_auth_token_and_user_id(client, db_session)
        await _ensure_candidate_profile_and_analysis(db_session, user_id)

        resp = await client.get(
            "/api/v1/search?role=backend",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data

    @pytest.mark.asyncio
    async def test_exports_download(self, client: AsyncClient, db_session: AsyncSession):
        token, user_id = await _get_auth_token_and_user_id(client, db_session)
        candidate_id, analysis_id = await _ensure_candidate_profile_and_analysis(db_session, user_id)

        # Generate a recruiter report first to populate report_data
        await client.post(
            "/api/v1/reports/recruiter",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "candidate_id": str(candidate_id),
                "analysis_id": str(analysis_id),
            },
        )

        resp = await client.get(
            f"/api/v1/exports/{analysis_id}?format=pdf",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.headers["Content-Disposition"].startswith("attachment; filename=")
        assert resp.read().startswith(b"%PDF")
