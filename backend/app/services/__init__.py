"""Services package — Business logic layer.

All business logic must live here, never in route handlers
(Architecture Bible Section 5).
"""

from app.services.auth.auth_service import AuthService

__all__ = ["AuthService"]
