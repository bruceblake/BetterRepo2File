"""
Application factory for BetterRepo2File v2.0 - RobustRepo
"""
import os
from flask import Flask
from flask_cors import CORS
from flask_session import Session
import redis
from .config import Config


def create_app(config_name=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Override with instance config if it exists
    app.config.from_pyfile('config.py', silent=True)
    
    # Override with environment-specific config
    if config_name:
        app.config.from_object(f'app.config.{config_name}')
    
    # Set up Redis connection for Flask-Session
    redis_client = redis.from_url(app.config['REDIS_URL'])
    app.config['SESSION_REDIS'] = redis_client
    
    # Initialize extensions
    CORS(app)
    Session(app)
    
    # Initialize managers (these don't need app context)
    from .session_manager import SessionManager
    from .storage_manager import StorageManager
    from .job_manager import JobManager
    
    app.session_manager = SessionManager()
    app.storage_manager = StorageManager()
    app.job_manager = JobManager()
    
    # Import and register blueprints
    # UI Routes
    from .routes.ui_routes import ui_bp
    app.register_blueprint(ui_bp)
    
    # Job API Routes
    from .routes.job_api_routes import job_api_bp
    app.register_blueprint(job_api_bp)
    
    # Public API v1 Routes
    from .routes.v1_api_routes import api_v1_bp
    app.register_blueprint(api_v1_bp)
    
    # Profile Routes
    from .routes.profile_routes import profile_bp
    app.register_blueprint(profile_bp)
    
    # Iteration Routes
    from .routes.iteration_routes import iteration_bp
    app.register_blueprint(iteration_bp)
    
    # LLM Routes
    from .routes.llm_routes import llm_bp
    app.register_blueprint(llm_bp)
    
    # Health Routes
    from .routes.health_routes import health_bp
    app.register_blueprint(health_bp)
    
    # Set up observability (temporarily disabled to fix logging issues)
    # from .observability import initialize_tracing, initialize_metrics
    # from .middleware.observability_middleware import ObservabilityMiddleware
    
    # # Initialize tracing
    # initialize_tracing(app, service_name="robustrepo", environment=config_name or "development")
    
    # # Initialize metrics
    # initialize_metrics(service_name="robustrepo", environment=config_name or "development")
    
    # # Add observability middleware
    # ObservabilityMiddleware(app)
    
    # Set up logging
    if not app.debug:
        from .logger import setup_logging
        setup_logging(app)
    
    return app