"""Advanced monitoring and metrics collection for the VidyaMitra Career Agent.

Copyright (c) 2026 VidyaMitra Career Agent
Licensed under the MIT License. See LICENSE file for details.
"""

import time
import logging
import functools
from typing import Dict, Any, Callable, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
from threading import Lock

from app.logging_config import log_analysis_request, log_request


class PerformanceMonitor:
    """Monitor and track application performance metrics."""

    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics = {
            "request_times": deque(maxlen=max_history),
            "analysis_times": deque(maxlen=max_history),
            "success_count": 0,
            "error_count": 0,
            "total_requests": 0,
            "analysis_success_count": 0,
            "analysis_error_count": 0,
        }
        self.hourly_stats = defaultdict(
            lambda: {"requests": 0, "errors": 0, "avg_response_time": 0.0}
        )
        self.lock = Lock()
        self.logger = logging.getLogger("resume_analyzer.monitoring")

    def record_request(self, processing_time: float, success: bool = True) -> None:
        """Record a request performance metric."""
        with self.lock:
            self.metrics["request_times"].append(processing_time)
            self.metrics["total_requests"] += 1

            if success:
                self.metrics["success_count"] += 1
            else:
                self.metrics["error_count"] += 1

            # Update hourly stats
            current_hour = datetime.now().strftime("%Y-%m-%d %H:00")
            self.hourly_stats[current_hour]["requests"] += 1
            if not success:
                self.hourly_stats[current_hour]["errors"] += 1

    def record_analysis(
        self,
        processing_time: float,
        resume_len: int,
        job_desc_len: int,
        success: bool = True,
        error: str = None,
    ) -> None:
        """Record an analysis performance metric."""
        with self.lock:
            self.metrics["analysis_times"].append(processing_time)

            if success:
                self.metrics["analysis_success_count"] += 1
            else:
                self.metrics["analysis_error_count"] += 1

        # Log the analysis request
        log_analysis_request(resume_len, job_desc_len, processing_time, success, error)

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics."""
        with self.lock:
            request_times = list(self.metrics["request_times"])
            analysis_times = list(self.metrics["analysis_times"])

            stats = {
                "total_requests": self.metrics["total_requests"],
                "success_rate": self._calculate_success_rate(),
                "analysis_success_rate": self._calculate_analysis_success_rate(),
                "performance": {
                    "avg_request_time": self._calculate_average(request_times),
                    "avg_analysis_time": self._calculate_average(analysis_times),
                    "p95_request_time": self._calculate_percentile(request_times, 95),
                    "p95_analysis_time": self._calculate_percentile(analysis_times, 95),
                    "min_request_time": min(request_times) if request_times else 0,
                    "max_request_time": max(request_times) if request_times else 0,
                },
                "health_status": self._get_health_status(),
                "hourly_trends": dict(self.hourly_stats),
            }

            return stats

    def _calculate_success_rate(self) -> float:
        """Calculate overall success rate."""
        total = self.metrics["success_count"] + self.metrics["error_count"]
        if total == 0:
            return 100.0
        return (self.metrics["success_count"] / total) * 100

    def _calculate_analysis_success_rate(self) -> float:
        """Calculate analysis success rate."""
        total = (
            self.metrics["analysis_success_count"]
            + self.metrics["analysis_error_count"]
        )
        if total == 0:
            return 100.0
        return (self.metrics["analysis_success_count"] / total) * 100

    def _calculate_average(self, values: list) -> float:
        """Calculate average of values."""
        return sum(values) / len(values) if values else 0.0

    def _calculate_percentile(self, values: list, percentile: int) -> float:
        """Calculate percentile of values."""
        if not values:
            return 0.0
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]

    def _get_health_status(self) -> str:
        """Determine overall health status."""
        success_rate = self._calculate_success_rate()
        analysis_success_rate = self._calculate_analysis_success_rate()

        request_times = list(self.metrics["request_times"])
        avg_time = self._calculate_average(request_times)

        if success_rate < 90 or analysis_success_rate < 90:
            return "unhealthy"
        elif avg_time > 10.0:  # More than 10 seconds average
            return "degraded"
        elif success_rate < 95 or analysis_success_rate < 95:
            return "warning"
        else:
            return "healthy"

    def cleanup_old_data(self, hours_to_keep: int = 24) -> None:
        """Clean up old hourly statistics."""
        cutoff_time = datetime.now() - timedelta(hours=hours_to_keep)
        cutoff_str = cutoff_time.strftime("%Y-%m-%d %H:00")

        with self.lock:
            keys_to_remove = [
                key for key in self.hourly_stats.keys() if key < cutoff_str
            ]
            for key in keys_to_remove:
                del self.hourly_stats[key]


# Global monitor instance
performance_monitor = PerformanceMonitor()


def monitor_performance(operation_type: str = "request"):
    """Decorator to monitor function performance."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error_msg = None

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_msg = str(e)
                raise
            finally:
                end_time = time.time()
                processing_time = end_time - start_time

                if operation_type == "request":
                    performance_monitor.record_request(processing_time, success)
                elif operation_type == "analysis":
                    # Try to extract document lengths from args/kwargs
                    resume_len = 0
                    job_desc_len = 0

                    # This is a simple heuristic - adjust based on your function signatures
                    if args and hasattr(args[0], "resume_text"):
                        resume_len = len(args[0].resume_text)
                    if args and hasattr(args[0], "job_description"):
                        job_desc_len = len(args[0].job_description)

                    performance_monitor.record_analysis(
                        processing_time, resume_len, job_desc_len, success, error_msg
                    )

        return wrapper

    return decorator


