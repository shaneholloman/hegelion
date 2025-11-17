"""Structured logging utilities for Hegelion."""

from __future__ import annotations

import json
import logging
import os
import sys
from typing import Any, Dict, Optional

# Configure logging level from environment
LOG_LEVEL = os.getenv("HEGELION_LOG_LEVEL", "WARNING").upper()

# Create logger
logger = logging.getLogger("hegelion")
logger.setLevel(getattr(logging, LOG_LEVEL, logging.WARNING))

# JSON formatter for structured logs
class JSONFormatter(logging.Formatter):
    """Format log records as JSON for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields from record
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data)


# Setup handler if not already configured
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)


def log_phase(phase: str, **kwargs: Any) -> None:
    """Log a dialectical phase with structured data."""
    extra = {"extra_fields": {"phase": phase, **kwargs}}
    logger.info(f"Phase: {phase}", extra=extra)


def log_error(error_type: str, message: str, **kwargs: Any) -> None:
    """Log an error with structured data."""
    extra = {"extra_fields": {"error_type": error_type, **kwargs}}
    logger.error(message, extra=extra)


def log_metric(metric_name: str, value: Any, **kwargs: Any) -> None:
    """Log a metric with structured data."""
    extra = {"extra_fields": {"metric": metric_name, "value": value, **kwargs}}
    logger.debug(f"Metric: {metric_name}={value}", extra=extra)


__all__ = ["logger", "log_phase", "log_error", "log_metric"]
