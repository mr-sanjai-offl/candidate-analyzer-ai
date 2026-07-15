"""User database model.

Mandates roles and attributes of individual system users according to
Architecture Bible Section 9.
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.refresh_token import RefreshToken


class UserRole(enum.StrEnum):
    """Enumeration of system user roles for RBAC.

    - ADMIN: Full system administration permissions.
    - RECRUITER: Search, parse, and analyze candidate portfolios.
    - CANDIDATE: Upload resumes and view personal dashboard evaluations.
    """

    ADMIN = "ADMIN"
    RECRUITER = "RECRUITER"
    CANDIDATE = "CANDIDATE"


class User(Base):
    """SQLAlchemy model for ApexGuidance system users.

    Provides core security parameters, audit trail timestamps,
    and profile status indicators.
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        doc="Unique login email address.",
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="BCrypt password hash.",
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="User's full display name.",
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", native_enum=True),
        nullable=False,
        default=UserRole.CANDIDATE,
        doc="Role-Based Access Control identifier.",
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Flag showing whether email address has been verified.",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Active flag. Setting to false blocks user authentication.",
    )
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        doc="Timestamp of the last successful authentication request.",
    )

    # Relationships
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
