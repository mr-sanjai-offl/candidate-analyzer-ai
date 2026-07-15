"""Prompt Versioning and Templates database models.

Allows dynamic prompt storage, version history, and A/B testing configurations.
"""

from sqlalchemy import String, Integer, Float, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class PromptTemplate(Base):
    """Stores metadata and active configs for prompt templates."""

    __tablename__ = "prompt_templates"

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
        doc="Name identifying the prompt template type (e.g. recruiter_report).",
    )
    active_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        doc="The version number currently set as active.",
    )
    ab_testing_enabled: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        doc="Indicates if A/B testing is active for this template.",
    )
    ab_split_ratio: Mapped[float] = mapped_column(
        Float,
        default=0.5,
        nullable=False,
        doc="The traffic fraction directed to version A (0.0 to 1.0).",
    )


class PromptVersion(Base):
    """Stores individual prompt versions and content."""

    __tablename__ = "prompt_versions"

    template_name: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False,
        doc="The template name this version belongs to.",
    )
    version_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Sequential version number.",
    )
    system_prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="System instruction template text.",
    )
    user_prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="User instruction template text with variables.",
    )
