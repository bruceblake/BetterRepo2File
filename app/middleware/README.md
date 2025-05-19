# RobustRepo Middleware

This directory contains Flask middleware components for the RobustRepo application.

## Components

### ObservabilityMiddleware
- Request tracking and timing
- Automatic span creation for distributed tracing
- Request/response logging with structured data
- Metric collection for request performance
- Request ID generation and tracking

### ErrorHandlerMiddleware
- Consistent JSON error responses across the application
- Different handlers for HTTP exceptions vs unexpected errors
- Integration with the observability system for error tracking
- Debug mode support with detailed error information
- Request ID correlation for error tracking

## Usage

Both middleware components are automatically initialized in the application factory (`app/__init__.py`):

```python
from app.middleware import ObservabilityMiddleware, ErrorHandlerMiddleware

# In create_app():
ObservabilityMiddleware(app)
ErrorHandlerMiddleware(app)
```

The middleware work together to provide comprehensive request tracking and error handling:

1. ObservabilityMiddleware tracks the request lifecycle
2. ErrorHandlerMiddleware catches any errors and formats them consistently
3. Both integrate with the logging and metrics systems
4. Request IDs are maintained throughout for correlation

## Architecture

The middleware follows Flask's standard patterns:
- Initialization with the Flask app
- Registration of handlers using Flask's hooks
- Integration with the broader observability framework
- Consistent error response format for API consumers