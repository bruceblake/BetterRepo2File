# Phase 1: Redis and Session Management Implementation

This document describes the implementation of Phase 1 of BetterRepo2File v2.0 "RobustRepo", which introduces Redis-based session management and prepares the infrastructure for distributed processing.

## Components Implemented

### 1. Configuration Module (`app/config.py`)
- Central configuration management using environment variables
- Support for multiple environments (development, production, testing)
- Configuration for Redis, Celery, MinIO, and other services

### 2. Session Manager (`app/session_manager.py`)
- Redis-backed session management
- Session creation, retrieval, update, and deletion
- TTL-based session expiration
- Integration with Flask-Session

### 3. Storage Manager (`app/storage_manager.py`)
- MinIO/S3 object storage integration
- File and directory operations
- JSON data storage support
- Presigned URL generation
- Multipart upload support (placeholder)

### 4. Docker Infrastructure (`docker-compose.yml`)
- Redis service for session storage and Celery broker
- MinIO service for object storage
- Celery worker service (prepared for Phase 2)
- Flower service for Celery monitoring
- Health checks and dependency management

### 5. Test Infrastructure (`tests/test_phase1_integration.py`)
- Integration tests for Redis connectivity
- Session management tests
- MinIO storage tests
- JSON storage and retrieval tests

## Environment Variables

The following environment variables are now supported:

- `REDIS_URL`: Redis connection URL (default: `redis://localhost:6379/0`)
- `CELERY_BROKER_URL`: Celery broker URL (default: same as REDIS_URL)
- `CELERY_RESULT_BACKEND`: Celery result backend URL
- `MINIO_ENDPOINT`: MinIO server endpoint
- `MINIO_ACCESS_KEY`: MinIO access key
- `MINIO_SECRET_KEY`: MinIO secret key
- `MINIO_SECURE`: Whether to use HTTPS for MinIO
- `MINIO_BUCKET_NAME`: Default bucket name

## Usage

### Starting the Infrastructure

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Running Tests

```bash
# Run Phase 1 integration tests
python -m pytest tests/test_phase1_integration.py -v

# Run with Docker
docker-compose run --rm test python -m pytest tests/test_phase1_integration.py -v
```

### Accessing Services

- Flask App: http://localhost:5000
- MinIO Console: http://localhost:9001 (login: minioadmin/minioadmin)
- Flower (Celery monitoring): http://localhost:5555
- Redis: localhost:6379

## Session Management Usage

```python
# Create a session
session_id = session_manager.create_session()

# Store data in session
session_manager.set_session_data(session_id, "user_id", "123")
session_manager.set_session_data(session_id, "repo_url", "https://github.com/user/repo")

# Retrieve data from session
user_id = session_manager.get_session_data(session_id, "user_id")

# Update session data
session_manager.update_session(session_id, {"last_activity": datetime.utcnow()})

# Check if session is active
if session_manager.is_session_active(session_id):
    # Process request
    pass
```

## Storage Management Usage

```python
# Upload a file
storage_manager.upload_file("/path/to/file.txt", "jobs/123/output.txt")

# Upload JSON data
metadata = {"job_id": "123", "status": "complete"}
storage_manager.upload_json(metadata, "jobs/123/metadata.json")

# Download a file
storage_manager.download_file("jobs/123/output.txt", "/tmp/output.txt")

# Generate presigned URL
url = storage_manager.get_file_url("jobs/123/output.txt", expires=3600)

# List objects with prefix
files = storage_manager.list_objects("jobs/123/")
```

## Migration Notes

The following changes need to be considered when migrating from the old system:

1. **Session Storage**: Sessions are now stored in Redis instead of JSON files
2. **File Storage**: Temporary files are now stored in MinIO instead of local filesystem
3. **Configuration**: Configuration is now centralized in `app/config.py`
4. **Imports**: Module imports have been updated to support the new structure

## Next Steps (Phase 2)

The infrastructure is now ready for Phase 2, which will implement:
- Celery task queue for repository processing
- Migration of subprocess calls to Celery tasks
- Job state tracking and result management
- Distributed processing capabilities

## Troubleshooting

### Redis Connection Issues
```bash
# Check Redis connectivity
redis-cli ping

# Check Redis logs
docker-compose logs redis
```

### MinIO Issues
```bash
# Check MinIO status
curl http://localhost:9000/minio/health/live

# View MinIO logs
docker-compose logs minio
```

### Session Issues
- Ensure Redis is running and accessible
- Check Redis memory usage: `redis-cli info memory`
- Verify session TTL settings in configuration

## Security Considerations

1. Change default MinIO credentials in production
2. Use secure Redis passwords in production
3. Enable SSL/TLS for Redis and MinIO in production
4. Set secure cookie flags for sessions
5. Implement proper authentication and authorization

This completes Phase 1 of the BetterRepo2File v2.0 implementation.