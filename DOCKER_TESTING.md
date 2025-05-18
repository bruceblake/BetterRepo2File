# Running Tests with Docker

This guide explains how to run the BetterRepo2File test suite using Docker.

## Prerequisites

- Docker installed and running
- Docker Compose installed
- For WSL users: Ensure Docker Desktop is running and WSL integration is enabled

## Running Tests

### Quick Start

Run all tests once:
```bash
docker-compose --profile test up --build
```

### Individual Test Commands

1. **Build the test image:**
   ```bash
   docker-compose build test
   ```

2. **Run all tests:**
   ```bash
   docker-compose run --rm test
   ```

3. **Run specific test files:**
   ```bash
   # Python tests only
   docker-compose run --rm test python -m pytest tests/test_app.py -v

   # JavaScript tests only
   docker-compose run --rm test bash -c "cd tests && npm test"
   ```

4. **Run tests with coverage:**
   ```bash
   docker-compose run --rm test
   ```
   Coverage reports will be saved to `./test_results/`

## Test Results

After running tests, you can find:
- Python coverage report: `./test_results/python_coverage/index.html`
- JavaScript coverage report: `./test_results/js_coverage/index.html`

## Running Tests with Docker Socket (for Docker-based tests)

If you need to run tests that interact with Docker:
```bash
docker-compose --profile test-docker up --build
```

## Development Workflow

1. **Run the application:**
   ```bash
   docker-compose up app
   ```

2. **Run tests in another terminal:**
   ```bash
   docker-compose run --rm test
   ```

3. **View test results:**
   ```bash
   # Open coverage reports
   open test_results/python_coverage/index.html
   open test_results/js_coverage/index.html
   ```

## Troubleshooting

### Permission Issues (WSL)
If you encounter permission issues in WSL:
```bash
# Fix Docker socket permissions
sudo chmod 666 /var/run/docker.sock

# Or run with sudo
sudo docker-compose run --rm test
```

### Port Conflicts
If port 5000 is already in use:
```bash
# Stop the conflicting service or change the port in docker-compose.yml
docker-compose down
docker-compose up app
```

### Test Failures
If tests fail, check:
1. All dependencies are installed (check Dockerfile)
2. Test files have correct permissions
3. Docker has enough resources allocated

## Continuous Integration

You can integrate these Docker tests into your CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
name: Run Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: docker-compose --profile test up --build --exit-code-from test
```

## Clean Up

To remove test containers and volumes:
```bash
docker-compose down -v
docker system prune -af
```