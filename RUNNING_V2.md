# Running BetterRepo2File v2.0 - RobustRepo

This guide explains how to run the new v2.0 architecture with Flask application factory pattern, Celery for async processing, and distributed storage.

## Quick Start

### 1. Using Docker Compose (Recommended)

```bash
# Copy environment variables
cp .env.example .env
# Edit .env with your configuration

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

The application will be available at:
- Main application: http://localhost:5000
- MinIO console: http://localhost:9001 (login: minioadmin/minioadmin)
- Flower (Celery monitoring): http://localhost:5555

### 2. Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_APP=run.py
export FLASK_ENV=development
export REDIS_URL=redis://localhost:6379/0
# ... (set other variables from .env.example)

# Run the application
flask run
# OR
python run.py
```

### 3. Running Individual Services

#### Redis
```bash
docker run -d -p 6379:6379 redis:7-alpine redis-server --requirepass changeme
```

#### MinIO
```bash
docker run -d \
  -p 9000:9000 \
  -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  minio/minio server /data --console-address ":9001"
```

#### Celery Worker
```bash
celery -A app.celery_app worker --loglevel=info
```

#### Celery Flower (Monitoring)
```bash
celery -A app.celery_app flower
```

## Architecture Changes

### Application Factory Pattern
The application now uses the Flask application factory pattern:
- `app/__init__.py`: Contains `create_app()` function
- `run.py`: Entry point for running the application

### Blueprints Structure
Routes are organized into blueprints:
- `app/routes/ui_routes.py`: UI endpoints
- `app/routes/job_api_routes.py`: Internal API for job processing
- `app/routes/v1_api_routes.py`: Public API v1
- `app/routes/profile_routes.py`: Profile management

### Async Processing
All repository processing now happens asynchronously:
- Jobs are submitted to Celery
- Status updates via Server-Sent Events (SSE)
- Results stored in MinIO
- Presigned URLs for file downloads

## API Changes

### Process Endpoint
- Old: `/process` (synchronous)
- New: `/api/process` (returns job_id immediately)

### Status Tracking
- New endpoint: `/api/job_status/<job_id>` (SSE)
- Returns real-time progress updates

### Results
- New endpoint: `/api/result/<job_id>`
- Returns presigned URLs for downloading results

## Environment Variables

Key environment variables (see `.env.example` for full list):
- `FLASK_APP=run.py`
- `FLASK_ENV=development`
- `REDIS_URL=redis://:password@host:port/db`
- `MINIO_ENDPOINT=host:port`
- `MINIO_ACCESS_KEY` and `MINIO_SECRET_KEY`

## Troubleshooting

### ImportError: attempted relative import with no known parent package
Make sure to run the application using:
```bash
flask run
# OR
python run.py
```

Not directly with `python app/app.py`

### Redis Connection Errors
Ensure Redis is running and the password matches your configuration.

### MinIO Connection Errors
Check that MinIO is running and credentials are correct.

### Celery Worker Not Processing
- Check worker logs: `docker-compose logs celery`
- Ensure Redis is accessible
- Verify task routing in Celery configuration

## Development vs Production

### Development
```bash
export FLASK_ENV=development
flask run --debug
```

### Production
```bash
export FLASK_ENV=production
export SECRET_KEY=<secure-random-key>
export SESSION_COOKIE_SECURE=true
gunicorn "app:create_app()" --workers 4 --bind 0.0.0.0:5000
```

## Testing

```bash
# Run all tests
docker-compose run --rm test

# Run specific tests
pytest tests/test_app.py -v
```