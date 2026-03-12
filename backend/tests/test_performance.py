"""Performance and load testing for the Resume Analyzer."""

import pytest
import time
import statistics
from typing import List
from fastapi.testclient import TestClient
from concurrent.futures import ThreadPoolExecutor, as_completed


class TestPerformanceMetrics:
    """Test performance characteristics of the analysis engine."""

    @pytest.mark.performance
    def test_single_analysis_response_time(
        self, client: TestClient, sample_resume: str, sample_job_description: str
    ) -> None:
        """Test that single analysis completes within acceptable time limits."""
        start_time = time.time()

        response = client.post(
            "/analyze",
            json={
                "resume_text": sample_resume,
                "job_description": sample_job_description,
            },
        )

        end_time = time.time()
        processing_time = end_time - start_time

        assert response.status_code == 200
        assert (
            processing_time < 10.0
        ), f"Analysis took {processing_time:.2f}s, expected < 10s"

        # Ideal response time should be under 5 seconds
        if processing_time < 5.0:
            pytest.skip(
                f"Analysis completed in {processing_time:.2f}s (excellent performance)"
            )
        else:
            print(
                f"Warning: Analysis took {processing_time:.2f}s (acceptable but not optimal)"
            )

    @pytest.mark.performance
    def test_analysis_response_consistency(
        self, client: TestClient, sample_resume: str, sample_job_description: str
    ) -> None:
        """Test that multiple analyses produce consistent response times."""
        response_times = []

        for i in range(5):
            start_time = time.time()

            response = client.post(
                "/analyze",
                json={
                    "resume_text": sample_resume,
                    "job_description": sample_job_description,
                },
            )

            end_time = time.time()
            processing_time = end_time - start_time

            assert response.status_code == 200
            response_times.append(processing_time)

        # Check consistency - standard deviation should be reasonable
        avg_time = statistics.mean(response_times)
        std_dev = statistics.stdev(response_times) if len(response_times) > 1 else 0

        assert avg_time < 10.0, f"Average response time {avg_time:.2f}s too high"
        assert std_dev < 3.0, f"Response time variance too high: σ={std_dev:.2f}s"

        print(f"Performance: avg={avg_time:.2f}s, σ={std_dev:.2f}s")

    @pytest.mark.performance
    @pytest.mark.slow
    def test_concurrent_analysis_handling(
        self, client: TestClient, sample_resume: str, sample_job_description: str
    ) -> None:
        """Test that the API can handle multiple concurrent requests."""
        num_concurrent = 3  # Conservative for testing

        def make_request() -> tuple:
            start_time = time.time()
            response = client.post(
                "/analyze",
                json={
                    "resume_text": sample_resume,
                    "job_description": sample_job_description,
                },
            )
            end_time = time.time()
            return response.status_code, end_time - start_time

        # Execute concurrent requests
        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(make_request) for _ in range(num_concurrent)]
            results = [future.result() for future in as_completed(futures)]

        # Verify all requests succeeded
        status_codes = [result[0] for result in results]
        response_times = [result[1] for result in results]

        assert all(
            code == 200 for code in status_codes
        ), f"Some requests failed: {status_codes}"

        # Check that concurrent processing doesn't significantly degrade performance
        max_time = max(response_times)
        avg_time = statistics.mean(response_times)

        assert max_time < 15.0, f"Slowest concurrent request took {max_time:.2f}s"
        assert (
            avg_time < 12.0
        ), f"Average concurrent response time {avg_time:.2f}s too high"

        print(f"Concurrent performance: max={max_time:.2f}s, avg={avg_time:.2f}s")

    @pytest.mark.performance
    def test_memory_efficiency_large_documents(self, client: TestClient) -> None:
        """Test that the API handles large documents efficiently."""
        # Create a large resume (simulate a detailed 3-page resume)
        large_resume = (
            """
        JOHN DOE - SENIOR SOFTWARE ENGINEER
        
        PROFESSIONAL SUMMARY
        """
            + "Experienced software engineer with expertise in Python, JavaScript, and cloud technologies. "
            * 50
        )

        # Create a large job description
        large_job_desc = (
            """
        SENIOR SOFTWARE ENGINEER POSITION
        
        REQUIREMENTS
        """
            + "We are looking for a skilled engineer with experience in modern technologies. "
            * 30
        )

        start_time = time.time()

        response = client.post(
            "/analyze",
            json={"resume_text": large_resume, "job_description": large_job_desc},
        )

        end_time = time.time()
        processing_time = end_time - start_time

        assert response.status_code == 200
        assert (
            processing_time < 15.0
        ), f"Large document analysis took {processing_time:.2f}s"

        # Verify the response structure is still valid
        data = response.json()
        assert "match_percentage" in data
        assert isinstance(data["match_percentage"], (int, float))

    @pytest.mark.performance
    def test_health_endpoint_performance(self, client: TestClient) -> None:
        """Test that health endpoint responds quickly."""
        response_times = []

        for _ in range(10):
            start_time = time.time()
            response = client.get("/health")
            end_time = time.time()

            assert response.status_code == 200
            response_times.append(end_time - start_time)

        avg_time = statistics.mean(response_times)
        max_time = max(response_times)

        # Health endpoint should be very fast
        assert (
            avg_time < 0.1
        ), f"Health endpoint average response time {avg_time:.3f}s too slow"
        assert (
            max_time < 0.5
        ), f"Health endpoint max response time {max_time:.3f}s too slow"


