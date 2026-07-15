"""API dependencies and authentication middleware.

Implements JWT verification, user context retrieval, and Role-Based
Access Control (RBAC) dependencies.
"""

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_token
from app.database.models.user import User, UserRole
from app.database.session import get_db_session
from app.services.auth.auth_service import AuthService

# Use OAuth2 bearer authorization token extraction.
# Set auto_error=False so we can handle raising custom UnauthorizedExceptions.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,
)


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """Retrieve and validate the currently authenticated user.

    Decodes the access token payload, checks account active status,
    and returns the User model from the database.

    Args:
        token: Bearer JWT token from the request header.
        db: Async database session.

    Returns:
        The authenticated User model instance.

    Raises:
        UnauthorizedException: If authentication fails, or token is invalid.
    """
    if not token:
        raise UnauthorizedException("Authentication credentials were not provided")

    settings = get_settings()

    # Decode and validate signature/expiration
    payload = decode_token(
        token,
        settings.JWT_SECRET_KEY,
        settings.JWT_ALGORITHM,
    )

    # Enforce access token usage only
    if payload.get("type") != "access":
        raise UnauthorizedException("Invalid token type")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException("Subject claim missing")

    # Retrieve user from the database
    user = await AuthService.get_user_by_id(db, user_id_str)
    if not user:
        raise UnauthorizedException("User not found")

    if not user.is_active:
        raise ForbiddenException("User account is inactive")

    return user


class RoleChecker:
    """Class-based dependency checker for Role-Based Access Control (RBAC)."""

    def __init__(self, allowed_roles: list[UserRole]) -> None:
        """Initialize RoleChecker with allowed user roles.

        Args:
            allowed_roles: List of UserRole enums permitted to access route.
        """
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        """Enforce role constraint on the current authenticated user.

        Args:
            current_user: User instance returned by get_current_user.

        Returns:
            The current User if allowed.

        Raises:
            ForbiddenException: If current user's role is not in allowed list.
        """
        if current_user.role not in self.allowed_roles:
            raise ForbiddenException(
                "You do not have the required permissions to perform this action",
            )
        return current_user
