"""Integration tests for the Resume Analyzer application."""

import pytest
import json
import os
from pathlib import Path
from typing import Dict, Any
from fastapi.testclient import TestClient


class TestEndToEndWorkflow:
    """Test complete end-to-end analysis workflows."""

    @pytest.mark.integration
    def test_complete_analysis_workflow(
        self, client: TestClient, sample_resume: str, sample_job_description: str
    ) -> None:
        """Test a complete analysis workflow from input to output."""
        # Step 1: Health check
        health_response = client.get("/health")
        assert health_response.status_code == 200
        assert health_response.json()["status"] == "healthy"

        # Step 2: Perform analysis
        analysis_response = client.post(
            "/analyze",
            json={
                "resume_text": sample_resume,
                "job_description": sample_job_description,
            },
        )

        assert analysis_response.status_code == 200
        analysis_data = analysis_response.json()

        # Step 3: Validate complete response structure
        required_fields = [
            "match_percentage",
            "matched_keywords",
            "missing_keywords",
            "suggestions",
            "strengths",
            "areas_for_improvement",
        ]

        for field in required_fields:
            assert field in analysis_data, f"Missing required field: {field}"

        # Step 4: Validate data quality
        assert 0 <= analysis_data["match_percentage"] <= 100
        assert isinstance(analysis_data["matched_keywords"], list)
        assert isinstance(analysis_data["missing_keywords"], list)
        assert isinstance(analysis_data["suggestions"], list)
        assert isinstance(analysis_data["strengths"], list)
        assert isinstance(analysis_data["areas_for_improvement"], list)

        # Step 5: Check that we got meaningful results
        total_keywords = len(analysis_data["matched_keywords"]) + len(
            analysis_data["missing_keywords"]
        )
        assert total_keywords > 0, "Analysis should identify at least some keywords"

        # Step 6: Verify log status is accessible
        log_response = client.get("/logs/status")
        assert log_response.status_code == 200

    @pytest.mark.integration
    def test_error_handling_workflow(self, client: TestClient) -> None:
        """Test error handling across the application."""
        # Test missing data
        response = client.post("/analyze", json={})
        assert response.status_code == 422  # Validation error

        # Test invalid data
        response = client.post(
            "/analyze", json={"resume_text": None, "job_description": None}
        )
        assert response.status_code == 422

        # Test malformed JSON (simulated by sending invalid field types)
        response = client.post(
            "/analyze",
            json={
                "resume_text": 123,  # Should be string
                "job_description": ["not", "a", "string"],  # Should be string
            },
        )
        assert response.status_code == 422

    @pytest.mark.integration
    def test_api_documentation_endpoints(self, client: TestClient) -> None:
        """Test that API documentation endpoints are accessible."""
        # Test OpenAPI schema
        docs_response = client.get("/docs")
        assert docs_response.status_code == 200

        # Test OpenAPI JSON
        openapi_response = client.get("/openapi.json")
        assert openapi_response.status_code == 200

        # Validate OpenAPI structure
        openapi_data = openapi_response.json()
        assert "openapi" in openapi_data
        assert "paths" in openapi_data
        assert "/analyze" in openapi_data["paths"]


