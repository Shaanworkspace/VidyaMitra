"""Main FastAPI application for VidyaMitra Career Agent.

Copyright (c) 2026 VidyaMitra Career Agent
Licensed under the MIT License. See LICENSE file for details.
"""

from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time

from app.config import settings
from app.models import AnalysisRequest, AnalysisResponse, ErrorResponse
from app.chains.analyzer import ResumeAnalyzer
from app.logging_config import (
    setup_logging,
    log_request,
    log_analysis_request,
    get_log_status,
)

# Configure logging
loggers = setup_logging()
logger = loggers["app"]
access_logger = loggers["access"]
error_logger = loggers["error"]

# Initialize FastAPI app
app = FastAPI(
    title="VidyaMitra Career Agent API",
    description="AI-Powered Resume Evaluator, Trainer & Career Planner",
    version="1.0.0",
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with timing."""
    start_time = time.time()

    # Get client IP
    client_ip = request.client.host if request.client else "unknown"

    # Process request
    response = await call_next(request)

    # Calculate processing time
    processing_time = time.time() - start_time

    # Log request
    log_request(
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        processing_time=processing_time,
        client_ip=client_ip,
    )

    return response


# Configure CORS - hardcoded allowed origins
allowed_origins = [
    # Production Vercel frontends
    "https://vidya-mitra-beta.vercel.app",
    "https://vidyamitra.vercel.app",
    # Any future *.vercel.app preview deployments for this project
    "https://vidya-mitra.vercel.app",
    # Local development
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3002",
]
# Also include anything from env (CORS_ORIGINS) for flexibility
try:
    allowed_origins.extend(settings.cors_origins)
except Exception:
    pass

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzer
analyzer = ResumeAnalyzer()


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting VidyaMitra Career Agent API...")
    logger.info(f"Using model: {settings.model_name}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model": settings.model_name}


@app.get("/logs/status")
async def log_status():
    """Get logging status and file information."""
    return get_log_status()


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(request: AnalysisRequest):
    """Analyze resume against job description."""
    start_time = time.time()
    resume_len = len(request.resume_text)
    job_desc_len = len(request.job_description)

    try:
        logger.info(
            f"Starting resume analysis - Resume: {resume_len} chars, Job: {job_desc_len} chars"
        )

        # Perform analysis
        result = await analyzer.analyze(
            resume_text=request.resume_text, job_description=request.job_description
        )

        processing_time = time.time() - start_time

        # Log successful analysis
        log_analysis_request(
            resume_len=resume_len,
            job_desc_len=job_desc_len,
            processing_time=processing_time,
            success=True,
        )

        return result

    except Exception as e:
        processing_time = time.time() - start_time

        # Log failed analysis
        log_analysis_request(
            resume_len=resume_len,
            job_desc_len=job_desc_len,
            processing_time=processing_time,
            success=False,
            error=str(e),
        )

        error_logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    error_logger.error(
        f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc) if settings.api_host == "0.0.0.0" else None,
            status_code=500,
        ).dict(),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app", host=settings.api_host, port=settings.api_port, reload=True
    )
