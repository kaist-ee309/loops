"""Structured logging configuration using loguru."""

import sys

from loguru import logger

from app.config import settings


def setup_logging():
    """Configure structured logging with loguru (stdout only)."""
    # Remove default handler
    logger.remove()

    if settings.debug:
        # Development: Human-readable format
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        logger.add(
            sys.stdout,
            format=log_format,
            level="DEBUG",
            colorize=True,
        )
    else:
        # Production: JSON format for Cloud Logging
        logger.add(
            sys.stdout,
            format="{message}",
            level="INFO",
            serialize=True,
        )

    logger.info("Logging configured", debug=settings.debug, app_name=settings.app_name)


# Export logger for use in other modules
__all__ = ["logger", "setup_logging"]
