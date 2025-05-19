"""
Debug test to check page structure
"""
import pytest
from playwright.sync_api import Page


def test_page_structure(page: Page, base_url: str):
    """Check the actual page structure"""
    print(f"Navigating to: {base_url}")
    page.goto(base_url, wait_until="domcontentloaded")
    
    # Take a screenshot for debugging
    page.screenshot(path="test-results/debug-homepage.png")
    
    # Get the page title
    title = page.title()
    print(f"Page title: {title}")
    
    # Get all visible text
    text_content = page.get_by_role("heading").all_text_contents()
    print(f"Headings: {text_content}")
    
    # Check if specific elements exist
    elements_to_check = [
        "#githubUrlInputRepo",
        "#generateContextBtn",
        "#processingMode",
        "select#processingMode",
        "#outputArea"
    ]
    
    for selector in elements_to_check:
        try:
            element = page.locator(selector)
            exists = element.count() > 0
            print(f"Element '{selector}' exists: {exists}")
            if exists:
                is_visible = element.is_visible()
                print(f"  - is visible: {is_visible}")
        except Exception as e:
            print(f"Error checking '{selector}': {e}")
    
    # Get the page content snippet
    content = page.content()
    print(f"Page content length: {len(content)}")
    print(f"First 500 chars: {content[:500]}...")