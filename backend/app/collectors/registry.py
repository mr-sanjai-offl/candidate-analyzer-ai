"""Collector registry and factory.

Provides dynamic discovery and instantiation of collectors by platform name.
No collector should know about any other collector — the registry is the
single point of coordination.
"""

import logging
from typing import Any, Type

from app.collectors.base import BaseCollector, CollectorConfig
from app.database.models.enums import PlatformType

logger = logging.getLogger(__name__)


class CollectorRegistry:
    """Central registry mapping platform types to collector classes.

    Usage::

        registry = CollectorRegistry()
        registry.register(PlatformType.GITHUB, GitHubCollector)
        cls = registry.get(PlatformType.GITHUB)
    """

    def __init__(self) -> None:
        self._collectors: dict[PlatformType, Type[BaseCollector[Any, Any]]] = {}

    def register(
        self, platform: PlatformType, collector_cls: Type[BaseCollector[Any, Any]]
    ) -> None:
        """Register a collector class for a platform."""
        if platform in self._collectors:
            logger.warning(
                "Overwriting existing collector registration for %s", platform
            )
        self._collectors[platform] = collector_cls
        logger.info("Registered collector for platform: %s", platform)

    def get(self, platform: PlatformType) -> Type[BaseCollector[Any, Any]]:
        """Retrieve the collector class for a platform.

        Raises:
            KeyError: If no collector is registered for the platform.
        """
        if platform not in self._collectors:
            raise KeyError(f"No collector registered for platform: {platform}")
        return self._collectors[platform]

    def list_platforms(self) -> list[PlatformType]:
        """Return all registered platform types."""
        return list(self._collectors.keys())


class CollectorFactory:
    """Factory that creates configured collector instances from the registry."""

    def __init__(self, registry: CollectorRegistry) -> None:
        self._registry = registry

    def create(
        self, platform: PlatformType, config: CollectorConfig
    ) -> BaseCollector[Any, Any]:
        """Instantiate a collector for the given platform and config.

        Args:
            platform: The target platform.
            config: The collector configuration (URLs, tokens, timeouts).

        Returns:
            A fully configured collector instance ready for ``run()``.
        """
        collector_cls = self._registry.get(platform)
        return collector_cls(config)


# ── Global singleton registry ────────────────────────────────────────────────

_global_registry = CollectorRegistry()


def get_registry() -> CollectorRegistry:
    """Return the application-wide collector registry."""
    return _global_registry


def get_factory() -> CollectorFactory:
    """Return a factory backed by the global registry."""
    return CollectorFactory(_global_registry)
