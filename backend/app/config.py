"""Configuration settings for the VidyaMitra Career Agent API.

Copyright (c) 2026 VidyaMitra Career Agent
Licensed under the MIT License. See LICENSE file for details.
"""

import os
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import validator, Field
from dotenv import load_dotenv

load_dotenv()


class APISettings(BaseSettings):
    """API and security configuration settings."""

    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="Host to bind the API server")
    api_port: int = Field(
        default=8000, ge=1024, le=65535, description="Port for the API server"
    )
    frontend_url: str = Field(
        default="http://localhost:3000", description="Frontend application URL for CORS"
    )
    frontend_url_alt: Optional[str] = Field(
        default=None, description="Alternative frontend URL for CORS"
    )
    debug: bool = Field(default=False, description="Enable debug mode")
    environment: str = Field(
        default="development", description="Environment mode (development/production)"
    )

    # Security Configuration
    cors_origins: List[str] = Field(
        default=["http://localhost:3000"], description="Allowed CORS origins"
    )
    api_key_header: str = Field(
        default="X-API-Key", description="Header name for API key authentication"
    )
    rate_limit_requests: int = Field(
        default=100, description="Rate limit requests per minute"
    )
    max_request_size: int = Field(
        default=1024 * 1024, description="Maximum request size in bytes"
    )

    @validator("environment")
    def validate_environment(cls, v):
        """Validate environment setting."""
        valid_environments = ["development", "testing", "staging", "production"]
        if v not in valid_environments:
            raise ValueError(f"Environment must be one of: {valid_environments}")
        return v

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"


