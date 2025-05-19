"""Middleware for request tracking and observability."""
import time
import uuid
from flask import Flask, request, g
from werkzeug.exceptions import HTTPException

from app.observability import (
    create_span,
    record_metric,
    log_http_request,
    log_error
)


class ObservabilityMiddleware:
    """Middleware for adding observability to Flask requests."""
    
    def __init__(self, app: Flask = None):
        """Initialize the middleware."""
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize the middleware with the Flask app."""
        self.app = app
        
        # Register before request handler
        app.before_request(self._before_request)
        
        # Register after request handler
        app.after_request(self._after_request)
        
        # Register error handler
        app.errorhandler(Exception)(self._handle_error)
    
    def _before_request(self):
        """Called before each request."""
        # Generate request ID
        g.request_id = str(uuid.uuid4())
        
        # Start timing
        g.start_time = time.time()
        
        # Start span for request
        g.request_span = create_span(
            f"http.request.{request.method}",
            attributes={
                "http.method": request.method,
                "http.url": request.url,
                "http.target": request.path,
                "http.host": request.host,
                "http.scheme": request.scheme,
                "http.user_agent": request.headers.get("User-Agent", ""),
                "request.id": g.request_id,
            }
        ).__enter__()
    
    def _after_request(self, response):
        """Called after each request."""
        # Calculate duration
        duration_ms = (time.time() - g.start_time) * 1000
        
        # End request span
        if hasattr(g, "request_span") and g.request_span:
            g.request_span.set_attribute("http.status_code", response.status_code)
            g.request_span.__exit__(None, None, None)
        
        # Record metrics
        record_metric(
            "robustrepo.requests.total",
            1,
            attributes={
                "http.method": request.method,
                "http.path": request.path,
                "http.status_code": response.status_code,
            }
        )
        
        record_metric(
            "robustrepo.requests.duration",
            duration_ms,
            attributes={
                "http.method": request.method,
                "http.path": request.path,
                "http.status_code": response.status_code,
            }
        )
        
        # Log request
        log_http_request(
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            request_id=g.request_id,
            remote_addr=request.remote_addr,
            user_agent=request.headers.get("User-Agent", "")
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = g.request_id
        
        return response
    
    def _handle_error(self, error):
        """Handle errors during request processing."""
        # Calculate duration
        duration_ms = (time.time() - g.start_time) * 1000 if hasattr(g, "start_time") else 0
        
        # Get status code
        if isinstance(error, HTTPException):
            status_code = error.code
        else:
            status_code = 500
        
        # End request span with error
        if hasattr(g, "request_span") and g.request_span:
            g.request_span.set_attribute("http.status_code", status_code)
            g.request_span.set_attribute("error", True)
            g.request_span.set_attribute("error.type", type(error).__name__)
            g.request_span.set_attribute("error.message", str(error))
            g.request_span.__exit__(type(error), error, error.__traceback__)
        
        # Record error metrics
        record_metric(
            "robustrepo.requests.errors.total",
            1,
            attributes={
                "http.method": request.method,
                "http.path": request.path,
                "http.status_code": status_code,
                "error.type": type(error).__name__,
            }
        )
        
        # Log error
        log_error(
            f"Request failed: {request.method} {request.path}",
            error=error,
            request_id=g.request_id if hasattr(g, "request_id") else None,
            method=request.method,
            path=request.path,
            status_code=status_code,
            duration_ms=duration_ms
        )
        
        # Re-raise for Flask to handle
        raise error