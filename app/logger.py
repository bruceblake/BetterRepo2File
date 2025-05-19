import logging
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import sys


def setup_logging(app):
    """Configure application logging for production use"""
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('app.log')
        ]
    )
    
    # Configure app logger
    app.logger.setLevel(logging.INFO)
    
    # Add structured logging for production
    if not app.debug:
        try:
            from pythonjsonlogger import jsonlogger
            
            # JSON formatter for structured logging
            json_formatter = jsonlogger.JsonFormatter()
            
            # File handler for JSON logs
            json_handler = logging.FileHandler('app_json.log')
            json_handler.setFormatter(json_formatter)
            
            app.logger.addHandler(json_handler)
        except ImportError:
            # pythonjsonlogger not installed, use standard logging
            app.logger.warning("pythonjsonlogger not installed, using standard logging format")
    
    # Reduce noise from libraries
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    return app.logger

class IterationLogger:
    """Enhanced logger for iteration workflows with detailed output and metrics"""
    
    def __init__(self, name: str = 'BetterRepo2File', log_dir: str = 'logs'):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.log_queues = []
        
        # Create different log files for different purposes
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.main_log = self.log_dir / f'main_{self.session_id}.log'
        self.metrics_log = self.log_dir / f'metrics_{self.session_id}.json'
        self.iteration_log = self.log_dir / f'iteration_{self.session_id}.log'
        
        # Set up formatters
        self.detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        self.simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Set up main logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Console handler with color coding
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(ColoredFormatter())
        self.logger.addHandler(console_handler)
        
        # File handler for detailed logs
        file_handler = logging.FileHandler(self.main_log)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self.detailed_formatter)
        self.logger.addHandler(file_handler)
        
        # Iteration logger for tracking workflow progress
        self.iteration_logger = logging.getLogger(f'{name}.iteration')
        iteration_handler = logging.FileHandler(self.iteration_log)
        iteration_handler.setFormatter(self.simple_formatter)
        self.iteration_logger.addHandler(iteration_handler)
        self.iteration_logger.setLevel(logging.INFO)
        
        # Metrics tracking
        self.metrics = {
            'session_id': self.session_id,
            'start_time': datetime.now().isoformat(),
            'iterations': [],
            'errors': [],
            'performance': {}
        }
        
        self.current_iteration = None
    
    def start_iteration(self, iteration_id: str, description: str = ''):
        """Start tracking a new iteration"""
        self.current_iteration = {
            'id': iteration_id,
            'description': description,
            'start_time': time.time(),
            'steps': [],
            'errors': [],
            'metrics': {}
        }
        self.iteration_logger.info(f"=== Starting Iteration: {iteration_id} ===")
        self.iteration_logger.info(f"Description: {description}")
        self.logger.info(f"Starting iteration: {iteration_id}")
    
    def log_step(self, step: str, details: Optional[Dict[str, Any]] = None):
        """Log a step within the current iteration"""
        if self.current_iteration:
            step_data = {
                'step': step,
                'timestamp': time.time(),
                'details': details or {}
            }
            self.current_iteration['steps'].append(step_data)
            self.iteration_logger.info(f"Step: {step}")
            if details:
                self.iteration_logger.info(f"Details: {json.dumps(details, indent=2)}")
            self.logger.debug(f"Iteration step: {step} - {details}")
            
            # Send to queues
            log_entry = {
                'type': 'step',
                'level': 'INFO',
                'message': step,
                'details': details,
                'timestamp': datetime.now().isoformat(),
                'iteration_id': self.current_iteration.get('id')
            }
            self._send_to_queues(log_entry)
    
    def log_error(self, error: str, exception: Optional[Exception] = None):
        """Log an error within the current iteration"""
        error_data = {
            'error': error,
            'timestamp': time.time(),
            'exception': str(exception) if exception else None,
            'traceback': None
        }
        
        if exception:
            import traceback
            error_data['traceback'] = traceback.format_exc()
        
        if self.current_iteration:
            self.current_iteration['errors'].append(error_data)
        
        self.metrics['errors'].append(error_data)
        self.iteration_logger.error(f"Error: {error}")
        if exception:
            self.iteration_logger.error(f"Exception: {exception}")
        self.logger.error(f"Error in iteration: {error}", exc_info=exception)
        
        # Send to queues
        log_entry = {
            'type': 'error',
            'level': 'ERROR',
            'message': error,
            'exception': str(exception) if exception else None,
            'traceback': error_data.get('traceback'),
            'timestamp': datetime.now().isoformat(),
            'iteration_id': self.current_iteration.get('id') if self.current_iteration else None
        }
        self._send_to_queues(log_entry)
    
    def log_metric(self, metric_name: str, value: Any):
        """Log a metric for the current iteration"""
        if self.current_iteration:
            self.current_iteration['metrics'][metric_name] = value
        self.metrics['performance'][metric_name] = value
        self.iteration_logger.info(f"Metric: {metric_name} = {value}")
        self.logger.info(f"Metric {metric_name}: {value}")
        
        # Send to queues
        log_entry = {
            'type': 'metric',
            'level': 'INFO',
            'message': f'{metric_name}: {value}',
            'metric_name': metric_name,
            'metric_value': value,
            'timestamp': datetime.now().isoformat(),
            'iteration_id': self.current_iteration.get('id') if self.current_iteration else None
        }
        self._send_to_queues(log_entry)
    
    def end_iteration(self, status: str = 'completed'):
        """End the current iteration and save metrics"""
        if self.current_iteration:
            self.current_iteration['end_time'] = time.time()
            self.current_iteration['duration'] = (
                self.current_iteration['end_time'] - 
                self.current_iteration['start_time']
            )
            self.current_iteration['status'] = status
            
            self.metrics['iterations'].append(self.current_iteration)
            
            self.iteration_logger.info(f"=== Iteration Complete: {self.current_iteration['id']} ===")
            self.iteration_logger.info(f"Status: {status}")
            self.iteration_logger.info(f"Duration: {self.current_iteration['duration']:.2f}s")
            self.logger.info(f"Completed iteration: {self.current_iteration['id']} - {status}")
            
            # Save metrics
            self.save_metrics()
            
            self.current_iteration = None
    
    def save_metrics(self):
        """Save metrics to JSON file"""
        self.metrics['last_updated'] = datetime.now().isoformat()
        with open(self.metrics_log, 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def get_session_logs(self) -> Dict[str, Any]:
        """Get all logs for the current session"""
        return {
            'session_id': self.session_id,
            'metrics': self.metrics,
            'log_files': {
                'main': str(self.main_log),
                'iteration': str(self.iteration_log),
                'metrics': str(self.metrics_log)
            }
        }
    
    def add_queue(self, queue):
        """Add a queue for real-time log streaming"""
        self.log_queues.append(queue)
    
    def remove_queue(self, queue):
        """Remove a queue from log streaming"""
        if queue in self.log_queues:
            self.log_queues.remove(queue)
    
    def _send_to_queues(self, log_entry: Dict[str, Any]):
        """Send log entry to all registered queues"""
        for queue in self.log_queues:
            try:
                queue.put(log_entry)
            except:
                pass  # Ignore queue errors


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color coding for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        record.msg = f"{log_color}{record.msg}{self.RESET}"
        return super().format(record)


# Global logger instance
iteration_logger = IterationLogger()

# Module-level logger for direct import
logger = logging.getLogger('betterrepo2file.app')
logger.setLevel(logging.INFO)

# Add console handler if not already configured
if not logger.handlers:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logger.addHandler(console_handler)

# Convenience functions
def log_iteration_start(iteration_id: str, description: str = ''):
    iteration_logger.start_iteration(iteration_id, description)

def log_step(step: str, details: Optional[Dict[str, Any]] = None):
    iteration_logger.log_step(step, details)

def log_error(error: str, exception: Optional[Exception] = None):
    iteration_logger.log_error(error, exception)

def log_metric(metric_name: str, value: Any):
    iteration_logger.log_metric(metric_name, value)

def log_iteration_end(status: str = 'completed'):
    iteration_logger.end_iteration(status)

def get_logger():
    return iteration_logger.logger