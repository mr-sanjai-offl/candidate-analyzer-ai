"""Authentication service.

Encapsulates all registration, login, logout, and token rotation business logic
to keep API routes clean (Architecture Section 13).
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import (
    ForbiddenException,
    UnauthorizedException,
    ValidationException,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.database.models.refresh_token import RefreshToken
from app.database.models.user import User
from app.schemas.auth import TokenResponse, UserRegisterRequest


class AuthService:
    """Core business logic service for authenticating ApexGuidance users."""

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
        """Fetch a user by email address.

        Args:
            db: Async database session.
            email: User's unique login email.

        Returns:
            The User instance if found, or None.
        """
        stmt = select(User).where(User.email == email, User.deleted_at.is_(None))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID | str) -> User | None:
        """Fetch a user by primary key ID.

        Args:
            db: Async database session.
            user_id: User UUID.

        Returns:
            The User instance if found, or None.
        """
        if isinstance(user_id, str):
            try:
                user_id = uuid.UUID(user_id)
            except ValueError:
                return None

        stmt = select(User).where(User.id == user_id, User.deleted_at.is_(None))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def register_user(
        cls,
        db: AsyncSession,
        register_data: UserRegisterRequest,
    ) -> User:
        """Create a new system user profile.

        Validates email uniqueness and hashes passwords using BCrypt.

        Args:
            db: Async database session.
            register_data: Registration request payload.

        Returns:
            The created User instance.

        Raises:
            ValidationException: If email address is already in use.
        """
        existing_user = await cls.get_user_by_email(db, register_data.email)
        if existing_user:
            raise ValidationException(
                message="Email address already registered",
                details={"email": "Email already in use"},
            )

        hashed = hash_password(register_data.password)

        new_user = User(
            email=register_data.email,
            password_hash=hashed,
            full_name=register_data.full_name,
            role=register_data.role,
            is_active=True,
            is_verified=False,
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        return new_user

    @classmethod
    async def authenticate_user(
        cls,
        db: AsyncSession,
        email: str,
        password: str,
    ) -> User:
        """Verify user credentials.

        Updates last login timestamp upon successful verification.

        Args:
            db: Async database session.
            email: Login email.
            password: Plaintext password.

        Returns:
            The authenticated User instance.

        Raises:
            UnauthorizedException: If email/password pair is invalid.
            ForbiddenException: If the user account is disabled/inactive.
        """
        user = await cls.get_user_by_email(db, email)
        if not user:
            raise UnauthorizedException("Invalid email or password")

        if not verify_password(password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise ForbiddenException("User account is inactive")

        # Update last login timestamp
        user.last_login = datetime.now(UTC)
        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def create_tokens_for_user(
        db: AsyncSession,
        user: User,
    ) -> TokenResponse:
        """Generate access and refresh tokens for a user.

        Persists the refresh token record in the database.

        Args:
            db: Async database session.
            user: User database model.

        Returns:
            A TokenResponse carrying access and refresh tokens.
        """
        settings = get_settings()

        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)

        # Retrieve expiration from token
        decoded = decode_token(
            refresh_token,
            settings.JWT_SECRET_KEY,
            settings.JWT_ALGORITHM,
        )
        expires_at = datetime.fromtimestamp(decoded["exp"], tz=UTC)

        # Store refresh token record
        token_record = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=expires_at,
            is_revoked=False,
        )

        db.add(token_record)
        await db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    @classmethod
    async def refresh_tokens(
        cls,
        db: AsyncSession,
        refresh_token_str: str,
    ) -> TokenResponse:
        """Perform Refresh Token Rotation (RTR).

        Decodes the refresh token. If a token is reused (is_revoked=True),
        compromise is detected. All active tokens for the user are revoked
        for security. If valid, rotates and returns a new token pair.

        Args:
            db: Async database session.
            refresh_token_str: The client-provided refresh token.

        Returns:
            A TokenResponse with new access/refresh tokens.

        Raises:
            UnauthorizedException: If token is invalid, expired, or reused.
        """
        settings = get_settings()

        # 1. Decode & validate JWT signature/claims
        payload = decode_token(
            refresh_token_str,
            settings.JWT_SECRET_KEY,
            settings.JWT_ALGORITHM,
        )

        # Ensure the token type is refresh
        if payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid token type")

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise UnauthorizedException("Invalid token claims")

        user_id = uuid.UUID(user_id_str)

        # 2. Query database record for this token
        stmt = select(RefreshToken).where(RefreshToken.token == refresh_token_str)
        result = await db.execute(stmt)
        token_record = result.scalar_one_or_none()

        if not token_record:
            raise UnauthorizedException("Invalid refresh token")

        # 3. Handle Token Compromise / Replay Attack (is_revoked=True)
        if token_record.is_revoked:
            # Security breach! Revoke ALL refresh tokens for this user
            revoke_stmt = (
                update(RefreshToken)
                .where(RefreshToken.user_id == user_id)
                .values(is_revoked=True, updated_at=datetime.now(UTC))
            )
            await db.execute(revoke_stmt)
            await db.commit()
            raise UnauthorizedException(
                "Security breach detected. Please authenticate again.",
            )

        # 4. Check database expiration
        now = datetime.now(UTC)
        if token_record.expires_at < now:
            raise UnauthorizedException("Refresh token has expired")

        # 5. Check user still exists and is active
        user = await cls.get_user_by_id(db, user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("User account is inactive or not found")

        # 6. Revoke current refresh token (rotation)
        token_record.is_revoked = True
        token_record.updated_at = now
        db.add(token_record)

        # 7. Generate a brand new pair and store new refresh token
        new_access_token = create_access_token(subject=user.id)
        new_refresh_token = create_refresh_token(subject=user.id)

        new_decoded = decode_token(
            new_refresh_token,
            settings.JWT_SECRET_KEY,
            settings.JWT_ALGORITHM,
        )
        new_expires_at = datetime.fromtimestamp(new_decoded["exp"], tz=UTC)

        new_token_record = RefreshToken(
            user_id=user.id,
            token=new_refresh_token,
            expires_at=new_expires_at,
            is_revoked=False,
        )

        db.add(new_token_record)
        await db.commit()

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
        )

    @staticmethod
    async def revoke_refresh_token(db: AsyncSession, refresh_token_str: str) -> None:
        """Revoke a refresh token on user logout.

        Args:
            db: Async database session.
            refresh_token_str: The refresh token to invalidate.
        """
        stmt = select(RefreshToken).where(RefreshToken.token == refresh_token_str)
        result = await db.execute(stmt)
        token_record = result.scalar_one_or_none()

        if token_record and not token_record.is_revoked:
            token_record.is_revoked = True
            token_record.updated_at = datetime.now(UTC)
            db.add(token_record)
            await db.commit()
