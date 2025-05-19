"""OpenTelemetry tracing implementation for RobustRepo."""
import functools
import time
from typing import Any, Callable, Dict, Optional
from contextlib import contextmanager

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.trace import Status, StatusCode

# Try different import paths for OTLP exporter
try:
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
except ImportError:
    try:
        from opentelemetry.exporter.otlp.proto.grpc import OTLPSpanExporter
    except ImportError:
        try:
            from opentelemetry.exporter.otlp.trace_exporter import OTLPSpanExporter
        except ImportError:
            from opentelemetry.exporter.otlp import OTLPSpanExporter

# Instrumentation imports
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from app.config import Config


class TracingManager:
    """Manages OpenTelemetry tracing configuration and setup."""
    
    def __init__(self, service_name: str = "robustrepo", environment: str = "production"):
        """Initialize the tracing manager."""
        self.service_name = service_name
        self.environment = environment
        self.tracer_provider = None
        self.tracer = None
        self._initialized = False
    
    def initialize(self, app=None):
        """Initialize OpenTelemetry tracing."""
        if self._initialized:
            return
        
        # Create resource with service information
        resource = Resource.create({
            "service.name": self.service_name,
            "service.version": Config.VERSION,
            "deployment.environment": self.environment,
            "telemetry.sdk.language": "python",
        })
        
        # Set up tracer provider
        self.tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(self.tracer_provider)
        
        # Configure exporters based on environment
        if Config.OTEL_ENABLED:
            # OTLP exporter for production
            otlp_exporter = OTLPSpanExporter(
                endpoint=Config.OTEL_COLLECTOR_ENDPOINT,
                insecure=Config.OTEL_INSECURE_ENDPOINT
            )
            self.tracer_provider.add_span_processor(
                BatchSpanProcessor(otlp_exporter)
            )
        
        if Config.DEBUG or self.environment == "development":
            # Console exporter for debugging
            console_exporter = ConsoleSpanExporter()
            self.tracer_provider.add_span_processor(
                BatchSpanProcessor(console_exporter)
            )
        
        # Get tracer
        self.tracer = trace.get_tracer(__name__)
        
        # Instrument libraries
        self._instrument_libraries(app)
        
        self._initialized = True
    
    def _instrument_libraries(self, app=None):
        """Auto-instrument common libraries."""
        try:
            # Flask instrumentation
            if app:
                flask_instrumentor = FlaskInstrumentor()
                if not flask_instrumentor.is_instrumented_by_opentelemetry:
                    flask_instrumentor.instrument_app(app)
            
            # Celery instrumentation
            celery_instrumentor = CeleryInstrumentor()
            if not celery_instrumentor.is_instrumented_by_opentelemetry:
                celery_instrumentor.instrument()
            
            # Redis instrumentation
            redis_instrumentor = RedisInstrumentor()
            if not redis_instrumentor.is_instrumented_by_opentelemetry:
                redis_instrumentor.instrument()
            
            # HTTP requests instrumentation
            requests_instrumentor = RequestsInstrumentor()
            if not requests_instrumentor.is_instrumented_by_opentelemetry:
                requests_instrumentor.instrument()
            
        except Exception as e:
            print(f"Warning: Failed to instrument some libraries: {e}")
    
    def get_tracer(self) -> trace.Tracer:
        """Get the tracer instance."""
        if not self._initialized:
            raise RuntimeError("TracingManager not initialized. Call initialize() first.")
        return self.tracer
    
    @contextmanager
    def create_span(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        kind: trace.SpanKind = trace.SpanKind.INTERNAL
    ):
        """Create a new span with the given name."""
        tracer = self.get_tracer()
        
        with tracer.start_as_current_span(
            name,
            kind=kind,
            attributes=attributes or {}
        ) as span:
            try:
                yield span
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
    
    def trace_operation(
        self,
        name: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        record_exception: bool = True
    ):
        """Decorator to trace function execution."""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                span_name = name or f"{func.__module__}.{func.__name__}"
                
                with self.create_span(
                    span_name,
                    attributes=attributes
                ) as span:
                    # Add function details
                    span.set_attribute("function.module", func.__module__)
                    span.set_attribute("function.name", func.__name__)
                    
                    # Add timing
                    start_time = time.time()
                    
                    try:
                        result = func(*args, **kwargs)
                        
                        # Record success metrics
                        span.set_attribute("function.duration_ms", 
                                         (time.time() - start_time) * 1000)
                        span.set_status(Status(StatusCode.OK))
                        
                        return result
                        
                    except Exception as e:
                        # Record error metrics
                        span.set_attribute("function.duration_ms", 
                                         (time.time() - start_time) * 1000)
                        span.set_attribute("error.type", type(e).__name__)
                        span.set_attribute("error.message", str(e))
                        
                        if record_exception:
                            span.record_exception(e)
                            span.set_status(Status(StatusCode.ERROR, str(e)))
                        
                        raise
            
            return wrapper
        return decorator


# Global tracing manager instance
tracing_manager = TracingManager()


# Convenience functions
def initialize_tracing(app=None, service_name: str = "robustrepo", environment: str = "production"):
    """Initialize global tracing."""
    global tracing_manager
    tracing_manager = TracingManager(service_name, environment)
    tracing_manager.initialize(app)


def trace_operation(
    name: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
    record_exception: bool = True
):
    """Convenience decorator for tracing operations."""
    return tracing_manager.trace_operation(name, attributes, record_exception)


@contextmanager
def create_span(
    name: str,
    attributes: Optional[Dict[str, Any]] = None,
    kind: trace.SpanKind = trace.SpanKind.INTERNAL
):
    """Convenience function to create a span."""
    with tracing_manager.create_span(name, attributes, kind) as span:
        yield span


# Task-specific tracing helpers
@contextmanager
def trace_repository_processing(
    repo_url: str,
    processing_mode: str,
    token_budget: Optional[int] = None
):
    """Trace repository processing operations."""
    attributes = {
        "repo.url": repo_url,
        "processing.mode": processing_mode,
    }
    if token_budget:
        attributes["processing.token_budget"] = token_budget
    
    with create_span("repository.process", attributes) as span:
        yield span


@contextmanager
def trace_llm_context_generation(
    task_type: str,
    model: str,
    token_budget: int,
    file_count: int
):
    """Trace LLM context generation."""
    with create_span(
        "llm.context.generate",
        attributes={
            "llm.task_type": task_type,
            "llm.model": model,
            "llm.token_budget": token_budget,
            "llm.file_count": file_count,
        }
    ) as span:
        yield span


@contextmanager
def trace_storage_operation(
    operation: str,
    bucket: str,
    object_key: str,
    size: Optional[int] = None
):
    """Trace storage operations."""
    attributes = {
        "storage.operation": operation,
        "storage.bucket": bucket,
        "storage.object_key": object_key,
    }
    if size:
        attributes["storage.size_bytes"] = size
    
    with create_span(f"storage.{operation}", attributes) as span:
        yield span