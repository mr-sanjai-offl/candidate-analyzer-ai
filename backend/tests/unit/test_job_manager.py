"""Unit tests for the BackgroundJobService."""

import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.database.models.background_job import BackgroundJob
from app.database.models.enums import JobStatus
from app.services.job_manager import BackgroundJobService


@pytest.fixture
def mock_job_repo():
    repo = AsyncMock()
    return repo


@pytest.fixture
def job_service(mock_job_repo):
    return BackgroundJobService(job_repo=mock_job_repo)


@pytest.mark.asyncio
async def test_create_job(job_service, mock_job_repo):
    # Setup
    db = AsyncMock()
    mock_job = BackgroundJob(
        id=uuid.uuid4(),
        task_name="test_task",
        celery_task_id="task-123",
        status=JobStatus.PENDING,
    )
    mock_job_repo.create.return_value = mock_job

    # Execute
    job_id = await job_service.create_job(db, "test_task", "task-123")

    # Assert
    assert job_id == mock_job.id
    mock_job_repo.create.assert_called_once()
    call_kwargs = mock_job_repo.create.call_args.kwargs
    assert call_kwargs["obj_in"]["task_name"] == "test_task"
    assert call_kwargs["obj_in"]["celery_task_id"] == "task-123"
    assert call_kwargs["obj_in"]["status"] == JobStatus.PENDING


@pytest.mark.asyncio
async def test_update_status_running(job_service, mock_job_repo):
    # Setup
    db = AsyncMock()
    job_id = uuid.uuid4()
    mock_job = BackgroundJob(
        id=job_id,
        status=JobStatus.PENDING,
        started_at=None,
    )
    mock_job_repo.get_by_id.return_value = mock_job

    # Execute
    await job_service.update_status(db, job_id, JobStatus.RUNNING, worker_id="worker-1")

    # Assert
    mock_job_repo.update.assert_called_once()
    update_kwargs = mock_job_repo.update.call_args.kwargs
    update_data = update_kwargs["obj_in"]
    assert update_data["status"] == JobStatus.RUNNING
    assert update_data["worker_id"] == "worker-1"
    assert "started_at" in update_data
