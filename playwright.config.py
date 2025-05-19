"""
Playwright configuration for E2E tests
"""
import os


# Playwright configuration
use_chromium = True
use_firefox = True
use_webkit = False  # WebKit can be problematic in Docker

# Browser launch options
browser_launch_args = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-dev-shm-usage",
    "--disable-accelerated-2d-canvas",
    "--no-first-run",
    "--no-zygote",
    "--disable-gpu",
]

# Context options
browser_context_args = {
    "viewport": {"width": 1280, "height": 720},
    "ignore_https_errors": True,
    "user_agent": "RobustRepo-E2E-Tests/1.0",
}

# Test configuration
default_timeout = 30000  # 30 seconds
expect_timeout = 10000   # 10 seconds
navigation_timeout = 30000  # 30 seconds

# Screenshot and video settings
screenshot_mode = "only-on-failure"
video_mode = "retain-on-failure"
trace_mode = "retain-on-failure"

# Parallel execution
workers = 1 if os.environ.get("CI") else 2

# Retry configuration
retries = 1 if os.environ.get("CI") else 0

# Output directory
output_dir = "test-results"