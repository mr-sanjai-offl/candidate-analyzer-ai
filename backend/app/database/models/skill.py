"""Skill database model.

Stores global definitions for skills that can be extracted and evaluated.
"""

from sqlalchemy import Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.database.base import Base
from app.database.models.enums import SkillCategory

if TYPE_CHECKING:
    from app.database.models.candidate_skill import CandidateSkill


class Skill(Base):
    """A global skill definition."""

    __tablename__ = "skills"

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
        doc="Name of the skill (e.g., Python, React, PostgreSQL).",
    )
    category: Mapped[SkillCategory] = mapped_column(
        Enum(SkillCategory, name="skill_category", native_enum=True),
        nullable=False,
        default=SkillCategory.OTHER,
        doc="Broad category of the skill.",
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Optional description of the skill.",
    )

    # Relationships
    candidate_skills: Mapped[list["CandidateSkill"]] = relationship(
        "CandidateSkill",
        back_populates="skill",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
