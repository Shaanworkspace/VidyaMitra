"""
Custom exception classes for VidyaMitra Career Agent.

This module provides specialized exception classes for different types of errors
that can occur during resume analysis processing.

Copyright (c) 2026 VidyaMitra Career Agent
Licensed under the MIT License. See LICENSE file for details.
"""

from typing import Optional, Dict, Any


class VidyaMitraError(Exception):
    """Base exception class for all VidyaMitra Career Agent errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


class AnalysisError(VidyaMitraError):
    """Raised when errors occur during resume analysis processing."""

    def __init__(
        self,
        message: str,
        analysis_type: Optional[str] = None,
        processing_stage: Optional[str] = None,
        **kwargs,
    ):
        details = {
            "analysis_type": analysis_type,
            "processing_stage": processing_stage,
            **kwargs,
        }
        super().__init__(message, details)


class ValidationError(VidyaMitraError):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        validation_type: Optional[str] = None,
        **kwargs,
    ):
        details = {
            "field_name": field_name,
            "validation_type": validation_type,
            **kwargs,
        }
        super().__init__(message, details)


class ConfigurationError(VidyaMitraError):
    """Raised when configuration issues are detected."""

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        config_file: Optional[str] = None,
        **kwargs,
    ):
        details = {"config_key": config_key, "config_file": config_file, **kwargs}
        super().__init__(message, details)


class APIError(VidyaMitraError):
    """Raised when external API calls fail."""

    def __init__(
        self,
        message: str,
        api_name: Optional[str] = None,
        status_code: Optional[int] = None,
        response: Optional[str] = None,
        **kwargs,
    ):
        details = {
            "api_name": api_name,
            "status_code": status_code,
            "response": response,
            **kwargs,
        }
        super().__init__(message, details)


class ModelError(VidyaMitraError):
    """Raised when machine learning model operations fail."""

    def __init__(
        self,
        message: str,
        model_name: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs,
    ):
        details = {"model_name": model_name, "operation": operation, **kwargs}
        super().__init__(message, details)


class DataProcessingError(VidyaMitraError):
    """Raised when data processing operations fail."""

    def __init__(
        self,
        message: str,
        data_type: Optional[str] = None,
        processing_step: Optional[str] = None,
        **kwargs,
    ):
        details = {"data_type": data_type, "processing_step": processing_step, **kwargs}
        super().__init__(message, details)


class TimeoutError(VidyaMitraError):
    """Raised when operations exceed their timeout limits."""

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        **kwargs,
    ):
        details = {"operation": operation, "timeout_seconds": timeout_seconds, **kwargs}
        super().__init__(message, details)


class RateLimitError(APIError):
    """Raised when API rate limits are exceeded."""

    def __init__(
        self,
        message: str = "API rate limit exceeded",
        retry_after: Optional[int] = None,
        **kwargs,
    ):
        details = {"retry_after": retry_after, **kwargs}
        super().__init__(message, api_name="openai", **details)


# Exception type mapping for easy error handling
EXCEPTION_MAP = {
    "analysis": AnalysisError,
    "validation": ValidationError,
    "configuration": ConfigurationError,
    "api": APIError,
    "model": ModelError,
    "data_processing": DataProcessingError,
    "timeout": TimeoutError,
    "rate_limit": RateLimitError,
}


def get_exception_class(error_type: str) -> type:
    """Get the appropriate exception class for a given error type."""
    return EXCEPTION_MAP.get(error_type, VidyaMitraError)


def raise_for_error(error_type: str, message: str, **kwargs) -> None:
    """Raise the appropriate exception for a given error type."""
    exception_class = get_exception_class(error_type)
    raise exception_class(message, **kwargs)
