"""OpenTelemetry metrics implementation for RobustRepo."""
import time
from typing import Dict, Any, Optional, Callable
from contextlib import contextmanager

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.sdk.resources import Resource

from app.config import Config


class MetricsManager:
    """Manages OpenTelemetry metrics collection and export."""
    
    def __init__(self, service_name: str = "robustrepo", environment: str = "production"):
        """Initialize the metrics manager."""
        self.service_name = service_name
        self.environment = environment
        self.meter_provider = None
        self.meter = None
        self._initialized = False
        self._metrics = {}
    
    def initialize(self):
        """Initialize OpenTelemetry metrics."""
        if self._initialized:
            return
        
        # Create resource
        resource = Resource.create({
            "service.name": self.service_name,
            "service.version": Config.VERSION,
            "deployment.environment": self.environment,
        })
        
        # Configure exporters
        readers = []
        
        if Config.OTEL_ENABLED:
            # OTLP exporter for production
            otlp_exporter = OTLPMetricExporter(
                endpoint=Config.OTEL_COLLECTOR_ENDPOINT,
                insecure=Config.OTEL_INSECURE_ENDPOINT
            )
            readers.append(
                PeriodicExportingMetricReader(
                    exporter=otlp_exporter,
                    export_interval_millis=30000  # 30 seconds
                )
            )
        
        if Config.DEBUG or self.environment == "development":
            # Console exporter for debugging
            console_exporter = ConsoleMetricExporter()
            readers.append(
                PeriodicExportingMetricReader(
                    exporter=console_exporter,
                    export_interval_millis=10000  # 10 seconds
                )
            )
        
        # Create meter provider
        self.meter_provider = MeterProvider(
            resource=resource,
            metric_readers=readers
        )
        
        # Set global meter provider
        metrics.set_meter_provider(self.meter_provider)
        
        # Get meter
        self.meter = metrics.get_meter(__name__)
        
        # Initialize default metrics
        self._initialize_default_metrics()
        
        self._initialized = True
    
    def _initialize_default_metrics(self):
        """Initialize default application metrics."""
        # Request metrics
        self._metrics['request_counter'] = self.meter.create_counter(
            name="robustrepo.requests.total",
            description="Total number of requests",
            unit="1"
        )
        
        self._metrics['request_duration'] = self.meter.create_histogram(
            name="robustrepo.requests.duration",
            description="Request duration in milliseconds",
            unit="ms"
        )
        
        # Job metrics
        self._metrics['job_counter'] = self.meter.create_counter(
            name="robustrepo.jobs.total",
            description="Total number of jobs",
            unit="1"
        )
        
        self._metrics['job_duration'] = self.meter.create_histogram(
            name="robustrepo.jobs.duration",
            description="Job processing duration in seconds",
            unit="s"
        )
        
        # LLM metrics
        self._metrics['llm_tokens_used'] = self.meter.create_counter(
            name="robustrepo.llm.tokens.used",
            description="Total tokens used in LLM operations",
            unit="tokens"
        )
        
        self._metrics['llm_context_size'] = self.meter.create_histogram(
            name="robustrepo.llm.context.size",
            description="Size of generated LLM contexts",
            unit="tokens"
        )
        
        # Storage metrics
        self._metrics['storage_operations'] = self.meter.create_counter(
            name="robustrepo.storage.operations.total",
            description="Total storage operations",
            unit="1"
        )
        
        self._metrics['storage_bytes'] = self.meter.create_counter(
            name="robustrepo.storage.bytes.total",
            description="Total bytes transferred",
            unit="bytes"
        )
        
        # Repository processing metrics
        self._metrics['repo_files_processed'] = self.meter.create_histogram(
            name="robustrepo.repo.files.processed",
            description="Number of files processed per repository",
            unit="files"
        )
        
        self._metrics['repo_processing_time'] = self.meter.create_histogram(
            name="robustrepo.repo.processing.time",
            description="Repository processing time",
            unit="s"
        )
    
    def get_metric(self, name: str):
        """Get a metric by name."""
        if not self._initialized:
            raise RuntimeError("MetricsManager not initialized. Call initialize() first.")
        return self._metrics.get(name)
    
    def create_counter(
        self,
        name: str,
        description: str = "",
        unit: str = "1"
    ):
        """Create a new counter metric."""
        if not self._initialized:
            raise RuntimeError("MetricsManager not initialized. Call initialize() first.")
        
        counter = self.meter.create_counter(
            name=name,
            description=description,
            unit=unit
        )
        self._metrics[name] = counter
        return counter
    
    def create_histogram(
        self,
        name: str,
        description: str = "",
        unit: str = "1"
    ):
        """Create a new histogram metric."""
        if not self._initialized:
            raise RuntimeError("MetricsManager not initialized. Call initialize() first.")
        
        histogram = self.meter.create_histogram(
            name=name,
            description=description,
            unit=unit
        )
        self._metrics[name] = histogram
        return histogram
    
    def create_gauge(
        self,
        name: str,
        description: str = "",
        unit: str = "1"
    ):
        """Create a new gauge metric."""
        if not self._initialized:
            raise RuntimeError("MetricsManager not initialized. Call initialize() first.")
        
        # For gauges, we use observable gauges in OpenTelemetry
        # This requires a callback function
        def default_callback(options):
            yield metrics.Observation(0, {})
        
        gauge = self.meter.create_observable_gauge(
            name=name,
            description=description,
            unit=unit,
            callbacks=[default_callback]
        )
        self._metrics[name] = gauge
        return gauge
    
    def record_metric(
        self,
        name: str,
        value: float,
        attributes: Optional[Dict[str, Any]] = None
    ):
        """Record a metric value."""
        metric = self.get_metric(name)
        if metric:
            if hasattr(metric, 'add'):
                # Counter
                metric.add(value, attributes or {})
            elif hasattr(metric, 'record'):
                # Histogram
                metric.record(value, attributes or {})
    
    @contextmanager
    def timed_operation(
        self,
        metric_name: str,
        attributes: Optional[Dict[str, Any]] = None
    ):
        """Context manager to time an operation."""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.record_metric(metric_name, duration, attributes)


