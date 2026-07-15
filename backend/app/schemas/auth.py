"""Authentication and User validation schemas.

Pydantic models for incoming registration/login payloads and outgoing JWTs
to satisfy Architecture Section 7.
"""

import re
import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.database.models.user import UserRole

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class UserRegisterRequest(BaseModel):
    """Payload for registering a new user."""

    email: str = Field(
        ...,
        description="Unique login email address.",
        examples=["candidate@apexguidance.ai"],
    )
    password: str = Field(
        ...,
        description="Password for authentication.",
        examples=["P@ssw0rd123!"],
    )
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="The user's full display name.",
        examples=["Jane Doe"],
    )
    role: UserRole = Field(
        default=UserRole.CANDIDATE,
        description="The desired user role (CANDIDATE, RECRUITER, ADMIN).",
        examples=[UserRole.CANDIDATE],
    )

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        """Verify the email matches generic email constraints."""
        v = v.strip().lower()
        if not EMAIL_REGEX.match(v):
            raise ValueError("Invalid email format")
        return v

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Enforce standard enterprise password complexity.

        - Must contain at least 8 characters.
        - Must contain at least one uppercase letter.
        - Must contain at least one lowercase letter.
        - Must contain at least one digit.
        - Must contain at least one special character.
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        special_chars = "!@#$%^&*()-_=+[]{}|;:',.<>?/`~"
        if not any(c in special_chars for c in v):
            raise ValueError("Password must contain at least one special character")
        return v


class UserLoginRequest(BaseModel):
    """Payload for authenticating existing users."""

    email: str = Field(
        ...,
        description="User email address.",
        examples=["candidate@apexguidance.ai"],
    )
    password: str = Field(
        ...,
        description="User password.",
        examples=["P@ssw0rd123!"],
    )

    @field_validator("email")
    @classmethod
    def clean_email(cls, v: str) -> str:
        """Strip and lowercase the email address."""
        return v.strip().lower()


class TokenResponse(BaseModel):
    """Response returned upon successful registration, login, or token refresh."""

    access_token: str = Field(
        ...,
        description="Signed JWT access token.",
    )
    refresh_token: str = Field(
        ...,
        description="Signed JWT refresh token.",
    )
    token_type: str = Field(
        default="bearer",
        description="Type of token (always 'bearer').",
    )


class TokenRefreshRequest(BaseModel):
    """Payload to refresh an access token using a refresh token."""

    refresh_token: str = Field(
        ...,
        description="JWT refresh token signature string.",
    )


class UserResponse(BaseModel):
    """Pydantic model representing user information returned to clients."""

    id: uuid.UUID = Field(
        ...,
        description="UUID primary key.",
    )
    email: str = Field(
        ...,
        description="Email address.",
    )
    full_name: str = Field(
        ...,
        description="Full display name.",
    )
    role: UserRole = Field(
        ...,
        description="User permissions role.",
    )
    is_verified: bool = Field(
        ...,
        description="True if email is verified.",
    )
    is_active: bool = Field(
        ...,
        description="True if account is active.",
    )
    last_login: datetime | None = Field(
        default=None,
        description="Last login timestamp.",
    )
    created_at: datetime = Field(
        ...,
        description="Account creation timestamp.",
    )
    updated_at: datetime = Field(
        ...,
        description="Account last updated timestamp.",
    )

    model_config = {
        "from_attributes": True,
    }


class MessageResponse(BaseModel):
    """Standard message response payload."""

    message: str = Field(
        ...,
        description="Summary explanation details.",
        examples=["Operation successful"],
    )
