"""Error handling middleware for RobustRepo."""
import logging
import traceback
from typing import Any, Dict
from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException

from app.observability import log_error, create_span, record_metric
from app.logger import logger


class ErrorHandlerMiddleware:
    """Middleware for handling errors in a consistent manner."""
    
    def __init__(self, app: Flask = None):
        """Initialize the error handler middleware."""
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize the middleware with the Flask app."""
        self.app = app
        
        # Register error handlers
        app.register_error_handler(Exception, self._handle_error)
        app.register_error_handler(404, self._handle_404)
        app.register_error_handler(500, self._handle_500)
    
    def _handle_error(self, error: Exception) -> tuple:
        """Handle all errors in a consistent manner."""
        # Determine if this is an HTTP exception
        if isinstance(error, HTTPException):
            return self._handle_http_exception(error)
        
        # Handle unexpected errors
        return self._handle_unexpected_error(error)
    
    def _handle_http_exception(self, error: HTTPException) -> tuple:
        """Handle HTTP exceptions."""
        # Log the error
        log_error(
            f"HTTP Error: {error.code} - {error.name}",
            error,
            path=request.path,
            method=request.method,
            status_code=error.code
        )
        
        # Record metric
        record_metric(
            "robustrepo.errors.http",
            1,
            {
                "status_code": error.code,
                "method": request.method,
                "path": request.path
            }
        )
        
        # Create response
        response = {
            "error": {
                "code": error.code,
                "name": error.name,
                "description": error.description,
            }
        }
        
        # Add request ID if available
        if hasattr(request, 'request_id'):
            response["request_id"] = request.request_id
        
        return jsonify(response), error.code
    
    def _handle_unexpected_error(self, error: Exception) -> tuple:
        """Handle unexpected errors."""
        # Log the full error with traceback
        logger.error(
            f"Unexpected error: {type(error).__name__}: {str(error)}",
            exc_info=True
        )
        
        log_error(
            "Internal server error",
            error,
            path=request.path,
            method=request.method,
            error_type=type(error).__name__
        )
        
        # Record metric
        record_metric(
            "robustrepo.errors.unexpected",
            1,
            {
                "error_type": type(error).__name__,
                "method": request.method,
                "path": request.path
            }
        )
        
        # Create error response
        response = {
            "error": {
                "code": 500,
                "name": "Internal Server Error",
                "description": "An unexpected error occurred",
                "type": type(error).__name__
            }
        }
        
        # Add request ID if available
        if hasattr(request, 'request_id'):
            response["request_id"] = request.request_id
        
        # In debug mode, add the error message and traceback
        if self.app.debug:
            response["error"]["message"] = str(error)
            response["error"]["traceback"] = traceback.format_exc()
        
        return jsonify(response), 500
    
    def _handle_404(self, error: HTTPException) -> tuple:
        """Handle 404 Not Found errors."""
        response = {
            "error": {
                "code": 404,
                "name": "Not Found",
                "description": "The requested resource was not found",
                "path": request.path
            }
        }
        
        if hasattr(request, 'request_id'):
            response["request_id"] = request.request_id
        
        return jsonify(response), 404
    
    def _handle_500(self, error: HTTPException) -> tuple:
        """Handle 500 Internal Server errors."""
        response = {
            "error": {
                "code": 500,
                "name": "Internal Server Error",
                "description": "The server encountered an internal error"
            }
        }
        
        if hasattr(request, 'request_id'):
            response["request_id"] = request.request_id
        
        return jsonify(response), 500
    
    def handle_validation_error(self, error: Dict[str, Any]) -> tuple:
        """Handle validation errors specifically."""
        response = {
            "error": {
                "code": 400,
                "name": "Validation Error",
                "description": "The request contains invalid data",
                "fields": error
            }
        }
        
        if hasattr(request, 'request_id'):
            response["request_id"] = request.request_id
        
        return jsonify(response), 400