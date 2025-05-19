"""Health check management for RobustRepo."""
import time
import tempfile
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Callable, Optional, Any
from enum import Enum

import redis
from minio import Minio
from app.celery_app import celery_app
from app.config import Config


class HealthStatus(Enum):
    """Health check status values."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    name: str
    status: HealthStatus
    message: str
    duration_ms: float
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class HealthCheckManager:
    """Manages application health checks."""
    
    def __init__(self):
        """Initialize the health check manager."""
        self.health_checks: Dict[str, Callable] = {}
        self._register_default_checks()
    
    def register_health_check(
        self,
        name: str,
        check_function: Callable[[], HealthCheckResult]
    ):
        """Register a health check function."""
        self.health_checks[name] = check_function
    
    def _register_default_checks(self):
        """Register default health checks."""
        self.register_health_check("redis", self._check_redis)
        self.register_health_check("minio", self._check_minio)
        self.register_health_check("celery", self._check_celery)
        self.register_health_check("disk_space", self._check_disk_space)
        self.register_health_check("memory", self._check_memory)
    
    def run_health_check(self, name: str) -> HealthCheckResult:
        """Run a specific health check."""
        if name not in self.health_checks:
            return HealthCheckResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check '{name}' not found",
                duration_ms=0,
                timestamp=datetime.utcnow()
            )
        
        start_time = time.time()
        try:
            result = self.health_checks[name]()
            duration_ms = (time.time() - start_time) * 1000
            result.duration_ms = duration_ms
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return HealthCheckResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                duration_ms=duration_ms,
                timestamp=datetime.utcnow()
            )
    
    def run_all_checks(self) -> Dict[str, HealthCheckResult]:
        """Run all registered health checks."""
        results = {}
        for name in self.health_checks:
            results[name] = self.run_health_check(name)
        return results
    
    def get_overall_status(self) -> HealthStatus:
        """Get overall system health status."""
        results = self.run_all_checks()
        
        # If any check is unhealthy, system is unhealthy
        if any(result.status == HealthStatus.UNHEALTHY for result in results.values()):
            return HealthStatus.UNHEALTHY
        
        # If any check is degraded, system is degraded
        if any(result.status == HealthStatus.DEGRADED for result in results.values()):
            return HealthStatus.DEGRADED
        
        return HealthStatus.HEALTHY
    
    def _check_redis(self) -> HealthCheckResult:
        """Check Redis connectivity."""
        try:
            r = redis.from_url(Config.REDIS_URL)
            r.ping()
            
            # Get some basic stats
            info = r.info()
            
            return HealthCheckResult(
                name="redis",
                status=HealthStatus.HEALTHY,
                message="Redis is connected and responsive",
                duration_ms=0,
                timestamp=datetime.utcnow(),
                metadata={
                    "version": info.get("redis_version"),
                    "connected_clients": info.get("connected_clients"),
                    "used_memory_human": info.get("used_memory_human")
                }
            )
        except Exception as e:
            return HealthCheckResult(
                name="redis",
                status=HealthStatus.UNHEALTHY,
                message=f"Redis connection failed: {str(e)}",
                duration_ms=0,
                timestamp=datetime.utcnow()
            )
    
    def _check_minio(self) -> HealthCheckResult:
        """Check MinIO connectivity."""
        try:
            client = Minio(
                Config.MINIO_ENDPOINT,
                access_key=Config.MINIO_ACCESS_KEY,
                secret_key=Config.MINIO_SECRET_KEY,
                secure=Config.MINIO_SECURE
            )
            
            # List buckets to verify connection
            buckets = client.list_buckets()
            
            return HealthCheckResult(
                name="minio",
                status=HealthStatus.HEALTHY,
                message="MinIO is connected and responsive",
                duration_ms=0,
                timestamp=datetime.utcnow(),
                metadata={
                    "bucket_count": len(buckets),
                    "buckets": [b.name for b in buckets]
                }
            )
        except Exception as e:
            return HealthCheckResult(
                name="minio",
                status=HealthStatus.UNHEALTHY,
                message=f"MinIO connection failed: {str(e)}",
                duration_ms=0,
                timestamp=datetime.utcnow()
            )
    
    def _check_celery(self) -> HealthCheckResult:
        """Check Celery worker status."""
        try:
            # Get active workers
            inspect = celery_app.control.inspect()
            active_workers = inspect.active()
            
            if not active_workers:
                return HealthCheckResult(
                    name="celery",
                    status=HealthStatus.UNHEALTHY,
                    message="No active Celery workers found",
                    duration_ms=0,
                    timestamp=datetime.utcnow()
                )
            
            # Count total workers and tasks
            worker_count = len(active_workers)
            total_tasks = sum(len(tasks) for tasks in active_workers.values())
            
            # Get worker stats
            stats = inspect.stats()
            
            return HealthCheckResult(
                name="celery",
                status=HealthStatus.HEALTHY,
                message=f"{worker_count} active workers with {total_tasks} tasks",
                duration_ms=0,
                timestamp=datetime.utcnow(),
                metadata={
                    "worker_count": worker_count,
                    "active_tasks": total_tasks,
                    "workers": list(active_workers.keys()),
                    "stats": stats
                }
            )
        except Exception as e:
            return HealthCheckResult(
                name="celery",
                status=HealthStatus.UNHEALTHY,
                message=f"Celery check failed: {str(e)}",
                duration_ms=0,
                timestamp=datetime.utcnow()
            )
    
    def _check_disk_space(self) -> HealthCheckResult:
        """Check available disk space."""
        try:
            import shutil
            
            # Check temp directory space
            stat = shutil.disk_usage(tempfile.gettempdir())
            
            # Calculate percentage used
            used_percent = (stat.used / stat.total) * 100
            
            if used_percent > 90:
                status = HealthStatus.UNHEALTHY
                message = f"Critical: Disk space at {used_percent:.1f}% used"
            elif used_percent > 80:
                status = HealthStatus.DEGRADED
                message = f"Warning: Disk space at {used_percent:.1f}% used"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk space at {used_percent:.1f}% used"
            
            return HealthCheckResult(
                name="disk_space",
                status=status,
                message=message,
                duration_ms=0,
                timestamp=datetime.utcnow(),
                metadata={
                    "total_bytes": stat.total,
                    "used_bytes": stat.used,
                    "free_bytes": stat.free,
                    "used_percent": used_percent
                }
            )
        except Exception as e:
            return HealthCheckResult(
                name="disk_space",
                status=HealthStatus.UNHEALTHY,
                message=f"Disk space check failed: {str(e)}",
                duration_ms=0,
                timestamp=datetime.utcnow()
            )
    
    def _check_memory(self) -> HealthCheckResult:
        """Check memory usage."""
        try:
            import psutil
            
            # Get memory statistics
            memory = psutil.virtual_memory()
            
            if memory.percent > 90:
                status = HealthStatus.UNHEALTHY
                message = f"Critical: Memory at {memory.percent:.1f}% used"
            elif memory.percent > 80:
                status = HealthStatus.DEGRADED
                message = f"Warning: Memory at {memory.percent:.1f}% used"
            else:
                status = HealthStatus.HEALTHY
                message = f"Memory at {memory.percent:.1f}% used"
            
            return HealthCheckResult(
                name="memory",
                status=status,
                message=message,
                duration_ms=0,
                timestamp=datetime.utcnow(),
                metadata={
                    "total_bytes": memory.total,
                    "available_bytes": memory.available,
                    "used_bytes": memory.used,
                    "used_percent": memory.percent
                }
            )
        except Exception as e:
            return HealthCheckResult(
                name="memory",
                status=HealthStatus.UNHEALTHY,
                message=f"Memory check failed: {str(e)}",
                duration_ms=0,
                timestamp=datetime.utcnow()
            )


# Global health check manager
health_manager = HealthCheckManager()


# Convenience functions
def register_health_check(name: str, check_function: Callable[[], HealthCheckResult]):
    """Register a health check."""
    health_manager.register_health_check(name, check_function)


def run_health_check(name: str) -> HealthCheckResult:
    """Run a specific health check."""
    return health_manager.run_health_check(name)


def run_all_health_checks() -> Dict[str, HealthCheckResult]:
    """Run all health checks."""
    return health_manager.run_all_checks()


def get_overall_health() -> HealthStatus:
    """Get overall system health."""
    return health_manager.get_overall_status()