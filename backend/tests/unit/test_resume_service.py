"""Unit tests for ResumeService."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.database.models.resume import ParsingState, UploadedResume
from app.services.resume_service import ResumeService


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_resume_repo():
    return AsyncMock()


@pytest.fixture
def mock_version_repo():
    return AsyncMock()


@pytest.fixture
def mock_storage():
    return MagicMock()


@pytest.fixture
def mock_validator():
    return MagicMock()


@pytest.fixture
def resume_service(mock_resume_repo, mock_version_repo, mock_storage, mock_validator):
    return ResumeService(
        resume_repo=mock_resume_repo,
        version_repo=mock_version_repo,
        storage=mock_storage,
        validator=mock_validator,
    )


@pytest.fixture
def sample_owner_id():
    return uuid.uuid4()


@pytest.fixture
def sample_resume(sample_owner_id):
    r = MagicMock(spec=UploadedResume)
    r.id = uuid.uuid4()
    r.owner_id = sample_owner_id
    r.original_filename = "resume.pdf"
    r.storage_path = f"{sample_owner_id}/{r.id}/resume.pdf"
    r.file_hash = "abc123"
    r.file_size = 1024
    r.mime_type = "application/pdf"
    r.parsing_status = ParsingState.PENDING
    r.deleted_at = None
    return r


# ── hash ─────────────────────────────────────────────────────────────────────

class TestComputeHash:
    def test_produces_64_char_hex(self):
        digest = ResumeService._compute_hash(b"hello world")
        assert len(digest) == 64
        assert all(c in "0123456789abcdef" for c in digest)

    def test_identical_bytes_same_hash(self):
        assert ResumeService._compute_hash(b"abc") == ResumeService._compute_hash(b"abc")

    def test_different_bytes_different_hash(self):
        assert ResumeService._compute_hash(b"abc") != ResumeService._compute_hash(b"xyz")


# ── upload_resume ─────────────────────────────────────────────────────────────

class TestUploadResume:
    @pytest.mark.asyncio
    async def test_upload_success(
        self, resume_service, mock_resume_repo, mock_storage, mock_validator, sample_owner_id, sample_resume
    ):
        db = AsyncMock()
        file_bytes = b"%PDF-1.4 dummy content"

        # Patch validation helpers so they pass silently
        with (
            patch("app.services.resume_service.FileValidationService.sanitize_filename", return_value="resume.pdf"),
            patch("app.services.resume_service.FileValidationService.validate_size", return_value=None),
            patch("app.services.resume_service.FileValidationService.validate_content", return_value="application/pdf"),
        ):
            mock_resume_repo.get_by_hash.return_value = None
            mock_storage.upload_file.return_value = "path/to/resume.pdf"

            # The db.add / commit / refresh path
            db.add = MagicMock()
            db.commit = AsyncMock()
            db.refresh = AsyncMock(side_effect=lambda obj: None)

            # We need the created object returned — patch the model constructor
            with patch("app.services.resume_service.UploadedResume", return_value=sample_resume):
                result = await resume_service.upload_resume(
                    db=db,
                    owner_id=sample_owner_id,
                    file_bytes=file_bytes,
                    original_filename="resume.pdf",
                )

            assert result == sample_resume
            mock_storage.upload_file.assert_called_once()

    @pytest.mark.asyncio
    async def test_duplicate_raises(
        self, resume_service, mock_resume_repo, sample_owner_id, sample_resume
    ):
        db = AsyncMock()
        file_bytes = b"%PDF-1.4 dummy"

        with (
            patch("app.services.resume_service.FileValidationService.sanitize_filename", return_value="resume.pdf"),
            patch("app.services.resume_service.FileValidationService.validate_size", return_value=None),
            patch("app.services.resume_service.FileValidationService.validate_content", return_value="application/pdf"),
        ):
            mock_resume_repo.get_by_hash.return_value = sample_resume  # duplicate found

            with pytest.raises(BadRequestException, match="already been uploaded"):
                await resume_service.upload_resume(
                    db=db,
                    owner_id=sample_owner_id,
                    file_bytes=file_bytes,
                    original_filename="resume.pdf",
                )


# ── get_resume ────────────────────────────────────────────────────────────────

class TestGetResume:
    @pytest.mark.asyncio
    async def test_not_found_raises(self, resume_service, mock_resume_repo, sample_owner_id):
        db = AsyncMock()
        mock_resume_repo.get_by_id_with_extraction.return_value = None
        with pytest.raises(NotFoundException):
            await resume_service.get_resume(
                db=db, resume_id=uuid.uuid4(), requester_id=sample_owner_id
            )

    @pytest.mark.asyncio
    async def test_wrong_owner_raises(self, resume_service, mock_resume_repo, sample_resume):
        db = AsyncMock()
        mock_resume_repo.get_by_id_with_extraction.return_value = sample_resume
        other_user = uuid.uuid4()
        with pytest.raises(ForbiddenException):
            await resume_service.get_resume(
                db=db, resume_id=sample_resume.id, requester_id=other_user, is_admin=False
            )

    @pytest.mark.asyncio
    async def test_admin_bypasses_ownership(
        self, resume_service, mock_resume_repo, sample_resume
    ):
        db = AsyncMock()
        mock_resume_repo.get_by_id_with_extraction.return_value = sample_resume
        result = await resume_service.get_resume(
            db=db,
            resume_id=sample_resume.id,
            requester_id=uuid.uuid4(),  # different user
            is_admin=True,
        )
        assert result == sample_resume


# ── get_signed_url ─────────────────────────────────────────────────────────────

class TestGetSignedUrl:
    def test_delegates_to_storage(self, resume_service, mock_storage):
        mock_storage.get_signed_url.return_value = "https://storage.example.com/signed"
        url = resume_service.get_signed_url("path/to/file.pdf", expires_in=1800)
        mock_storage.get_signed_url.assert_called_once_with("resumes", "path/to/file.pdf", 1800)
        assert url == "https://storage.example.com/signed"
