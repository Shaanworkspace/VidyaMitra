import pytest
import sys
import os
from typing import List, Generator

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_resume() -> str:
    """Sample resume text for testing."""
    return """
    John Doe
    Software Engineer
    john.doe@email.com | (555) 123-4567
    
    EXPERIENCE
    Senior Software Engineer - Tech Corp (2020-Present)
    - Developed scalable microservices using Python and FastAPI
    - Led team of 5 engineers in agile environment
    - Implemented CI/CD pipelines reducing deployment time by 60%
    
    Software Engineer - StartupXYZ (2018-2020)
    - Built RESTful APIs serving 100k+ daily requests
    - Optimized database queries improving performance by 40%
    - Mentored junior developers on best practices
    
    SKILLS
    Languages: Python, JavaScript, TypeScript, Go
    Frameworks: FastAPI, Flask, React, Node.js
    Databases: PostgreSQL, MongoDB, Redis
    Tools: Docker, Kubernetes, AWS, Git
    
    EDUCATION
    BS Computer Science - University of Tech (2018)
    """


@pytest.fixture
def sample_job_description() -> str:
    """Sample job description for testing."""
    return """
    Senior Software Engineer
    
    We are looking for an experienced Senior Software Engineer to join our team.
    
    Requirements:
    - 5+ years of experience in software development
    - Strong proficiency in Python and modern web frameworks (FastAPI, Flask)
    - Experience with microservices architecture and RESTful APIs
    - Knowledge of containerization (Docker, Kubernetes)
    - Experience with cloud platforms (AWS preferred)
    - Strong understanding of databases (PostgreSQL, MongoDB)
    - Experience with CI/CD pipelines and DevOps practices
    - Excellent problem-solving and communication skills
    - Bachelor's degree in Computer Science or related field
    
    Nice to have:
    - Experience with React and modern frontend development
    - Knowledge of Go programming language
    - Experience leading engineering teams
    - Open source contributions
    """


@pytest.fixture
def expected_analysis_fields() -> List[str]:
    """Expected fields in analysis response."""
    return [
        "match_percentage",
        "matched_keywords",
        "missing_keywords",
        "suggestions",
        "strengths",
        "areas_for_improvement",
    ]
