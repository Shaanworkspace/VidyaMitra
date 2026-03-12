"""Main resume analyzer using LangChain.

Copyright (c) 2026 VidyaMitra Career Agent
Licensed under the MIT License. See LICENSE file for details.
"""

import json
import asyncio
import time
from typing import Dict, List, Any
import logging

from langchain_google_genai import ChatGoogleGenerativeAI

# Updated imports for modern LangChain
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from app.models import AnalysisResponse, BulletSuggestion
from app.chains.prompts import (
    KEYWORD_EXTRACTION_PROMPT,
    MATCH_ANALYSIS_PROMPT,
    BULLET_IMPROVEMENT_PROMPT,
)
from app.chains.utils import (
    normalize_match_result,
    extract_from_natural_language,
    apply_semantic_boost,
    simple_keyword_match,
    extract_bullet_points,
    generate_feedback,
)
from app.exceptions import (
    AnalysisError,
    ValidationError,
    APIError,
    ModelError,
    DataProcessingError,
    TimeoutError,
    RateLimitError,
)

logger = logging.getLogger(__name__)


class ResumeAnalyzer:
    """
    Main class for analyzing resumes against job descriptions.

    Advanced version using hybrid approach: LLM-based keyword extraction
    combined with FAISS vector similarity for semantic analysis. Includes
    fallback to simple keyword matching when advanced analysis fails.
    """

    def __init__(self):
        """Initialize the analyzer with LangChain components."""
        self.llm = ChatGoogleGenerativeAI(
            model=settings.model_name,
            temperature=settings.temperature,
            max_output_tokens=settings.max_tokens,
            google_api_key=settings.google_api_key,
            max_retries=settings.max_retries,
            timeout=settings.request_timeout,
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap
        )

        # Initialize modern LangChain chains using pipe syntax
        self.keyword_chain = KEYWORD_EXTRACTION_PROMPT | self.llm
        self.match_chain = MATCH_ANALYSIS_PROMPT | self.llm
        self.improvement_chain = BULLET_IMPROVEMENT_PROMPT | self.llm

    async def analyze(self, resume_text: str, job_description: str) -> AnalysisResponse:
        """Perform complete resume analysis."""
        start_time = time.time()

        # Input validation with custom exceptions
        if not resume_text or not resume_text.strip():
            raise ValidationError(
                "Resume text cannot be empty",
                field_name="resume_text",
                validation_type="required",
            )

        if not job_description or not job_description.strip():
            raise ValidationError(
                "Job description cannot be empty",
                field_name="job_description",
                validation_type="required",
            )

        if len(resume_text.strip()) < 50:
            raise ValidationError(
                "Resume text must be at least 50 characters long",
                field_name="resume_text",
                validation_type="min_length",
                min_length=50,
                actual_length=len(resume_text.strip()),
            )

        try:
            # Extract keywords from both texts and generate embeddings in parallel
            resume_keywords_task = self._extract_keywords(resume_text, "resume")
            jd_keywords_task = self._extract_keywords(
                job_description, "job description"
            )

            resume_keywords, jd_keywords = await asyncio.gather(
                resume_keywords_task, jd_keywords_task
            )
            semantic_score = 0.0

            # Perform hybrid match analysis (keywords + semantic)
            match_result = await self._analyze_match(
                resume_keywords,
                jd_keywords,
                resume_text,
                job_description,
                semantic_score,
            )

            # Extract bullet points and generate improvements
            bullet_points = extract_bullet_points(resume_text)
            suggestions = []

            if bullet_points and match_result.get("missing_keywords"):
                improvement_result = await self._improve_bullets(
                    bullet_points[:5],  # Limit to top 5 bullets
                    job_description,
                    match_result["missing_keywords"],
                )
                suggestions = improvement_result

            # Calculate processing time
            processing_time = time.time() - start_time

            # Build response
            return AnalysisResponse(
                match_percentage=match_result.get("match_percentage", 0),
                matched_keywords=match_result.get("matched_keywords", []),
                missing_keywords=match_result.get("missing_keywords", []),
                suggestions=suggestions,
                strengths=match_result.get("strengths", []),
                areas_for_improvement=match_result.get("improvements", []),
                overall_feedback=generate_feedback(match_result),
                processing_time=processing_time,
            )

        except ValidationError:
            # Re-raise validation errors as they are already properly typed
            raise
        except APIError:
            # Re-raise API errors as they are already properly typed
            raise
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}", exc_info=True)
            raise AnalysisError(
                f"Failed to complete resume analysis: {str(e)}",
                analysis_type="full_analysis",
                processing_stage="main_pipeline",
            )

    async def _extract_keywords(self, text: str, context: str) -> List[str]:
        """Extract keywords from text."""
        try:
            result = await self.keyword_chain.ainvoke(
                {"text": text, "context": context}
            )
            result = result.content  # Extract content from AIMessage
            keywords = [k.strip() for k in result.split(",") if k.strip()]
            return keywords[:30]  # Limit to 30 keywords
        except Exception as e:
            logger.warning(f"Keyword extraction failed for {context}, using fallback: {str(e)}")
            # Fallback: extract simple keywords from text
            words = set(text.lower().split())
            stop_words = {'the','a','an','is','are','was','were','be','been','being','have','has','had','do','does','did','will','would','shall','should','may','might','must','can','could','and','but','or','nor','not','so','yet','both','either','neither','each','every','all','any','few','more','most','other','some','such','no','only','same','than','too','very','just','because','as','until','while','of','at','by','for','with','about','against','between','through','during','before','after','above','below','to','from','up','down','in','out','on','off','over','under','again','further','then','once','here','there','when','where','why','how','what','which','who','whom','this','that','these','those','i','me','my','we','our','you','your','he','him','his','she','her','it','its','they','them','their'}
            keywords = [w for w in words if len(w) > 2 and w not in stop_words and w.isalpha()]
            return keywords[:30]

    async def _analyze_match(
        self,
        resume_keywords: List[str],
        job_keywords: List[str],
        resume_text: str,
        job_description: str,
        semantic_score: float = 0.0,
    ) -> Dict[str, Any]:
        """Analyze resume-job match using LLM with advanced three-tier parsing."""
        try:
            result = await self.match_chain.ainvoke(
                {
                    "resume_keywords": ", ".join(resume_keywords),
                    "job_keywords": ", ".join(job_keywords),
                    "resume_text": resume_text[:3000],  # Limit text length
                    "job_description": job_description[:3000],
                }
            )
            result = result.content  # Extract content from AIMessage

            # Three-tier response normalization system
            parsed_result = await self._parse_llm_response(
                result, resume_keywords, job_keywords, semantic_score
            )

            return parsed_result

        except Exception as e:
            logger.error(
                f"LLM match analysis failed: {str(e)}, using fallback matching"
            )
            return simple_keyword_match(
                resume_text, job_description, resume_keywords, job_keywords
            )

    async def _parse_llm_response(
        self,
        raw_response: str,
        resume_keywords: List[str],
        job_keywords: List[str],
        semantic_score: float,
    ) -> Dict[str, Any]:
        """Three-tier response parsing system for production reliability."""

        # Tier 1: Parse structured JSON response
        try:
            parsed_result = json.loads(raw_response)
            logger.info("Tier 1: Successfully parsed structured JSON response")
            normalized_result = normalize_match_result(parsed_result)
            # Apply semantic boost to LLM result if available
            if semantic_score > 0:
                normalized_result = apply_semantic_boost(
                    normalized_result, semantic_score
                )
            return normalized_result

        except json.JSONDecodeError:
            logger.warning("Tier 1 failed: JSON parsing error, trying text extraction")

        # Tier 2: Extract from natural language using regex patterns
        try:
            extracted_result = extract_from_natural_language(
                raw_response, resume_keywords, job_keywords
            )
            logger.info("Tier 2: Successfully extracted from natural language")
            if semantic_score > 0:
                extracted_result = apply_semantic_boost(
                    extracted_result, semantic_score
                )
            return extracted_result

        except Exception as e:
            logger.warning(f"Tier 2 failed: Text extraction error: {str(e)}")

        # Tier 3: Rule-based fallback with semantic enhancement
        logger.info("Tier 3: Using rule-based fallback matching")
        result = simple_keyword_match("", "", resume_keywords, job_keywords)
        return apply_semantic_boost(result, semantic_score)

    async def _improve_bullets(
        self,
        bullet_points: List[str],
        job_description: str,
        missing_keywords: List[str],
    ) -> List[BulletSuggestion]:
        """Generate improved bullet points."""
        try:
            result = await self.improvement_chain.ainvoke(
                {
                    "bullet_points": "\n".join(f"- {bp}" for bp in bullet_points),
                    "job_description": job_description[:2000],
                    "missing_keywords": ", ".join(missing_keywords[:10]),
                }
            )
            result = result.content  # Extract content from AIMessage

            # Parse JSON response
            improvements = json.loads(result)
            return [
                BulletSuggestion(**item)
                for item in improvements
                if all(k in item for k in ["original", "improved", "reason"])
            ]
        except Exception as e:
            logger.error(f"Bullet improvement error: {str(e)}")
            return []