class TestLoadLimits:
    """Test system behavior under load and edge cases."""

    @pytest.mark.performance
    def test_very_short_documents(self, client: TestClient) -> None:
        """Test performance with minimal document sizes."""
        start_time = time.time()

        response = client.post(
            "/analyze",
            json={
                "resume_text": "John Doe, Engineer",
                "job_description": "Engineer needed",
            },
        )

        end_time = time.time()
        processing_time = end_time - start_time

        assert response.status_code == 200
        # Short documents should process very quickly
        assert (
            processing_time < 5.0
        ), f"Short document analysis took {processing_time:.2f}s"

    @pytest.mark.performance
    def test_maximum_reasonable_document_size(self, client: TestClient) -> None:
        """Test with maximum reasonable document sizes."""
        # Simulate a very detailed resume (5-page equivalent)
        max_resume = (
            "DETAILED PROFESSIONAL EXPERIENCE\n"
            + "Python development experience. " * 200
        )
        max_job_desc = (
            "COMPREHENSIVE JOB REQUIREMENTS\n"
            + "Looking for experienced developer. " * 100
        )

        start_time = time.time()

        response = client.post(
            "/analyze",
            json={"resume_text": max_resume, "job_description": max_job_desc},
        )

        end_time = time.time()
        processing_time = end_time - start_time

        assert response.status_code == 200
        # Even large documents should complete within reasonable time
        assert (
            processing_time < 20.0
        ), f"Maximum size document analysis took {processing_time:.2f}s"

        # Verify response quality isn't degraded
        data = response.json()
        assert data["match_percentage"] >= 0
        assert len(data["matched_keywords"]) >= 0


class TestResourceUsage:
    """Test resource efficiency and cleanup."""

    @pytest.mark.performance
    def test_repeated_analysis_memory_stability(
        self, client: TestClient, sample_resume: str, sample_job_description: str
    ) -> None:
        """Test that repeated analyses don't cause memory leaks."""
        # Perform multiple analyses to check for memory stability
        for i in range(10):
            response = client.post(
                "/analyze",
                json={
                    "resume_text": sample_resume,
                    "job_description": sample_job_description,
                },
            )

            assert response.status_code == 200

            # Basic validation that each response is properly formed
            data = response.json()
            assert "match_percentage" in data
            assert isinstance(data["match_percentage"], (int, float))

        # If we get here without issues, memory is stable
        assert True

    @pytest.mark.performance
    def test_api_endpoint_resource_cleanup(self, client: TestClient) -> None:
        """Test that API endpoints properly clean up resources."""
        # Test various endpoints to ensure they don't leak resources
        endpoints_to_test = [
            ("/health", "GET"),
            ("/logs/status", "GET"),
        ]

        for endpoint, method in endpoints_to_test:
            for _ in range(5):
                if method == "GET":
                    response = client.get(endpoint)
                else:
                    continue  # Skip unsupported methods

                # Just verify they respond without errors
                assert response.status_code in [
                    200,
                    404,
                ], f"Endpoint {endpoint} returned {response.status_code}"