class LLMSettings(BaseSettings):
    """LLM and AI service configuration settings."""

    # Google Gemini Configuration (free tier)
    google_api_key: str = Field(description="Google Gemini API key for LLM services")
    model_name: str = Field(
        default="gemini-2.0-flash", description="Google Gemini model to use for analysis"
    )
    embedding_model: str = Field(
        default="text-embedding-ada-002", description="Embedding model (unused with Gemini)"
    )
    # Legacy OpenAI key (optional, kept for compatibility)
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key (optional)")
    max_tokens: int = Field(
        default=2000, ge=100, le=4000, description="Maximum tokens per API call"
    )
    temperature: float = Field(
        default=0.3, ge=0.0, le=1.0, description="Model temperature for consistency"
    )
    request_timeout: int = Field(
        default=30, ge=5, le=120, description="API request timeout in seconds"
    )
    max_retries: int = Field(
        default=0, ge=0, le=5, description="Maximum number of API retries"
    )

    # LangChain Configuration
    langchain_tracing_v2: bool = Field(
        default=False, description="Enable LangSmith tracing"
    )
    langchain_api_key: Optional[str] = Field(
        default=None, description="LangSmith API key for tracing"
    )
    langchain_project: str = Field(
        default="resume-analyzer", description="LangSmith project name"
    )
    langchain_endpoint: str = Field(
        default="https://api.smith.langchain.com", description="LangSmith endpoint URL"
    )

    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration as a dictionary."""
        return {
            "api_key": self.google_api_key,
            "model": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "timeout": self.request_timeout,
            "max_retries": self.max_retries,
        }

    def get_langchain_config(self) -> Dict[str, Any]:
        """Get LangChain configuration as a dictionary."""
        return {
            "tracing_v2": self.langchain_tracing_v2,
            "api_key": self.langchain_api_key,
            "project": self.langchain_project,
            "endpoint": self.langchain_endpoint,
        }


class AnalysisSettings(BaseSettings):
    """Analysis and performance configuration settings."""

    # Analysis Configuration
    min_match_threshold: float = Field(
        default=0.3, ge=0.0, le=1.0, description="Minimum keyword match threshold"
    )
    max_suggestions: int = Field(
        default=5, ge=1, le=20, description="Maximum number of suggestions to generate"
    )
    chunk_size: int = Field(
        default=1000, ge=100, le=2000, description="Text chunk size for processing"
    )
    chunk_overlap: int = Field(
        default=200, ge=0, le=500, description="Overlap between text chunks"
    )
    max_keywords: int = Field(
        default=50, ge=10, le=100, description="Maximum keywords to extract"
    )

    # Performance Configuration
    async_concurrency: int = Field(
        default=10, ge=1, le=50, description="Maximum concurrent async operations"
    )
    cache_ttl: int = Field(
        default=3600, ge=0, description="Cache TTL in seconds (0 to disable)"
    )
    enable_caching: bool = Field(default=True, description="Enable response caching")
    response_compression: bool = Field(
        default=True, description="Enable response compression"
    )

    # Business Logic Configuration
    supported_languages: List[str] = Field(
        default=["en"], description="Supported languages for analysis"
    )
    supported_file_types: List[str] = Field(
        default=["txt", "pdf", "docx"], description="Supported file types"
    )
    max_file_size: int = Field(
        default=5 * 1024 * 1024, description="Maximum file upload size in bytes"
    )
    analysis_timeout: int = Field(
        default=60, ge=10, le=300, description="Analysis timeout in seconds"
    )

    def get_analysis_config(self) -> Dict[str, Any]:
        """Get analysis configuration as a dictionary."""
        return {
            "min_match_threshold": self.min_match_threshold,
            "max_suggestions": self.max_suggestions,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "max_keywords": self.max_keywords,
            "timeout": self.analysis_timeout,
        }


class MonitoringSettings(BaseSettings):
    """Logging and monitoring configuration settings."""

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string",
    )
    log_max_size: int = Field(
        default=10 * 1024 * 1024, description="Maximum log file size in bytes"
    )
    log_backup_count: int = Field(
        default=5, ge=1, le=20, description="Number of log backups to keep"
    )
    enable_access_logging: bool = Field(
        default=True, description="Enable HTTP access logging"
    )

    # Monitoring Configuration
    enable_metrics: bool = Field(default=True, description="Enable Prometheus metrics")
    metrics_port: int = Field(
        default=8001, ge=1024, le=65535, description="Port for metrics endpoint"
    )
    health_check_interval: int = Field(
        default=30, ge=5, le=300, description="Health check interval in seconds"
    )
    performance_monitoring: bool = Field(
        default=True, description="Enable performance monitoring"
    )

    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level setting."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()


class StorageSettings(BaseSettings):
    """Storage and feature flag configuration settings."""

    # Database/Storage Configuration
    database_url: Optional[str] = Field(
        default=None, description="Database connection URL"
    )
    redis_url: Optional[str] = Field(
        default="redis://localhost:6379/0", description="Redis connection URL"
    )
    storage_backend: str = Field(
        default="local", description="Storage backend (local/s3/gcs)"
    )
    upload_directory: str = Field(
        default="uploads", description="Directory for file uploads"
    )

    # Feature Flags
    enable_experimental_features: bool = Field(
        default=False, description="Enable experimental features"
    )
    enable_fallback_analysis: bool = Field(
        default=True, description="Enable fallback analysis when LLM fails"
    )
    enable_semantic_search: bool = Field(
        default=True, description="Enable semantic similarity search"
    )
    enable_batch_processing: bool = Field(
        default=False, description="Enable batch analysis processing"
    )

    @validator("storage_backend")
    def validate_storage_backend(cls, v):
        """Validate storage backend setting."""
        valid_backends = ["local", "s3", "gcs", "azure"]
        if v not in valid_backends:
            raise ValueError(f"Storage backend must be one of: {valid_backends}")
        return v


class Settings(
    APISettings, LLMSettings, AnalysisSettings, MonitoringSettings, StorageSettings
):
    """Main application settings inheriting from all configuration categories."""

    def setup_environment_logging(self) -> None:
        """Setup environment-specific logging configuration."""
        if self.is_production():
            # Production: More restrictive logging
            logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
            logging.getLogger("urllib3").setLevel(logging.WARNING)
        else:
            # Development: More verbose logging
            logging.getLogger("uvicorn.access").setLevel(logging.INFO)

    class Config:
        env_file = ".env"
        case_sensitive = False
        validate_assignment = True
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()

# Setup environment-specific configuration
settings.setup_environment_logging()
