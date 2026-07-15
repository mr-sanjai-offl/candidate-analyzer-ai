"""Project database model.

Stores details about software engineering projects associated with a candidate.
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.models.enums import ProjectType

if TYPE_CHECKING:
    from app.database.models.candidate_profile import CandidateProfile


class Project(Base):
    """A project worked on by the candidate."""

    __tablename__ = "projects"

    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        doc="The candidate profile this project belongs to.",
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Project name.",
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Detailed description of the project.",
    )
    project_type: Mapped[ProjectType] = mapped_column(
        Enum(ProjectType, name="project_type", native_enum=True),
        nullable=False,
        default=ProjectType.PERSONAL,
        doc="The type/context of the project.",
    )
    url: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        doc="URL to the live project or repository.",
    )

    # Relationships
    candidate_profile: Mapped["CandidateProfile"] = relationship(
        "CandidateProfile",
        back_populates="projects",
    )
