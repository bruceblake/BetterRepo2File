# Observability in RobustRepo

RobustRepo v2.0 includes comprehensive observability features using OpenTelemetry for distributed tracing, metrics collection, and enhanced logging.

## Components

### 1. Distributed Tracing

- Request tracing across all services
- Automatic instrumentation for Flask, Celery, Redis, and HTTP requests
- Span creation for custom operations
- Error tracking and exception recording

### 2. Metrics Collection

- Request metrics (count, duration, errors)
- Job processing metrics
- LLM usage metrics (tokens, costs)
- Storage operation metrics
- System metrics (CPU, memory, disk)

### 3. Structured Logging

- JSON-formatted logs with contextual information
- Request ID tracking
- Error stack traces
- Operation timing

### 4. Health Checks

- Component health monitoring (Redis, MinIO, Celery)
- System resource monitoring
- Kubernetes liveness/readiness probes
- Detailed health status endpoints

## Configuration

### Environment Variables

```bash
# Enable OpenTelemetry
OTEL_ENABLED=true

# OpenTelemetry Collector endpoint
OTEL_COLLECTOR_ENDPOINT=localhost:4317

# Use insecure connection (for development)
OTEL_INSECURE_ENDPOINT=true

# Service name
OTEL_SERVICE_NAME=robustrepo
```

### Health Check Endpoints

- `/health/` - Overall health status
- `/health/live` - Kubernetes liveness check
- `/health/ready` - Kubernetes readiness check
- `/health/detailed` - Detailed component status
- `/health/check/<name>` - Specific component check

## Usage Examples

### Custom Tracing

```python
from app.observability import trace_operation, create_span

# Using decorator
@trace_operation(name="custom.operation")
def my_function():
    # Function logic here
    pass

# Using context manager
with create_span("custom.span") as span:
    span.set_attribute("custom.attribute", "value")
    # Operation logic here
```

### Recording Metrics

```python
from app.observability import record_metric, timed_operation

# Record a counter
record_metric("custom.counter", 1, {"tag": "value"})

# Time an operation
with timed_operation("operation.duration"):
    # Operation logic here
```

### Structured Logging

```python
from app.observability import create_logger

logger = create_logger("my.component")

logger.info("Operation completed", 
    operation="process_data",
    duration_ms=150,
    records_processed=1000
)

logger.error("Operation failed", 
    error=exception,
    operation="process_data"
)
```

## Monitoring Setup

### Local Development

1. Run OpenTelemetry Collector:
```bash
docker run -p 4317:4317 -p 4318:4318 \
  otel/opentelemetry-collector-contrib:latest
```

2. View metrics and traces in console output

### Production

1. Deploy OpenTelemetry Collector
2. Configure backend (Jaeger, Prometheus, etc.)
3. Set OTEL_ENABLED=true
4. Configure OTEL_COLLECTOR_ENDPOINT

## Best Practices

1. **Trace Important Operations**: Add custom spans for critical business logic
2. **Record Business Metrics**: Track application-specific metrics
3. **Use Structured Logging**: Include relevant context in all logs
4. **Monitor Health Checks**: Set up alerts for health check failures
5. **Sample Traces**: Configure sampling in production to reduce overhead

## Troubleshooting

### No Traces Appearing

1. Check OTEL_ENABLED is set to true
2. Verify collector endpoint is reachable
3. Check for instrumentation errors in logs

### High Memory Usage

1. Configure trace sampling
2. Reduce metric collection frequency
3. Set span limits

### Health Check Failures

1. Check component logs
2. Verify network connectivity
3. Check resource limits
