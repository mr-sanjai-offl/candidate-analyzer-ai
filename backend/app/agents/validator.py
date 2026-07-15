"""Response Validator.

Ensures that LLM outputs conform to required structures and are valid JSON.
"""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class ResponseValidator:
    """Validates structural properties of generated LLM completions."""

    @staticmethod
    def validate_json(text: str, required_keys: list[str]) -> tuple[bool, Any]:
        """Verify if text is valid JSON and contains all required root keys.

        Returns (is_valid, parsed_dict_or_original_text).
        """
        cleaned = text.strip()
        # Strip markdown wrapper if present
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines[0].startswith("```json") or lines[0].startswith("```"):
                cleaned = "\n".join(lines[1:-1])

        try:
            parsed = json.loads(cleaned)
            if not isinstance(parsed, dict):
                return False, parsed
            
            missing = [k for k in required_keys if k not in parsed]
            if missing:
                logger.warning("JSON missing required keys: %s", missing)
                return False, parsed
            
            return True, parsed
        except Exception as e:
            logger.debug("Failed to parse response as JSON: %s", e)
            return False, text
