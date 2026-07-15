"""Normalization Service.

Normalizes extracted data (dates, phones, URLs).
"""

import logging
import re

logger = logging.getLogger(__name__)

class NormalizationService:
    """Normalizes extracted entities."""

    @staticmethod
    def normalize_phone(phone: str) -> str:
        """Strip non-numeric characters from phone, leaving + for international."""
        if not phone:
            return ""
        normalized = re.sub(r'[^\d+]', '', phone)
        return normalized

    @staticmethod
    def normalize_email(email: str) -> str:
        """Lowercase email."""
        return email.lower().strip() if email else ""

    @staticmethod
    def deduplicate(items: list[str]) -> list[str]:
        """Remove duplicates while preserving order."""
        seen = set()
        result = []
        for item in items:
            cleaned = item.strip()
            if cleaned.lower() not in seen:
                seen.add(cleaned.lower())
                result.append(cleaned)
        return result
