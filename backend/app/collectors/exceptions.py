"""Collector exception hierarchy.

All collector-specific errors inherit from CollectorException,
which itself inherits from the application's AppException.
"""

from typing import Any

from app.core.exceptions import AppException


class CollectorException(AppException):
    """Base exception for all collector operations."""

    def __init__(
        self,
        message: str = "Collector operation failed",
        status_code: int = 502,
        details: dict[str, Any] | None = None,
        platform: str | None = None,
    ) -> None:
        if platform:
            details = details or {}
            details["platform"] = platform
        super().__init__(message=message, status_code=status_code, details=details)
        self.platform = platform


class CollectorRateLimitException(CollectorException):
    """Raised when an external API returns a rate-limit response (HTTP 429)."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int | None = None,
        platform: str | None = None,
    ) -> None:
        details: dict[str, Any] = {}
        if retry_after is not None:
            details["retry_after_seconds"] = retry_after
        super().__init__(
            message=message, status_code=429, details=details, platform=platform
        )
        self.retry_after = retry_after


class CollectorTimeoutException(CollectorException):
    """Raised when an external API request times out."""

    def __init__(
        self,
        message: str = "External API request timed out",
        platform: str | None = None,
    ) -> None:
        super().__init__(message=message, status_code=504, details=None, platform=platform)


class CollectorParsingException(CollectorException):
    """Raised when the collected payload cannot be parsed or normalized."""

    def __init__(
        self,
        message: str = "Failed to parse platform response",
        platform: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, status_code=502, details=details, platform=platform)


class CollectorAuthenticationException(CollectorException):
    """Raised when API authentication fails (invalid token, expired key)."""

    def __init__(
        self,
        message: str = "Platform API authentication failed",
        platform: str | None = None,
    ) -> None:
        super().__init__(message=message, status_code=401, details=None, platform=platform)


class CollectorNotFoundException(CollectorException):
    """Raised when the requested user/profile is not found on the platform."""

    def __init__(
        self,
        message: str = "Profile not found on platform",
        platform: str | None = None,
        username: str | None = None,
    ) -> None:
        details: dict[str, Any] = {}
        if username:
            details["username"] = username
        super().__init__(message=message, status_code=404, details=details, platform=platform)
