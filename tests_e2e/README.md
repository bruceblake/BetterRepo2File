# RobustRepo E2E Tests

This directory contains end-to-end tests for RobustRepo using Playwright and pytest.

## Setup

### Running Tests with Docker (Recommended)

1. Make sure all services are running:
   ```bash
   docker-compose up -d
   ```

2. Run the E2E tests:
   ```bash
   docker-compose --profile e2e up e2e-tests
   ```

   Or run specific tests:
   ```bash
   docker-compose run --rm e2e-tests pytest tests_e2e/test_basic_workflow.py::test_homepage_loads
   ```

### Running Tests Locally

1. Install dependencies:
   ```bash
   pip install -r requirements-test.txt
   playwright install chromium firefox
   ```

2. Set environment variables:
   ```bash
   export BASE_URL=http://localhost:5000
   export HEADLESS=false  # for headed mode
   ```

3. Run tests:
   ```bash
   pytest tests_e2e/
   ```

## Test Structure

```
tests_e2e/
├── conftest.py                 # Pytest fixtures and configuration
├── page_objects/              # Page Object Model classes
│   ├── home_page.py          # Home page interactions
│   └── vibe_coder_page.py    # Vibe Coder workflow page
├── test_basic_workflow.py     # Basic functionality tests
├── test_vibe_coder_workflow.py # Vibe Coder specific tests
└── test_api_endpoints.py      # API endpoint tests
```

## Writing Tests

### Page Object Model

We use the Page Object Model pattern for maintainability:

```python
from page_objects.home_page import HomePage

def test_example(page, base_url):
    home = HomePage(page)
    home.navigate(base_url)
    home.submit_github_repo("https://github.com/user/repo")
    assert home.get_job_status() == "SUCCESS"
```

### Test Markers

- `@pytest.mark.smoke` - Quick smoke tests (< 30s)
- `@pytest.mark.integration` - Integration tests requiring multiple services
- `@pytest.mark.slow` - Slow tests (> 30s)
- `@pytest.mark.api` - API-focused tests
- `@pytest.mark.ui` - UI-focused tests

Run specific markers:
```bash
pytest -m smoke
pytest -m "not slow"
```

## Debugging

### Headed Mode

Run tests with browser visible:
```bash
HEADLESS=false pytest tests_e2e/
```

Or in Docker:
```bash
PLAYWRIGHT_HEADLESS=false docker-compose --profile e2e up e2e-tests
```

### Playwright Inspector

Enable the Playwright Inspector:
```bash
PWDEBUG=1 pytest tests_e2e/test_basic_workflow.py::test_homepage_loads
```

### Traces

Traces are automatically captured on failure. View them:
```bash
playwright show-trace traces/trace.zip
```

### Screenshots and Videos

Screenshots and videos are saved on failure in the `test-results/` directory.

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Run E2E Tests
  run: |
    docker-compose up -d
    docker-compose --profile e2e run e2e-tests
  env:
    CI: true
    PLAYWRIGHT_HEADLESS: true
```

### Environment Variables

- `BASE_URL` - Application URL (default: http://localhost:5000)
- `HEADLESS` - Run in headless mode (default: true)
- `CI` - Set to true in CI environments
- `PLAYWRIGHT_HEADLESS` - Playwright headless mode

## Troubleshooting

### Common Issues

1. **Tests timeout waiting for app**
   - Ensure the app service has a health check
   - Increase wait timeout in `wait-for-app.sh`

2. **Browser fails to launch in Docker**
   - Make sure Playwright browsers are installed with dependencies
   - Check Docker has enough memory allocated

3. **CORS errors in API tests**
   - Verify CORS is properly configured in the Flask app
   - Check the API endpoints accept the test origin

### Logs

View test logs:
```bash
docker-compose logs e2e-tests
```

View application logs during tests:
```bash
docker-compose logs app
```

## Best Practices

1. **Use Page Objects** - Encapsulate page interactions
2. **Keep Tests Independent** - Each test should be runnable in isolation
3. **Use Fixtures** - Share common setup with pytest fixtures
4. **Wait Smartly** - Use Playwright's built-in wait methods
5. **Test Data Cleanup** - Clean up test data after tests
6. **Meaningful Assertions** - Include error messages in assertions
7. **Parallel Execution** - Design tests to run in parallel when possible