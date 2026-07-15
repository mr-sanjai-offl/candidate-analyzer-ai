"""Custom exception classes and FastAPI exception handlers.

Implements a structured exception hierarchy as required by Architecture
Bible Section 7 (Custom exception classes) and Section 13 (production-grade
error handling). Every exception carries a message, HTTP status code, and
optional structured details for debugging.
"""

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.logging import get_logger

logger = get_logger(__name__)


class AppException(Exception):
    """Base exception for all application-specific errors.

    All custom exceptions inherit from this class to ensure
    consistent error response formatting and centralized logging.

    Attributes:
        message: Human-readable error description.
        status_code: HTTP status code to return to the client.
        details: Optional structured data providing additional context.
    """

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class DatabaseException(AppException):
    """Exception raised for database-related errors.

    Returned as HTTP 503 Service Unavailable, indicating the
    database is temporarily unreachable or a query failed.
    """

    def __init__(
        self,
        message: str = "A database error occurred",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, status_code=503, details=details)


class ValidationException(AppException):
    """Exception raised for business-level validation errors.

    Returned as HTTP 422 Unprocessable Entity. Distinct from
    Pydantic's built-in validation errors, this covers
    application-specific validation rules.
    """

    def __init__(
        self,
        message: str = "Validation failed",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, status_code=422, details=details)


class NotFoundException(AppException):
    """Exception raised when a requested resource does not exist.

    Returned as HTTP 404 Not Found.
    """

    def __init__(
        self,
        message: str = "Resource not found",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, status_code=404, details=details)


class UnauthorizedException(AppException):
    """Exception raised when authentication fails or is missing.

    Returned as HTTP 401 Unauthorized.
    """

    def __init__(
        self,
        message: str = "Could not validate credentials",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, status_code=401, details=details)


class ForbiddenException(AppException):
    """Exception raised when user lacks required role/permissions.

    Returned as HTTP 403 Forbidden.
    """

    def __init__(
        self,
        message: str = "Permission denied",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, status_code=403, details=details)


class BadRequestException(AppException):
    """Exception raised when a request is malformed or invalid.

    Returned as HTTP 400 Bad Request.
    """

    def __init__(
        self,
        message: str = "Bad request",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, status_code=400, details=details)


class InternalServerException(AppException):
    """Exception raised for unexpected internal failures.

    Returned as HTTP 500 Internal Server Error.
    """

    def __init__(
        self,
        message: str = "An internal server error occurred",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, status_code=500, details=details)


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers with the FastAPI application.

    Centralizes error response formatting so that all errors —
    both expected application exceptions and unexpected runtime
    errors — return a consistent JSON structure.

    Args:
        app: The FastAPI application instance to attach handlers to.
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request,
        exc: AppException,
    ) -> JSONResponse:
        """Handle application-specific exceptions with structured logging."""
        logger.error(
            "Application error: %s | status=%d | path=%s",
            exc.message,
            exc.status_code,
            request.url.path,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.message,
                "details": exc.details,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Handle unhandled exceptions with a generic error response.

        Logs the full traceback for debugging while returning a
        safe, non-leaking error message to the client.
        """
        logger.exception("Unhandled exception on %s: %s", request.url.path, exc)
        return JSONResponse(
            status_code=500,
            content={
                "error": "An internal server error occurred",
                "details": {},
            },
        )
