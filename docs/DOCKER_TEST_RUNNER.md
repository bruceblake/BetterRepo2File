# Docker Test Runner for BetterRepo2File

## Overview

BetterRepo2File now includes a Docker-based test runner that provides isolated, reproducible test environments for projects. This feature automatically detects and runs tests using appropriate frameworks inside Docker containers.

## Features

- **Automatic Framework Detection**: Detects and runs tests for Python (pytest), JavaScript (Jest, Mocha), Go, Rust, Java (Maven, Gradle), .NET, and more
- **Isolated Test Environment**: Tests run in clean Docker containers, ensuring no dependency conflicts
- **Comprehensive Test Results**: Detailed test reports with individual test outcomes, durations, and summaries
- **UI Integration**: Seamless integration with the web UI, including Docker availability detection
- **Fallback Support**: Gracefully falls back to local test execution if Docker is unavailable

## Requirements

- Docker installed and running on the host system
- Docker daemon accessible to the application
- Sufficient permissions to create and run Docker containers

## Usage

### Via Web UI

1. Navigate to the test section in the workflow
2. Click "Run Tests"
3. If Docker is available, you'll be prompted to choose between Docker and local execution
4. Test results will display with a Docker indicator if run in a container

### Via API

```bash
# Check Docker availability
curl http://localhost:5000/api/check-docker

# Run tests with Docker
curl -X POST http://localhost:5000/api/run-tests \
  -H "Content-Type: application/json" \
  -d '{
    "repo_path": "/path/to/repo",
    "use_docker": true,
    "framework": "auto"
  }'
```

### Docker Compose

```bash
# Start the application with test runner support
docker-compose up

# Build only the test runner image
docker-compose build test-runner
```

## Supported Test Frameworks

The Docker test runner supports automatic detection and execution of:

- **Python**: pytest, unittest
- **JavaScript/TypeScript**: Jest, Mocha, npm test
- **Go**: go test
- **Rust**: cargo test
- **Java**: Maven (mvn test), Gradle
- **.NET**: dotnet test
- **Make**: make test

## Test Result Format

Test results include:

```json
{
  "docker": true,
  "framework": "pytest",
  "passed": 10,
  "failed": 2,
  "errors": 0,
  "success": false,
  "details": [
    {
      "name": "test_example.py::test_function",
      "outcome": "passed",
      "duration": 0.123
    }
  ],
  "output": "Full test output..."
}
```

## Architecture

The Docker test runner consists of:

1. **Dockerfile**: Multi-stage build with both application and test-runner targets
2. **Test Runner Module**: Python module (`repo2file/test_runner.py`) with Docker integration
3. **Docker Script**: Shell script (`scripts/docker_test_runner.sh`) for framework detection and execution
4. **API Endpoints**: REST endpoints for Docker detection and test execution
5. **UI Components**: JavaScript functions for Docker interaction and result display

## Customization

### Adding New Frameworks

To add support for a new test framework:

1. Update `scripts/docker_test_runner.sh` with detection logic
2. Add framework-specific commands and result parsing
3. Update `test_runner.py` with result parsing logic
4. Add framework to supported list in documentation

### Custom Docker Images

You can extend the test runner Dockerfile to include additional tools:

```dockerfile
FROM betterrepo2file-test-runner:latest as custom-runner

# Add your custom tools
RUN apt-get update && apt-get install -y your-tools

# Add custom test frameworks
RUN pip install your-framework
```

## Troubleshooting

### Docker Not Available

If Docker is not detected:
- Ensure Docker daemon is running: `docker info`
- Check permissions: `docker ps`
- Verify Docker socket access

### Test Execution Failures

- Check container logs: `docker logs <container-id>`
- Verify volume mounts are correct
- Ensure test framework is properly installed in the image

### Performance Issues

- Increase Docker memory allocation
- Use bind mounts for large repositories
- Consider caching test dependencies in the image

## Security Considerations

- Test containers run with read-only repository mounts
- No network access is provided to test containers by default
- Container resources are limited to prevent abuse
- Temporary files are cleaned up after test execution