# Observability Package for RobustRepo
"""
Provides OpenTelemetry instrumentation for distributed tracing,
metrics collection, and enhanced logging capabilities.
"""

from .tracing import TracingManager, trace_operation, create_span, initialize_tracing
from .metrics import MetricsManager, record_metric, create_counter, create_histogram, initialize_metrics
from .logging import ObservabilityLogger, create_logger, log_http_request, log_error
from .health import HealthCheckManager, register_health_check

__all__ = [
    'TracingManager',
    'trace_operation',
    'create_span',
    'initialize_tracing',
    'MetricsManager',
    'record_metric',
    'create_counter',
    'create_histogram',
    'initialize_metrics',
    'ObservabilityLogger',
    'create_logger',
    'log_http_request',
    'log_error',
    'HealthCheckManager',
    'register_health_check'
]