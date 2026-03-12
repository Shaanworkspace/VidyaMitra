import pytest
import json
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


class TestAnalysisEndpoint:
    """Test the core /analyze endpoint functionality."""

    @pytest.mark.analysis
    def test_analyze_endpoint_success(
        self,
        client: TestClient,
        sample_resume: str,
        sample_job_description: str,
        expected_analysis_fields: List[str],
    ) -> None:
        """Test successful analysis with valid input."""
        response = client.post(
            "/analyze",
            json={
                "resume_text": sample_resume,
                "job_description": sample_job_description,
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Verify core expected fields are present (excluding improved_bullets which doesn't exist)
        core_fields = [
            "match_percentage",
            "matched_keywords",
            "missing_keywords",
            "suggestions",
            "strengths",
            "overall_feedback",
            "areas_for_improvement",
        ]
        for field in core_fields:
            assert field in data, f"Missing field: {field}"

        # Verify data types and basic validation
        assert isinstance(data["match_percentage"], (int, float))
        assert 0 <= data["match_percentage"] <= 100
        assert isinstance(data["matched_keywords"], list)
        assert isinstance(data["missing_keywords"], list)
        assert isinstance(data["suggestions"], list)
        assert isinstance(data["strengths"], list)
        assert isinstance(data["overall_feedback"], str)
        assert isinstance(data["areas_for_improvement"], list)

    @pytest.mark.analysis
    def test_analyze_endpoint_missing_resume(
        self, client: TestClient, sample_job_description: str
    ) -> None:
        """Test analysis with missing resume text."""
        response = client.post(
            "/analyze", json={"job_description": sample_job_description}
        )

        assert response.status_code == 422  # FastAPI validation error

    @pytest.mark.analysis
    def test_analyze_endpoint_missing_job_description(
        self, client: TestClient, sample_resume: str
    ) -> None:
        """Test analysis with missing job description."""
        response = client.post("/analyze", json={"resume_text": sample_resume})

        assert response.status_code == 422  # FastAPI validation error

    @pytest.mark.analysis
    def test_analyze_endpoint_empty_strings(self, client: TestClient) -> None:
        """Test analysis with empty strings."""
        response = client.post(
            "/analyze", json={"resume_text": "", "job_description": ""}
        )

        # Should either reject (422) or handle gracefully (200)
        assert response.status_code in [200, 422]

        if response.status_code == 200:
            data = response.json()
            # If it processes, should still return valid structure
            assert "match_percentage" in data

    @pytest.mark.analysis
    def test_analyze_endpoint_short_text(self, client: TestClient) -> None:
        """Test analysis with minimal valid text (meets 50 char requirement)."""
        response = client.post(
            "/analyze",
            json={
                "resume_text": "John Doe, Software Engineer with Python and JavaScript experience in web development",
                "job_description": "Looking for Software Engineer with programming skills and development experience",
            },
        )

        # Should process minimal valid text that meets requirements
        assert response.status_code == 200
        data = response.json()
        assert "match_percentage" in data

    @pytest.mark.analysis
    def test_analyze_endpoint_realistic_match(
        self, client: TestClient, sample_resume: str, sample_job_description: str
    ) -> None:
        """Test that analysis produces realistic match percentages."""
        response = client.post(
            "/analyze",
            json={
                "resume_text": sample_resume,
                "job_description": sample_job_description,
            },
        )

        assert response.status_code == 200
        data = response.json()

        # For our sample data, should be a reasonable match (50-95%)
        assert 50 <= data["match_percentage"] <= 95

        # Should find some matching keywords
        assert len(data["matched_keywords"]) > 0

        # Should provide suggestions
        assert len(data["suggestions"]) > 0

    @pytest.mark.analysis
    @patch("app.chains.analyzer.LLMChain.arun")
    def test_analyze_endpoint_llm_failure_handling(
        self,
        mock_llm: MagicMock,
        client: TestClient,
        sample_resume: str,
        sample_job_description: str,
    ) -> None:
        """Test that system properly handles LLM service failures."""
        # Mock LLM chain to raise an exception
        mock_llm.side_effect = Exception("LLM service unavailable")

        response = client.post(
            "/analyze",
            json={
                "resume_text": sample_resume,
                "job_description": sample_job_description,
            },
        )

        # Should return 500 when critical LLM services fail
        assert response.status_code == 500
        data = response.json()

        # Should return error response with proper structure
        assert "detail" in data
        assert isinstance(data["detail"], str)

    @pytest.mark.analysis
    def test_health_endpoint(self, client: TestClient) -> None:
        """Test that health endpoint is working."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