# Global metrics manager instance
metrics_manager = MetricsManager()


# Convenience functions
def initialize_metrics(service_name: str = "robustrepo", environment: str = "production"):
    """Initialize global metrics collection."""
    global metrics_manager
    metrics_manager = MetricsManager(service_name, environment)
    metrics_manager.initialize()


def record_metric(
    name: str,
    value: float,
    attributes: Optional[Dict[str, Any]] = None
):
    """Record a metric value."""
    metrics_manager.record_metric(name, value, attributes)


def create_counter(name: str, description: str = "", unit: str = "1"):
    """Create a counter metric."""
    return metrics_manager.create_counter(name, description, unit)


def create_histogram(name: str, description: str = "", unit: str = "1"):
    """Create a histogram metric."""
    return metrics_manager.create_histogram(name, description, unit)


@contextmanager
def timed_operation(
    metric_name: str,
    attributes: Optional[Dict[str, Any]] = None
):
    """Time an operation and record to metrics."""
    with metrics_manager.timed_operation(metric_name, attributes):
        yield


# Metric recording helpers
def record_request(
    endpoint: str,
    method: str,
    status_code: int,
    duration_ms: float
):
    """Record HTTP request metrics."""
    attributes = {
        "http.endpoint": endpoint,
        "http.method": method,
        "http.status_code": status_code,
    }
    
    record_metric("robustrepo.requests.total", 1, attributes)
    record_metric("robustrepo.requests.duration", duration_ms, attributes)


def record_job(
    job_type: str,
    status: str,
    duration_s: float
):
    """Record job processing metrics."""
    attributes = {
        "job.type": job_type,
        "job.status": status,
    }
    
    record_metric("robustrepo.jobs.total", 1, attributes)
    record_metric("robustrepo.jobs.duration", duration_s, attributes)


def record_llm_usage(
    model: str,
    task_type: str,
    tokens_used: int,
    context_size: int
):
    """Record LLM usage metrics."""
    attributes = {
        "llm.model": model,
        "llm.task_type": task_type,
    }
    
    record_metric("robustrepo.llm.tokens.used", tokens_used, attributes)
    record_metric("robustrepo.llm.context.size", context_size, attributes)


def record_storage_operation(
    operation: str,
    bytes_transferred: int,
    success: bool
):
    """Record storage operation metrics."""
    attributes = {
        "storage.operation": operation,
        "storage.success": str(success),
    }
    
    record_metric("robustrepo.storage.operations.total", 1, attributes)
    if bytes_transferred > 0:
        record_metric("robustrepo.storage.bytes.total", bytes_transferred, attributes)


def record_repository_processing(
    repo_url: str,
    files_processed: int,
    processing_time_s: float,
    mode: str
):
    """Record repository processing metrics."""
    attributes = {
        "repo.url": repo_url,
        "processing.mode": mode,
    }
    
    record_metric("robustrepo.repo.files.processed", files_processed, attributes)
    record_metric("robustrepo.repo.processing.time", processing_time_s, attributes)