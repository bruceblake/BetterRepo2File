"""Enhanced logging with OpenTelemetry integration."""
import logging
import json
import sys
from typing import Any, Dict, Optional
from datetime import datetime

from opentelemetry.instrumentation.logging import LoggingInstrumentor
from pythonjsonlogger import jsonlogger


class ObservabilityLogger:
    """Enhanced logger with structured logging and OpenTelemetry integration."""
    
    def __init__(self, name: str, level: int = logging.INFO):
        """Initialize the observability logger."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False
        
        # Remove existing handlers
        self.logger.handlers = []
        
        # Create JSON formatter
        formatter = jsonlogger.JsonFormatter(
            fmt='%(timestamp)s %(level)s %(name)s %(message)s',
            rename_fields={
                'levelname': 'level',
                'name': 'logger'
            }
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Instrument logging for OpenTelemetry
        LoggingInstrumentor().instrument(set_logging_format=True)
    
    def _add_context(self, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Add standard context to log entries."""
        context = {
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'robustrepo',
            'environment': 'production',  # Could be dynamic
        }
        
        if extra:
            context.update(extra)
        
        return context
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        extra = self._add_context(kwargs)
        self.logger.debug(message, extra=extra)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        extra = self._add_context(kwargs)
        self.logger.info(message, extra=extra)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        extra = self._add_context(kwargs)
        self.logger.warning(message, extra=extra)
    
    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log error message."""
        extra = self._add_context(kwargs)
        
        if error:
            extra['error_type'] = type(error).__name__
            extra['error_message'] = str(error)
            extra['error_stacktrace'] = str(error.__traceback__)
        
        self.logger.error(message, extra=extra)
    
    def critical(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log critical message."""
        extra = self._add_context(kwargs)
        
        if error:
            extra['error_type'] = type(error).__name__
            extra['error_message'] = str(error)
            extra['error_stacktrace'] = str(error.__traceback__)
        
        self.logger.critical(message, extra=extra)
    
    def log_operation(
        self,
        operation: str,
        status: str,
        duration_ms: Optional[float] = None,
        **kwargs
    ):
        """Log an operation with standard fields."""
        extra = {
            'operation': operation,
            'status': status,
            **kwargs
        }
        
        if duration_ms is not None:
            extra['duration_ms'] = duration_ms
        
        level = logging.INFO if status == 'success' else logging.ERROR
        message = f"Operation {operation} completed with status {status}"
        
        if level == logging.INFO:
            self.info(message, **extra)
        else:
            self.error(message, **extra)
    
    def log_http_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        **kwargs
    ):
        """Log HTTP request details."""
        extra = {
            'http_method': method,
            'http_path': path,
            'http_status_code': status_code,
            'duration_ms': duration_ms,
            **kwargs
        }
        
        message = f"{method} {path} - {status_code}"
        self.info(message, **extra)
    
    def log_job(
        self,
        job_id: str,
        job_type: str,
        status: str,
        duration_s: Optional[float] = None,
        **kwargs
    ):
        """Log job processing details."""
        extra = {
            'job_id': job_id,
            'job_type': job_type,
            'job_status': status,
            **kwargs
        }
        
        if duration_s is not None:
            extra['duration_s'] = duration_s
        
        message = f"Job {job_id} ({job_type}) - {status}"
        
        if status in ('completed', 'success'):
            self.info(message, **extra)
        else:
            self.error(message, **extra)
    
    def log_llm_operation(
        self,
        operation_type: str,
        model: str,
        tokens_used: Optional[int] = None,
        cost: Optional[float] = None,
        **kwargs
    ):
        """Log LLM operation details."""
        extra = {
            'llm_operation': operation_type,
            'llm_model': model,
            **kwargs
        }
        
        if tokens_used is not None:
            extra['llm_tokens_used'] = tokens_used
        
        if cost is not None:
            extra['llm_cost'] = cost
        
        message = f"LLM operation {operation_type} with {model}"
        self.info(message, **extra)


# Factory function for creating loggers
def create_logger(name: str, level: int = logging.INFO) -> ObservabilityLogger:
    """Create an observability logger."""
    return ObservabilityLogger(name, level)


# Pre-configured loggers for different components
app_logger = create_logger('robustrepo.app')
api_logger = create_logger('robustrepo.api')
job_logger = create_logger('robustrepo.jobs')
llm_logger = create_logger('robustrepo.llm')
storage_logger = create_logger('robustrepo.storage')


# Convenience logging functions
def log_error(message: str, error: Exception, **kwargs):
    """Log an error with the app logger."""
    app_logger.error(message, error=error, **kwargs)


def log_operation(operation: str, status: str, **kwargs):
    """Log an operation with the app logger."""
    app_logger.log_operation(operation, status, **kwargs)


def log_http_request(method: str, path: str, status_code: int, duration_ms: float, **kwargs):
    """Log an HTTP request with the API logger."""
    api_logger.log_http_request(method, path, status_code, duration_ms, **kwargs)


def log_job(job_id: str, job_type: str, status: str, **kwargs):
    """Log a job with the job logger."""
    job_logger.log_job(job_id, job_type, status, **kwargs)


def log_llm_operation(operation_type: str, model: str, **kwargs):
    """Log an LLM operation with the LLM logger."""
    llm_logger.log_llm_operation(operation_type, model, **kwargs)