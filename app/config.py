"""Configuration module for BetterRepo2File v2.0 with Redis and Celery support"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load .env file if it exists
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
dotenv_path = os.path.join(project_root, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    print(f"Note: .env file not found at {dotenv_path}. Using environment variables.")

class Config:
    """Base configuration"""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-please-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Upload settings
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {
        'txt', 'md', 'py', 'js', 'jsx', 'ts', 'tsx', 'java', 'cpp', 'c', 'h', 
        'hpp', 'cs', 'rb', 'go', 'rs', 'php', 'swift', 'kt', 'scala', 'r',
        'jl', 'lua', 'pl', 'sql', 'sh', 'yaml', 'yml', 'json', 'xml', 'html',
        'css', 'scss', 'sass', 'less', 'vue', 'svelte', 'ipynb'
    }
    
    # Redis configuration
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', '')
    REDIS_URL = os.environ.get('REDIS_URL', f'redis://:{REDIS_PASSWORD}@localhost:6379/0' if REDIS_PASSWORD else 'redis://localhost:6379/0')
    
    # Flask-Session configuration
    SESSION_TYPE = 'redis'
    SESSION_REDIS = None  # Will be set in create_app
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'betterrepo2file:session:'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Celery configuration
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', REDIS_URL)
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', REDIS_URL)
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'UTC'
    CELERY_ENABLE_UTC = True
    CELERY_TASK_TRACK_STARTED = True
    CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
    CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes
    CELERY_WORKER_PREFETCH_MULTIPLIER = 1
    CELERY_WORKER_MAX_TASKS_PER_CHILD = 50
    
    # MinIO/S3 configuration
    MINIO_ENDPOINT = os.environ.get('MINIO_ENDPOINT', 'localhost:9000')
    MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY', 'minioadmin')
    MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY', 'minioadmin')
    MINIO_SECURE = os.environ.get('MINIO_SECURE', 'false').lower() == 'true'
    MINIO_BUCKET_NAME = os.environ.get('MINIO_BUCKET_NAME', 'betterrepo2file')
    
    # Presigned URL settings
    PRESIGNED_URL_EXPIRATION = int(os.environ.get('PRESIGNED_URL_EXPIRATION', '3600'))  # 1 hour default
    
    # OpenTelemetry configuration
    OTEL_SERVICE_NAME = os.environ.get('OTEL_SERVICE_NAME', 'betterrepo2file')
    OTEL_EXPORTER_OTLP_ENDPOINT = os.environ.get('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://localhost:4317')
    OTEL_EXPORTER_OTLP_INSECURE = os.environ.get('OTEL_EXPORTER_OTLP_INSECURE', 'true').lower() == 'true'
    
    # Job processing settings
    JOB_CLEANUP_INTERVAL = 3600  # 1 hour
    JOB_RETENTION_TIME = 3600  # Keep job data for 1 hour
    
    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }
    
    # Profiles configuration
    PROFILES_FILE = 'profiles.yml'
    PROFILES_DIR = 'profiles'
    
    # Git analysis settings
    GIT_DIFF_CONTEXT_LINES = 3
    GIT_MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB
    
    # LLM settings
    LLM_DEFAULT_PROVIDER = os.environ.get('LLM_DEFAULT_PROVIDER', 'gemini')
    LLM_DEFAULT_MODEL = os.environ.get('LLM_DEFAULT_MODEL', 'gemini-1.5-pro')
    LLM_TIMEOUT = 30  # seconds
    LLM_MAX_RETRIES = 3
    
    # Cache settings
    CACHE_TYPE = 'redis'
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    CACHE_KEY_PREFIX = 'betterrepo2file:cache:'
    
    # Default profile for UI
    DEFAULT_PROFILE = os.environ.get('DEFAULT_PROFILE', 'frontend')
    
    # Observability Configuration
    OTEL_ENABLED = os.environ.get('OTEL_ENABLED', 'false').lower() == 'true'
    OTEL_COLLECTOR_ENDPOINT = os.environ.get('OTEL_COLLECTOR_ENDPOINT', 'localhost:4317')
    OTEL_INSECURE_ENDPOINT = os.environ.get('OTEL_INSECURE_ENDPOINT', 'true').lower() == 'true'
    
    # Application Version
    VERSION = '2.0.0'
    
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'
    
class ProductionConfig(Config):
    """Production configuration"""
    FLASK_ENV = 'production'
    SESSION_COOKIE_SECURE = True
    
    # Override with production values from environment
    SECRET_KEY = os.environ.get('SECRET_KEY', Config.SECRET_KEY)
    
    @classmethod
    def init_app(cls, app):
        """Validate production configuration"""
        if not cls.SECRET_KEY or cls.SECRET_KEY == 'dev-secret-key-please-change-in-production':
            raise ValueError("SECRET_KEY environment variable must be set to a secure value in production")
    
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    WTF_CSRF_ENABLED = False
    
    # Use in-memory SQLite for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Use separate Redis database for tests
    REDIS_URL = 'redis://localhost:6379/15'
    SESSION_TYPE = 'filesystem'  # Don't use Redis for unit tests
    

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])