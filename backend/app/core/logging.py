"""Structured JSON logging configuration.

Implements structured logging as required by Architecture Bible
Section 7 (Structured JSON logging) and Section 12 (Structured logging
in every deployment).

No ``print()`` statements are used anywhere in the application
(Forbidden rule, Architecture Section 7).
"""

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any, override

from app.core.config import Settings


class JSONFormatter(logging.Formatter):
    """Format log records as structured JSON objects.

    Produces machine-parseable log lines suitable for log aggregation
    systems (ELK, Datadog, CloudWatch). Each line is a self-contained
    JSON object containing timestamp, level, logger name, message,
    source location, and optional exception details.
    """

    @override
    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as a JSON string.

        Args:
            record: The log record to format.

        Returns:
            A single-line JSON string representing the log entry.
        """
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info and record.exc_info[1] is not None:
            log_data["exception"] = {
                "type": (
                    record.exc_info[0].__name__
                    if record.exc_info[0] is not None
                    else "Unknown"
                ),
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }

        return json.dumps(log_data, default=str)


def setup_logging(settings: Settings) -> None:
    """Configure structured JSON logging for the application.

    Called during application startup via the lifespan context manager.
    Replaces all existing handlers on the root logger with a single
    JSON-formatted console handler.

    Args:
        settings: Application settings containing ``LOG_LEVEL`` configuration.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL.upper())

    # Clear existing handlers to avoid duplicate output
    root_logger.handlers.clear()

    # Console handler with JSON formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(console_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DATABASE_ECHO else logging.WARNING
    )


def get_logger(name: str) -> logging.Logger:
    """Get a named logger instance.

    Args:
        name: Logger name, typically ``__name__`` of the calling module.

    Returns:
        A configured :class:`logging.Logger` instance.
    """
    return logging.getLogger(name)
