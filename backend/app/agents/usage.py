"""Token Usage Tracker.

Tracks prompt and completion token counts across LLM requests.
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class TokenUsageTracker:
    """Singleton tracker for monitoring model token usage."""

    _instance = None

    def __new__(cls) -> "TokenUsageTracker":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.stats = {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "requests_count": 0,
            }
        return cls._instance

    def track(self, prompt_tokens: int, completion_tokens: int) -> None:
        """Accumulate token counts from a single LLM request execution."""
        self.stats["prompt_tokens"] += prompt_tokens
        self.stats["completion_tokens"] += completion_tokens
        self.stats["total_tokens"] += (prompt_tokens + completion_tokens)
        self.stats["requests_count"] += 1

        logger.debug(
            "Tracked LLM usage: prompt=%d, completion=%d | Global total=%d",
            prompt_tokens,
            completion_tokens,
            self.stats["total_tokens"],
        )

    def get_stats(self) -> Dict[str, int]:
        """Retrieve aggregated token usage metrics."""
        return self.stats

    def clear(self) -> None:
        """Reset stats tracking counters."""
        self.stats = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "requests_count": 0,
        }
