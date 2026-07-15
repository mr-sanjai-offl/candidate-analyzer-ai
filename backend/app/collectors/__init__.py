"""Collectors package — External platform data collection.

Discovers and registers all platforms collectors.
"""

from app.collectors.base import BaseCollector, CollectorConfig, CollectorContext, CollectorResult
from app.collectors.github.collector import GitHubCollector
from app.collectors.leetcode.collector import LeetCodeCollector
from app.collectors.codeforces.collector import CodeforcesCollector
from app.collectors.registry import get_registry
from app.database.models.enums import PlatformType

# Register concrete collectors into global registry
_registry = get_registry()
_registry.register(PlatformType.GITHUB, GitHubCollector)
_registry.register(PlatformType.LEETCODE, LeetCodeCollector)
_registry.register(PlatformType.CODEFORCES, CodeforcesCollector)

__all__ = [
    "BaseCollector",
    "CollectorConfig",
    "CollectorContext",
    "CollectorResult",
    "GitHubCollector",
    "LeetCodeCollector",
    "CodeforcesCollector",
]
