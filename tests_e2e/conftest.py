"""
Pytest fixtures for E2E tests
"""
import pytest
import os
from typing import Generator
from playwright.sync_api import Playwright, Browser, BrowserContext, Page


@pytest.fixture(scope="session")
def base_url() -> str:
    """Get the base URL from environment or use default."""
    return os.environ.get("BASE_URL", "http://app:5000")


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Configure browser launch arguments for headless mode in Docker."""
    return {
        **browser_type_launch_args,
        "headless": True,  # Run headless in Docker container
        "args": [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-accelerated-2d-canvas",
            "--no-first-run",
            "--no-zygote",
            "--disable-gpu",
        ]
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context with custom settings."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="function")
def authenticated_page(page: Page, base_url: str) -> Page:
    """Provide a page that's already authenticated (if needed)."""
    # For now, just return the page as-is since RobustRepo might not have auth
    # Later, add login logic here if authentication is implemented
    return page


@pytest.fixture(scope="session", autouse=True)
def setup_test_data():
    """Set up any test data needed for the entire test session."""
    # This could include:
    # - Creating test repositories in MinIO
    # - Setting up test GitHub repos
    # - Preparing test files
    yield
    # Cleanup after all tests


@pytest.fixture
def test_github_repo() -> str:
    """Provide a small public GitHub repo for testing."""
    return "https://github.com/octocat/Hello-World"


@pytest.fixture
def test_file_paths() -> dict:
    """Provide paths to test files."""
    test_dir = os.path.dirname(__file__)
    return {
        "small_python": os.path.join(test_dir, "fixtures", "small_project.zip"),
        "single_file": os.path.join(test_dir, "fixtures", "single_file.py"),
        "multi_files": os.path.join(test_dir, "fixtures", "multi_files.zip"),
    }


@pytest.fixture
def wait_for_job_completion(page: Page):
    """Helper to wait for job completion in the UI."""
    def _wait(timeout: int = 60000):
        # Wait for either SUCCESS or FAILURE status to appear
        status_selector = "[data-testid='job-status']"
        page.wait_for_selector(
            f"{status_selector}:has-text('SUCCESS'), {status_selector}:has-text('FAILURE')",
            timeout=timeout
        )
        return page.locator(status_selector).inner_text()
    return _wait


@pytest.fixture
def capture_api_response(page: Page):
    """Capture API responses for verification."""
    responses = {}
    
    def _capture(pattern: str):
        def handle_response(response):
            if pattern in response.url:
                responses[response.url] = {
                    "status": response.status,
                    "body": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text(),
                }
        
        page.on("response", handle_response)
        return responses
    
    return _capture