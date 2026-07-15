"""Skill and Technology Alias mapping models.

Provides standardization lookups during extraction to normalize technology names.
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class SkillAlias(Base):
    """Maps skill variants to standardized skill names."""

    __tablename__ = "skill_aliases"

    alias: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        doc="Non-standard alias variant.",
    )
    standard_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="The standardized name to map to.",
    )


class TechnologyAlias(Base):
    """Maps technology variants to standardized framework/tool names."""

    __tablename__ = "technology_aliases"

    alias: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        doc="Non-standard technology variant.",
    )
    standard_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="The standardized name to map to.",
    )
