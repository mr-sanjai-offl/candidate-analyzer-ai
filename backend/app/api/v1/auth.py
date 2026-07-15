"""Authentication API router.

Exposes auth endpoints for registering, logging in, logging out,
rotating JWTs, and fetching current user context.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database.models.user import User
from app.database.session import get_db_session
from app.schemas.auth import (
    MessageResponse,
    TokenRefreshRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.services.auth.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Registers a new candidate, recruiter, or admin profile.",
)
async def register(
    payload: UserRegisterRequest,
    db: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    """Register a new user profile.

    Validates input schemas, asserts email uniqueness, and returns
    the created user details.
    """
    user = await AuthService.register_user(db, payload)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate credentials",
    description="Logs a user in and returns access and refresh JWTs.",
)
async def login(
    payload: UserLoginRequest,
    db: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    """Log in and generate JWT tokens.

    Authenticates user credentials, registers last login timestamp,
    and returns a token response.
    """
    user = await AuthService.authenticate_user(
        db,
        payload.email,
        payload.password,
    )
    return await AuthService.create_tokens_for_user(db, user)


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Invalidate session",
    description="Revokes a refresh token to complete session logout.",
)
async def logout(
    payload: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db_session),
) -> MessageResponse:
    """Invalidate a refresh token.

    Revokes the provided refresh token record.
    """
    await AuthService.revoke_refresh_token(db, payload.refresh_token)
    return MessageResponse(message="Successfully logged out")


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Rotate tokens",
    description="Rotates access and refresh tokens using a refresh token.",
)
async def refresh(
    payload: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    """Rotate JWT credentials.

    Validates refresh token, invalidates old token, and returns a new pair.
    """
    return await AuthService.refresh_tokens(db, payload.refresh_token)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Current authenticated user details",
    description="Returns detailed information about the currently authenticated user.",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Retrieve current user context.

    Requires a valid access token in request headers.
    """
    return UserResponse.model_validate(current_user)
