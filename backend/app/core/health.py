"""
Health check and readiness monitoring for UNIFIND backend.

Provides comprehensive health checks for:
- Application health
- Database connectivity
- External service dependencies
- System resources
"""

import logging
import time
from datetime import datetime
from enum import Enum
from typing import Any, Dict

import psutil

from app.core.database import get_db
from app.core.observability import PerformanceTracker, metrics

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health check status values."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class DependencyStatus(str, Enum):
    """Dependency check status values."""

    UP = "up"
    DOWN = "down"
    DEGRADED = "degraded"


class HealthCheck:
    """
    Comprehensive health checking system.

    Monitors application health, dependencies, and system resources.
    """

    def __init__(self):
        self._start_time = time.time()
        self._logger = logging.getLogger(f"{__name__}.health")

    async def check_health(self, include_details: bool = False) -> Dict[str, Any]:
        """
        Perform comprehensive health check.

        Args:
            include_details: Include detailed dependency checks

        Returns:
            Health check result with status and details
        """
        with PerformanceTracker("health_check", threshold_ms=500):
            health_data = {
                "status": HealthStatus.HEALTHY.value,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "uptime_seconds": int(time.time() - self._start_time),
                "version": "2.1.0",
            }

            if include_details:
                # Check all dependencies
                dependencies = await self._check_dependencies()
                health_data["dependencies"] = dependencies

                # Check system resources
                resources = self._check_system_resources()
                health_data["resources"] = resources

                # Determine overall status
                health_data["status"] = self._determine_overall_status(dependencies)

            # Record health check metric
            metrics.increment("health.checks.total")

            return health_data

    async def check_readiness(self) -> Dict[str, Any]:
        """
        Check if the application is ready to serve traffic.

        Returns:
            Readiness status with critical dependency checks
        """
        with PerformanceTracker("readiness_check", threshold_ms=1000):
            readiness_data = {
                "ready": True,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "checks": {},
            }

            # Check critical dependencies
            critical_checks = [
                ("database", self._check_database),
            ]

            for check_name, check_func in critical_checks:
                try:
                    result = await check_func()
                    readiness_data["checks"][check_name] = result

                    if result["status"] != DependencyStatus.UP.value:
                        readiness_data["ready"] = False
                except Exception as e:
                    self._logger.error(f"Readiness check failed for {check_name}: {e}")
                    readiness_data["checks"][check_name] = {
                        "status": DependencyStatus.DOWN.value,
                        "error": str(e),
                    }
                    readiness_data["ready"] = False

            # Record readiness metric
            metrics.gauge("readiness.status", 1.0 if readiness_data["ready"] else 0.0)

            return readiness_data

    async def check_liveness(self) -> Dict[str, Any]:
        """
        Check if the application is alive (basic health).

        Returns:
            Liveness status
        """
        return {
            "alive": True,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "uptime_seconds": int(time.time() - self._start_time),
        }

    async def _check_dependencies(self) -> Dict[str, Dict[str, Any]]:
        """Check all external dependencies."""
        dependencies = {}

        # Database check
        dependencies["database"] = await self._check_database()

        # Gemini AI check
        dependencies["gemini_ai"] = await self._check_gemini_ai()

        # Cloudinary check
        dependencies["cloudinary"] = await self._check_cloudinary()

        return dependencies

    async def _check_database(self) -> Dict[str, Any]:
        """Check Firebase database connectivity."""
        try:
            start_time = time.time()
            db = get_db()

            # Perform a simple query
            _ = db.collection("_health_check").limit(1).get()

            latency_ms = (time.time() - start_time) * 1000

            # Record database latency
            metrics.timing("database.latency_ms", latency_ms)

            status = DependencyStatus.UP
            if latency_ms > 1000:
                status = DependencyStatus.DEGRADED

            return {
                "status": status.value,
                "latency_ms": round(latency_ms, 2),
                "message": "Database connection successful",
            }
        except Exception as e:
            self._logger.error(f"Database health check failed: {e}")
            metrics.increment("database.health_check.failures")
            return {
                "status": DependencyStatus.DOWN.value,
                "error": str(e),
                "message": "Database connection failed",
            }

    async def _check_gemini_ai(self) -> Dict[str, Any]:
        """Check Gemini AI service availability."""
        try:
            # Basic check - verify configuration exists
            from app.core.config import settings

            if not settings.GEMINI_API_KEY:
                return {
                    "status": DependencyStatus.DOWN.value,
                    "message": "Gemini API key not configured",
                }

            # In production, you might want to make a test API call
            return {"status": DependencyStatus.UP.value, "message": "Gemini AI configured"}
        except Exception as e:
            self._logger.error(f"Gemini AI health check failed: {e}")
            return {
                "status": DependencyStatus.DOWN.value,
                "error": str(e),
                "message": "Gemini AI check failed",
            }

    async def _check_cloudinary(self) -> Dict[str, Any]:
        """Check Cloudinary service availability."""
        try:
            from app.core.config import settings

            if not settings.CLOUDINARY_CLOUD_NAME:
                return {
                    "status": DependencyStatus.DOWN.value,
                    "message": "Cloudinary not configured",
                }

            return {"status": DependencyStatus.UP.value, "message": "Cloudinary configured"}
        except Exception as e:
            self._logger.error(f"Cloudinary health check failed: {e}")
            return {
                "status": DependencyStatus.DOWN.value,
                "error": str(e),
                "message": "Cloudinary check failed",
            }

    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage."""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # Record resource metrics
            metrics.gauge("system.cpu.percent", cpu_percent)
            metrics.gauge("system.memory.percent", memory.percent)
            metrics.gauge("system.disk.percent", disk.percent)

            return {
                "cpu": {
                    "percent": round(cpu_percent, 2),
                    "status": "healthy" if cpu_percent < 80 else "degraded",
                },
                "memory": {
                    "percent": round(memory.percent, 2),
                    "available_mb": round(memory.available / (1024 * 1024), 2),
                    "total_mb": round(memory.total / (1024 * 1024), 2),
                    "status": "healthy" if memory.percent < 85 else "degraded",
                },
                "disk": {
                    "percent": round(disk.percent, 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "total_gb": round(disk.total / (1024**3), 2),
                    "status": "healthy" if disk.percent < 90 else "degraded",
                },
            }
        except Exception as e:
            self._logger.error(f"System resource check failed: {e}")
            return {"error": str(e), "status": "unknown"}

    def _determine_overall_status(self, dependencies: Dict[str, Dict[str, Any]]) -> str:
        """
        Determine overall health status based on dependencies.

        Args:
            dependencies: Dictionary of dependency check results

        Returns:
            Overall health status
        """
        statuses = [dep.get("status") for dep in dependencies.values()]

        if any(status == DependencyStatus.DOWN.value for status in statuses):
            return HealthStatus.UNHEALTHY.value
        elif any(status == DependencyStatus.DEGRADED.value for status in statuses):
            return HealthStatus.DEGRADED.value
        else:
            return HealthStatus.HEALTHY.value


# Global health check instance
health_checker = HealthCheck()
