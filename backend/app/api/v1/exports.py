"""Exports API Router.

Exposes REST endpoints for downloading candidate evaluation reports as PDF, DOCX, JSON, or CSV files.
"""

import logging
import uuid
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import RoleChecker
from app.core.exceptions import NotFoundException, BadRequestException
from app.database.models.user import User, UserRole
from app.database.models.analysis import Analysis
from app.database.session import get_db_session
from app.services.export_engine import ExportEngineService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Exports"])


@router.get(
    "/exports/{analysis_id}",
    summary="Export candidate evaluation report file",
)
async def export_report(
    analysis_id: uuid.UUID,
    format: str = Query("json", description="Target download format: json | csv | pdf | docx"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(
        RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.CANDIDATE])
    ),
) -> Response:
    """Download evaluation report compiled to target file format bytes."""
    # 1. Fetch analysis
    analysis = await db.get(Analysis, analysis_id)
    if not analysis or not analysis.report_data:
        raise NotFoundException("Analysis report or completed report data not found.")

    # 2. Serialize
    fmt = format.lower()
    service = ExportEngineService()

    if fmt == "json":
        content = service.export_as_json(analysis.report_data)
        media_type = "application/json"
        filename = f"report_{analysis_id}.json"
    elif fmt == "csv":
        content = service.export_as_csv(analysis.report_data)
        media_type = "text/csv"
        filename = f"report_{analysis_id}.csv"
    elif fmt == "pdf":
        content = service.export_as_pdf(analysis.report_data)
        media_type = "application/pdf"
        filename = f"report_{analysis_id}.pdf"
    elif fmt == "docx":
        content = service.export_as_docx(analysis.report_data)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = f"report_{analysis_id}.docx"
    else:
        raise BadRequestException("Unsupported export download format.")

    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
