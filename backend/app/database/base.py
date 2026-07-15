"""SQLAlchemy declarative base with mandatory columns.

Every table must include ``id``, ``created_at``, ``updated_at``, and
``deleted_at`` as required by Architecture Bible Section 9:

    'Every table must have:
     id UUID PRIMARY KEY,
     created_at TIMESTAMPTZ,
     updated_at TIMESTAMPTZ,
     deleted_at TIMESTAMPTZ NULL (soft delete)'
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Abstract base class for all database models.

    Provides the four mandatory columns defined in Architecture Bible
    Section 9. All ORM models must inherit from this class to ensure
    schema consistency across the platform.

    Attributes:
        id: UUID primary key, auto-generated.
        created_at: Timestamp set by the database on row creation.
        updated_at: Timestamp updated by the database on row modification.
        deleted_at: Soft-delete timestamp. ``None`` means the row is active.
    """

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique identifier for the record.",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Timestamp when the record was created.",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Timestamp when the record was last updated.",
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        doc="Soft-delete timestamp. NULL means the record is active.",
    )
