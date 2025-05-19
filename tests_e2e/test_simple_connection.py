"""
Simple connection test to debug E2E issues
"""
import pytest
import requests
from playwright.sync_api import Page


def test_direct_api_connection():
    """Test direct API connection without Playwright"""
    response = requests.get("http://app:5000/health")
    print(f"Response status: {response.status_code}")
    print(f"Response text: {response.text}")
    assert response.status_code == 200


def test_playwright_connection(page: Page, base_url: str):
    """Test basic Playwright connection"""
    print(f"Base URL: {base_url}")
    response = page.goto(base_url + "/health", wait_until="domcontentloaded")
    print(f"Response status: {response.status}")
    assert response.status == 200
    content = page.content()
    print(f"Page content: {content[:200]}...")
    assert "status" in content