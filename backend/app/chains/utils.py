"""Utility functions for resume analysis.

Copyright (c) 2026 VidyaMitra Career Agent
Licensed under the MIT License. See LICENSE file for details.
"""

import re
from typing import Dict, List, Any


def normalize_match_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize and clean match analysis results from various sources.

    Handles different response formats and ensures consistent structure.
    """
    if not result:
        return {"matched_keywords": [], "missing_keywords": [], "match_percentage": 0}

    # Ensure all expected fields exist
    normalized = {
        "matched_keywords": [],
        "missing_keywords": [],
        "match_percentage": 0,
        "strengths": [],
        "recommendations": [],
    }

    # Extract and normalize matched keywords
    matched_raw = result.get("matched_keywords", result.get("matches", []))
    if isinstance(matched_raw, str):
        # Handle comma-separated string
        matched_raw = [k.strip() for k in matched_raw.split(",") if k.strip()]
    normalized["matched_keywords"] = [str(k).strip() for k in matched_raw if k]

    # Extract and normalize missing keywords
    missing_raw = result.get("missing_keywords", result.get("gaps", []))
    if isinstance(missing_raw, str):
        missing_raw = [k.strip() for k in missing_raw.split(",") if k.strip()]
    normalized["missing_keywords"] = [str(k).strip() for k in missing_raw if k]

    # Extract match percentage
    percentage = result.get("match_percentage", result.get("percentage", 0))
    if isinstance(percentage, str):
        # Extract number from string like "75%" or "75"
        percentage_match = re.search(r"(\d+)", str(percentage))
        percentage = int(percentage_match.group(1)) if percentage_match else 0
    normalized["match_percentage"] = max(0, min(100, int(percentage or 0)))

    # Extract other fields
    normalized["strengths"] = result.get("strengths", [])
    normalized["recommendations"] = result.get("recommendations", [])

    return normalized


def extract_from_natural_language(
    text: str, resume_keywords: List[str], job_keywords: List[str]
) -> Dict[str, Any]:
    """
    Extract match information from natural language LLM responses.

    Handles cases where the LLM doesn't return structured JSON.
    """
    result = {
        "matched_keywords": [],
        "missing_keywords": [],
        "match_percentage": 0,
        "strengths": [],
        "recommendations": [],
    }

    def extract_list_items(section_text: str) -> List[str]:
        """Extract items from bulleted or numbered lists."""
        lines = section_text.split("\n")
        items = []
        for line in lines:
            line = line.strip()
            # Remove bullet points, numbers, and common list markers
            line = re.sub(r"^[-•*\d+\.)\s]+", "", line).strip()
            if line and len(line) > 2:  # Ignore very short items
                items.append(line)
        return items

    # Try to extract match percentage
    percentage_patterns = [
        r"match(?:ing)?\s*(?:score|percentage|rate)?:?\s*(\d+)%",
        r"(\d+)%\s*match",
        r"score:?\s*(\d+)",
        r"compatibility:?\s*(\d+)%",
    ]

    for pattern in percentage_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result["match_percentage"] = int(match.group(1))
            break

    # Extract matched keywords section
    matched_section = re.search(
        r"(?:matched|found|present|strong)(?:\s+keywords?)?:?\s*(.*?)(?=(?:missing|gaps|weak|recommendations|$))",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if matched_section:
        matched_text = matched_section.group(1)
        result["matched_keywords"] = extract_list_items(matched_text)

    # Extract missing keywords section
    missing_section = re.search(
        r"(?:missing|gaps?|lacking|absent|weak)(?:\s+keywords?)?:?\s*(.*?)(?=(?:recommendations|suggestions|strengths|$))",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if missing_section:
        missing_text = missing_section.group(1)
        result["missing_keywords"] = extract_list_items(missing_text)

    # If we couldn't extract structured info, fall back to keyword matching
    if not result["matched_keywords"] and not result["missing_keywords"]:
        text_lower = text.lower()
        for keyword in job_keywords:
            if keyword.lower() in text_lower:
                result["matched_keywords"].append(keyword)

        # Identify missing keywords
        for keyword in job_keywords:
            if keyword not in result["matched_keywords"]:
                result["missing_keywords"].append(keyword)

    return result


def apply_semantic_boost(
    result: Dict[str, Any], semantic_score: float
) -> Dict[str, Any]:
    """
    Apply semantic similarity boost to keyword-based match results.

    Increases match percentage based on semantic similarity even when
    exact keyword matches are limited.
    """
    original_percentage = result.get("match_percentage", 0)

    # Convert semantic score (0-1) to percentage boost
    semantic_boost = int(semantic_score * 30)  # Max 30% boost

    # Apply boost with diminishing returns
    if original_percentage < 50:
        boost_factor = 1.0  # Full boost for low scores
    elif original_percentage < 75:
        boost_factor = 0.7  # Reduced boost for medium scores
    else:
        boost_factor = 0.3  # Minimal boost for high scores

    final_boost = int(semantic_boost * boost_factor)
    new_percentage = min(100, original_percentage + final_boost)

    result["match_percentage"] = new_percentage
    result["semantic_score"] = semantic_score

    return result


def simple_keyword_match(
    resume_text: str,
    job_description: str,
    resume_keywords: List[str] = None,
    job_keywords: List[str] = None,
) -> Dict[str, Any]:
    """
    Perform simple keyword-based matching as fallback.

    Used when LLM analysis fails or as a baseline comparison.
    """
    # Basic keyword extraction if not provided
    if not resume_keywords:
        resume_keywords = extract_basic_keywords(resume_text)
    if not job_keywords:
        job_keywords = extract_basic_keywords(job_description)

    # Find matches (case-insensitive)
    resume_lower = [k.lower() for k in resume_keywords]
    job_lower = [k.lower() for k in job_keywords]

    matched = []
    missing = []

    for job_keyword in job_keywords:
        if job_keyword.lower() in resume_lower:
            matched.append(job_keyword)
        else:
            missing.append(job_keyword)

    # Calculate percentage
    total_keywords = len(job_keywords)
    match_count = len(matched)
    percentage = int((match_count / total_keywords * 100)) if total_keywords > 0 else 0

    return {
        "matched_keywords": matched,
        "missing_keywords": missing,
        "match_percentage": percentage,
        "strengths": [],
        "recommendations": [],
    }


def extract_basic_keywords(text: str) -> List[str]:
    """Extract basic keywords from text using simple patterns."""
    # Remove common stop words and extract meaningful terms
    stop_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "up",
        "about",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "between",
        "among",
        "throughout",
        "during",
        "above",
        "below",
    }

    # Extract words that are likely to be skills or technologies
    words = re.findall(r"\b[A-Za-z][A-Za-z0-9+#\-\.]*\b", text)
    keywords = []

    for word in words:
        word_lower = word.lower()
        if len(word) >= 3 and word_lower not in stop_words and not word_lower.isdigit():
            keywords.append(word)

    # Remove duplicates while preserving order
    seen = set()
    unique_keywords = []
    for keyword in keywords:
        if keyword.lower() not in seen:
            seen.add(keyword.lower())
            unique_keywords.append(keyword)

    return unique_keywords[:50]  # Limit to top 50 keywords


def extract_bullet_points(resume_text: str) -> List[str]:
    """Extract bullet points from resume text."""
    lines = resume_text.split("\n")
    bullets = []

    for line in lines:
        line = line.strip()
        # Look for bullet point patterns
        if (
            line.startswith("•")
            or line.startswith("-")
            or line.startswith("*")
            or re.match(r"^\d+\.", line)
        ):
            # Clean the bullet point
            clean_bullet = re.sub(r"^[-•*\d+\.)\s]+", "", line).strip()
            if len(clean_bullet) > 10:  # Only include substantial bullets
                bullets.append(clean_bullet)

    return bullets[:10]  # Limit to top 10 bullets


def generate_feedback(match_result: Dict[str, Any]) -> str:
    """Generate human-readable feedback based on match results."""
    percentage = match_result.get("match_percentage", 0)
    matched = match_result.get("matched_keywords", [])
    missing = match_result.get("missing_keywords", [])

    if percentage >= 80:
        feedback = (
            "Excellent match! Your resume aligns very well with the job requirements."
        )
    elif percentage >= 60:
        feedback = "Good match with room for improvement."
    elif percentage >= 40:
        feedback = "Moderate match. Consider adding more relevant keywords."
    else:
        feedback = "Limited match. Significant improvements needed to align with job requirements."

    if matched:
        feedback += f" Strong areas: {', '.join(matched[:5])}."

    if missing:
        feedback += f" Consider adding: {', '.join(missing[:5])}."

    return feedback
