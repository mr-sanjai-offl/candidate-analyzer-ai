"""Notification Service.

Handles dispatch of system alerts and email recommendations for candidate report status.
"""

import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Mock notification manager logs transaction emails dispatch."""

    async def send_analysis_complete_email(self, email: str, candidate_name: str) -> bool:
        """Log analysis complete email alert transaction."""
        logger.info(
            "Sending Analysis Complete email to %s for candidate: %s",
            email,
            candidate_name,
        )
        return True

    async def send_weekly_recommendations_email(self, email: str) -> bool:
        """Log weekly platform learning recommendations alert transaction."""
        logger.info("Sending Weekly Recommendations digest email to %s", email)
        return True

    async def send_report_ready_email(self, email: str, report_url: str) -> bool:
        """Log report generated readiness email alert transaction."""
        logger.info("Sending Report Ready notification email to %s: Link: %s", email, report_url)
        return True

    async def send_export_ready_email(self, email: str, download_url: str) -> bool:
        """Log document exports completion alert transaction."""
        logger.info("Sending Export Ready download email to %s: Link: %s", email, download_url)
        return True
