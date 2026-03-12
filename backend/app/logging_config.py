"""Logging configuration for the VidyaMitra Career Agent application."""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Dict, Any

from app.config import settings


def setup_logging() -> Dict[str, logging.Logger]:
    """Configure application logging with file handlers and rotation."""

    # Create app-logs directory
    log_dir = Path("app-logs")
    log_dir.mkdir(exist_ok=True)

    # Configure formatters
    detailed_formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    simple_formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Configure handlers
    handlers = {
        "app_file": logging.handlers.RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        ),
        "error_file": logging.handlers.RotatingFileHandler(
            log_dir / "error.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        ),
        "access_file": logging.handlers.RotatingFileHandler(
            log_dir / "access.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        ),
        "console": logging.StreamHandler(),
    }

    # Set formatter for each handler
    handlers["app_file"].setFormatter(detailed_formatter)
    handlers["error_file"].setFormatter(detailed_formatter)
    handlers["access_file"].setFormatter(simple_formatter)
    handlers["console"].setFormatter(simple_formatter)

    # Set levels
    handlers["app_file"].setLevel(logging.INFO)
    handlers["error_file"].setLevel(logging.ERROR)
    handlers["access_file"].setLevel(logging.INFO)
    handlers["console"].setLevel(logging.INFO if settings.debug else logging.WARNING)

    # Configure loggers
    loggers = {}

    # Main application logger
    app_logger = logging.getLogger("resume_analyzer")
    app_logger.setLevel(logging.INFO)
    app_logger.addHandler(handlers["app_file"])
    app_logger.addHandler(handlers["error_file"])
    app_logger.addHandler(handlers["console"])
    loggers["app"] = app_logger

    # Access logger for HTTP requests
    access_logger = logging.getLogger("resume_analyzer.access")
    access_logger.setLevel(logging.INFO)
    access_logger.addHandler(handlers["access_file"])
    access_logger.addHandler(handlers["console"])
    loggers["access"] = access_logger

    # Error logger for exceptions
    error_logger = logging.getLogger("resume_analyzer.error")
    error_logger.setLevel(logging.ERROR)
    error_logger.addHandler(handlers["error_file"])
    error_logger.addHandler(handlers["console"])
    loggers["error"] = error_logger

    # Prevent duplicate logs
    for logger in loggers.values():
        logger.propagate = False

    return loggers


def log_request(
    method: str,
    path: str,
    status_code: int,
    processing_time: float,
    client_ip: str = None,
) -> None:
    """Log HTTP request details."""
    access_logger = logging.getLogger("resume_analyzer.access")

    message = f"{method} {path} - {status_code} - {processing_time:.3f}s"
    if client_ip:
        message += f" - {client_ip}"

    if status_code >= 400:
        access_logger.error(message)
    else:
        access_logger.info(message)


def log_analysis_request(
    resume_len: int,
    job_desc_len: int,
    processing_time: float,
    success: bool = True,
    error: str = None,
) -> None:
    """Log resume analysis request details."""
    app_logger = logging.getLogger("resume_analyzer")

    message = f"Analysis request - Resume: {resume_len} chars, Job: {job_desc_len} chars, Time: {processing_time:.3f}s"

    if success:
        app_logger.info(message + " - SUCCESS")
    else:
        app_logger.error(message + f" - FAILED: {error}")


def get_log_status() -> Dict[str, Any]:
    """Get current logging status and file sizes."""
    log_dir = Path("app-logs")
    status = {"log_directory": str(log_dir.absolute()), "files": {}}

    if log_dir.exists():
        for log_file in log_dir.glob("*.log"):
            status["files"][log_file.name] = {
                "size_bytes": log_file.stat().st_size,
                "size_mb": round(log_file.stat().st_size / (1024 * 1024), 2),
                "exists": True,
            }

    return status