class TestDataValidation:
    """Test data validation and sanitization."""

    @pytest.mark.integration
    def test_input_sanitization(self, client: TestClient) -> None:
        """Test that inputs are properly sanitized."""
        # Test with special characters
        response = client.post(
            "/analyze",
            json={
                "resume_text": 'John Doe <script>alert("test")</script> Engineer',
                "job_description": "Looking for engineer with & experience in < > technologies",
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Should process successfully and return valid structure
        assert "match_percentage" in data
        assert isinstance(data["match_percentage"], (int, float))

    @pytest.mark.integration
    def test_unicode_handling(self, client: TestClient) -> None:
        """Test proper handling of Unicode characters."""
        unicode_resume = """
        João Silva - Développeur Senior
        Résumé: Expérience en développement avec Python et JavaScript.
        Compétences: Machine Learning, Intelligence Artificielle
        """

        unicode_job = """
        Recherche: Développeur Senior
        Exigences: Expérience en Python, maîtrise de l'IA
        """

        response = client.post(
            "/analyze",
            json={"resume_text": unicode_resume, "job_description": unicode_job},
        )

        assert response.status_code == 200
        data = response.json()
        assert "match_percentage" in data

    @pytest.mark.integration
    def test_large_text_handling(self, client: TestClient) -> None:
        """Test handling of realistically large documents."""
        # Create a realistic large resume (3-4 pages)
        large_resume = f"""
        SENIOR SOFTWARE ENGINEER - JOHN DOE
        
        PROFESSIONAL SUMMARY
        {' '.join(['Experienced software engineer with expertise in full-stack development.'] * 20)}
        
        TECHNICAL SKILLS
        {' '.join(['Python, JavaScript, React, Node.js, AWS, Docker, Kubernetes.'] * 15)}
        
        PROFESSIONAL EXPERIENCE
        {' '.join(['Led development of scalable web applications using modern technologies.'] * 30)}
        
        EDUCATION AND CERTIFICATIONS
        {' '.join(['Master of Science in Computer Science, AWS Certified Solutions Architect.'] * 10)}
        """

        large_job_description = f"""
        SENIOR SOFTWARE ENGINEER POSITION
        
        ABOUT THE ROLE
        {' '.join(['We are seeking an experienced software engineer to join our team.'] * 25)}
        
        REQUIREMENTS
        {' '.join(['5+ years experience in Python, JavaScript, and cloud technologies.'] * 20)}
        
        RESPONSIBILITIES
        {' '.join(['Design and implement scalable software solutions.'] * 15)}
        """

        response = client.post(
            "/analyze",
            json={
                "resume_text": large_resume,
                "job_description": large_job_description,
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Should handle large documents and provide meaningful analysis
        assert "match_percentage" in data
        assert (
            data["match_percentage"] > 0
        )  # Should find some matches in this tech-focused content


class TestEnvironmentIntegration:
    """Test integration with environment and configuration."""

    @pytest.mark.integration
    def test_logging_integration(
        self, client: TestClient, sample_resume: str, sample_job_description: str
    ) -> None:
        """Test that logging is working during actual requests."""
        # Make a request that should generate logs
        response = client.post(
            "/analyze",
            json={
                "resume_text": sample_resume,
                "job_description": sample_job_description,
            },
        )

        assert response.status_code == 200

        # Check log status endpoint
        log_status_response = client.get("/logs/status")
        assert log_status_response.status_code == 200

        log_data = log_status_response.json()
        assert "log_directory" in log_data
        assert "files" in log_data

    @pytest.mark.integration
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"), reason="Requires OpenAI API key"
    )
    def test_external_api_integration(self, client: TestClient) -> None:
        """Test integration with external APIs (when available)."""
        # This test only runs if we have a real API key configured
        response = client.post(
            "/analyze",
            json={
                "resume_text": "Software Engineer with Python experience",
                "job_description": "Looking for Python developer",
            },
        )

        assert response.status_code == 200
        data = response.json()

        # With real API, should get more sophisticated analysis
        assert "match_percentage" in data
        assert len(data.get("suggestions", [])) > 0


class TestRealWorldScenarios:
    """Test realistic usage scenarios."""

    @pytest.mark.integration
    def test_career_transition_scenario(self, client: TestClient) -> None:
        """Test analysis for someone transitioning careers."""
        transition_resume = """
        MARKETING MANAGER - JANE SMITH
        
        EXPERIENCE:
        - 5 years marketing experience
        - Data analysis and reporting
        - Excel and SQL experience
        - Project management
        
        EDUCATION:
        - MBA in Marketing
        - Online courses in Python programming
        """

        data_job = """
        DATA ANALYST POSITION
        
        REQUIREMENTS:
        - Strong analytical skills
        - SQL and Python experience
        - Data visualization
        - Statistical analysis
        - Business intelligence
        """

        response = client.post(
            "/analyze",
            json={"resume_text": transition_resume, "job_description": data_job},
        )

        assert response.status_code == 200
        data = response.json()

        # Should provide meaningful analysis for career transition
        assert "match_percentage" in data
        assert len(data["suggestions"]) > 0  # Should have suggestions for improvement
        assert len(data["missing_keywords"]) > 0  # Should identify skill gaps

    @pytest.mark.integration
    def test_senior_role_scenario(self, client: TestClient) -> None:
        """Test analysis for senior-level positions."""
        senior_resume = """
        SENIOR SOFTWARE ARCHITECT - ALEX JOHNSON
        
        EXPERIENCE:
        - 10+ years software development
        - Team leadership and mentoring
        - System architecture and design
        - Microservices and cloud platforms
        - Python, Java, JavaScript expertise
        
        ACHIEVEMENTS:
        - Led teams of 15+ engineers
        - Designed scalable systems handling millions of requests
        - Implemented DevOps practices reducing deployment time by 80%
        """

        senior_job = """
        PRINCIPAL ENGINEER POSITION
        
        REQUIREMENTS:
        - 8+ years software development experience
        - Leadership and mentoring experience
        - Distributed systems expertise
        - Cloud architecture knowledge
        - Strong communication skills
        """

        response = client.post(
            "/analyze",
            json={"resume_text": senior_resume, "job_description": senior_job},
        )

        assert response.status_code == 200
        data = response.json()

        # Senior roles should show high match
        assert data["match_percentage"] > 50  # Should be a good match
        assert len(data["matched_keywords"]) > 5  # Should find multiple matches

    @pytest.mark.integration
    def test_entry_level_scenario(self, client: TestClient) -> None:
        """Test analysis for entry-level positions."""
        entry_resume = """
        COMPUTER SCIENCE GRADUATE - MIKE CHEN
        
        EDUCATION:
        - BS Computer Science, 2024
        - Relevant coursework: Data Structures, Algorithms, Web Development
        
        PROJECTS:
        - Built web application using React and Node.js
        - Machine learning project using Python and scikit-learn
        - Internship at tech startup
        
        SKILLS:
        - Python, JavaScript, HTML/CSS
        - Git version control
        - Problem solving and teamwork
        """

        entry_job = """
        JUNIOR SOFTWARE DEVELOPER
        
        REQUIREMENTS:
        - Recent CS graduate or equivalent
        - Knowledge of programming fundamentals
        - Experience with web technologies
        - Eager to learn and grow
        - Good communication skills
        """

        response = client.post(
            "/analyze", json={"resume_text": entry_resume, "job_description": entry_job}
        )

        assert response.status_code == 200
        data = response.json()

        # Entry level should still provide meaningful analysis
        assert "match_percentage" in data
        assert len(data["suggestions"]) > 0  # Should have growth suggestions
