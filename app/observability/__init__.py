# Observability Package for RobustRepo
"""
Provides OpenTelemetry instrumentation for distributed tracing,
metrics collection, and enhanced logging capabilities.
"""

from .tracing import TracingManager, trace_operation, create_span
from .metrics import MetricsManager, record_metric, create_counter, create_histogram
from .logging import ObservabilityLogger, create_logger
from .health import HealthCheckManager, register_health_check

__all__ = [
    'TracingManager',
    'trace_operation',
    'create_span',
    'MetricsManager',
    'record_metric',
    'create_counter',
    'create_histogram',
    'ObservabilityLogger',
    'create_logger',
    'HealthCheckManager',
    'register_health_check'
]