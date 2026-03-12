"""Pydantic models for API requests and responses."""

from typing import List, Optional
from pydantic import BaseModel, Field, validator


class AnalysisRequest(BaseModel):
    """Request model for resume analysis."""

    resume_text: str = Field(..., min_length=50, description="Resume content")
    job_description: str = Field(..., min_length=50, description="Job description")

    @validator("resume_text", "job_description")
    def validate_text_length(cls, v):
        if len(v.strip()) < 50:
            raise ValueError("Text must be at least 50 characters long")
        return v.strip()


class BulletSuggestion(BaseModel):
    """Model for individual bullet point suggestions."""

    original: str = Field(..., description="Original bullet point")
    improved: str = Field(..., description="Improved version")
    reason: str = Field(..., description="Explanation for improvement")


class AnalysisResponse(BaseModel):
    """Response model for resume analysis."""

    match_percentage: float = Field(..., ge=0, le=100)
    missing_keywords: List[str] = Field(default_factory=list)
    matched_keywords: List[str] = Field(default_factory=list)
    suggestions: List[BulletSuggestion] = Field(default_factory=list)
    overall_feedback: str = Field(..., description="Summary feedback")
    strengths: List[str] = Field(default_factory=list)
    areas_for_improvement: List[str] = Field(default_factory=list)
    processing_time: Optional[float] = Field(
        None, description="Analysis processing time in seconds"
    )


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    detail: Optional[str] = None
    status_code: int = 500
