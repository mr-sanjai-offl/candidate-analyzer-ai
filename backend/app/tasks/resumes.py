"""Celery tasks for resume processing pipeline."""

import logging
import uuid
import asyncio
from typing import Any

from app.core.celery_app import celery_app
from app.database.models.resume import ParsingState, UploadedResume, ResumeExtraction
from app.database.session import get_db_session_ctx
from app.services.parsers.resume_parser_service import ResumeParserService
from app.services.storage_service import StorageService
from app.tasks.base import RetryableTask

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, base=RetryableTask, name="app.tasks.resumes.process_resume")
def process_resume(self, resume_id: str) -> None:
    """End-to-end background pipeline for processing an uploaded resume.
    
    Since SQLAlchemy async doesn't play well with synchronous Celery workers,
    we run the async logic in an event loop.
    """
    asyncio.run(_async_process_resume(self, uuid.UUID(resume_id)))


async def _async_process_resume(task: Any, resume_id: uuid.UUID) -> None:
    """Async implementation of the resume processing pipeline."""
    task.log_progress(0, "Starting resume processing pipeline.")
    
    storage_service = StorageService()
    parser_service = ResumeParserService()

    async with get_db_session_ctx() as db:
        # 1. Fetch resume record
        resume = await db.get(UploadedResume, resume_id)
        if not resume:
            logger.error(f"Resume {resume_id} not found in DB.")
            return
            
        try:
            # 2. Virus Scan Hook (Mock)
            task.log_progress(10, "Validating and scanning file...")
            resume.parsing_status = ParsingState.VALIDATING
            await db.commit()
            
            # 3. Download from Storage
            task.log_progress(20, "Downloading from storage...")
            resume.parsing_status = ParsingState.PARSING
            await db.commit()
            
            # Use 'resumes' bucket
            file_bytes = storage_service.download_file("resumes", resume.storage_path)
            
            # 4. Parse & Extract (OCR happens here if needed)
            task.log_progress(40, "Parsing text and extracting entities...")
            resume.parsing_status = ParsingState.EXTRACTING
            await db.commit()
            
            raw_text, structured_data = parser_service.parse_and_extract(file_bytes, resume.mime_type)
            
            # 5. Normalize (Normally handled by ExtractionService, marked as state)
            task.log_progress(70, "Normalizing extracted data...")
            resume.parsing_status = ParsingState.NORMALIZING
            await db.commit()
            
            # 6. Save Extraction
            task.log_progress(90, "Saving structured data...")
            extraction = ResumeExtraction(
                resume_id=resume.id,
                raw_text=raw_text,
                structured_data=structured_data
            )
            db.add(extraction)
            
            resume.parsing_status = ParsingState.COMPLETED
            await db.commit()
            task.log_progress(100, "Resume processing complete.")
            logger.info(f"Successfully processed resume {resume_id}.")
            
        except Exception as e:
            logger.error(f"Pipeline failed for resume {resume_id}: {e}", exc_info=True)
            resume.parsing_status = ParsingState.FAILED
            await db.commit()
            raise e