class HealthChecker:
    """Health check functionality for the application."""

    def __init__(self):
        self.logger = logging.getLogger("resume_analyzer.health")
        self.checks = {
            "performance": self._check_performance,
            "logging": self._check_logging,
            "memory": self._check_memory,
        }

    def check_health(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "overall_score": 100,
        }

        total_score = 0
        check_count = 0

        for check_name, check_func in self.checks.items():
            try:
                check_result = check_func()
                health_status["checks"][check_name] = check_result
                total_score += check_result.get("score", 100)
                check_count += 1

                if check_result.get("status") == "failed":
                    health_status["status"] = "unhealthy"
                elif (
                    check_result.get("status") == "warning"
                    and health_status["status"] == "healthy"
                ):
                    health_status["status"] = "warning"

            except Exception as e:
                self.logger.error(f"Health check {check_name} failed: {e}")
                health_status["checks"][check_name] = {
                    "status": "failed",
                    "error": str(e),
                    "score": 0,
                }
                health_status["status"] = "unhealthy"
                check_count += 1

        health_status["overall_score"] = (
            total_score / check_count if check_count > 0 else 0
        )

        return health_status

    def _check_performance(self) -> Dict[str, Any]:
        """Check performance metrics."""
        stats = performance_monitor.get_performance_stats()

        success_rate = stats["success_rate"]
        avg_time = stats["performance"]["avg_request_time"]

        if success_rate < 90 or avg_time > 15:
            status = "failed"
            score = max(0, min(100, success_rate - 10))
        elif success_rate < 95 or avg_time > 10:
            status = "warning"
            score = max(70, min(100, success_rate))
        else:
            status = "passed"
            score = 100

        return {
            "status": status,
            "score": score,
            "details": {
                "success_rate": success_rate,
                "avg_response_time": avg_time,
                "total_requests": stats["total_requests"],
            },
        }

    def _check_logging(self) -> Dict[str, Any]:
        """Check logging system health."""
        try:
            # Test if we can write to log
            test_logger = logging.getLogger("resume_analyzer.health_test")
            test_logger.info("Health check test log message")

            return {
                "status": "passed",
                "score": 100,
                "details": {"logging_functional": True},
            }
        except Exception as e:
            return {"status": "failed", "score": 0, "details": {"error": str(e)}}

    def _check_memory(self) -> Dict[str, Any]:
        """Check memory usage (basic check)."""
        try:
            import psutil
            import os

            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)

            # Basic thresholds - adjust based on your requirements
            if memory_mb > 1000:  # Over 1GB
                status = "warning"
                score = 70
            elif memory_mb > 2000:  # Over 2GB
                status = "failed"
                score = 30
            else:
                status = "passed"
                score = 100

            return {
                "status": status,
                "score": score,
                "details": {
                    "memory_mb": round(memory_mb, 2),
                    "memory_bytes": memory_info.rss,
                },
            }
        except ImportError:
            # psutil not available
            return {
                "status": "passed",
                "score": 80,
                "details": {"psutil_available": False},
            }
        except Exception as e:
            return {"status": "warning", "score": 50, "details": {"error": str(e)}}


# Global health checker instance
health_checker = HealthChecker()


def get_system_status() -> Dict[str, Any]:
    """Get comprehensive system status including performance and health."""
    return {
        "health": health_checker.check_health(),
        "performance": performance_monitor.get_performance_stats(),
        "timestamp": datetime.now().isoformat(),
    }
