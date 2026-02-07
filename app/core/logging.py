"""Structured logging configuration using structlog"""

import logging
import sys
import structlog
from app.config import settings


def setup_logging():
    """Configure structured logging for the application"""
    
    # Determine if we're in development or production
    is_dev = settings.environment == "development"
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if is_dev else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.log_level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )
    
    # Get logger
    return structlog.get_logger()


# Global logger instance
logger = setup_logging()
