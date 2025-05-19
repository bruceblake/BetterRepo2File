"""
Page Object for the RobustRepo Home Page
"""
from playwright.sync_api import Page, Locator
from typing import Optional


class HomePage:
    """Page Object for the main home page of RobustRepo."""
    
    def __init__(self, page: Page):
        self.page = page
        
        # Locators for main elements
        self.github_url_input: Locator = page.locator("#githubUrlInputRepo")
        self.branch_input: Locator = page.locator("#branch").or_(page.locator("#githubBranch"))
        self.file_upload_input: Locator = page.locator("input[type='file']")
        # Mode selector might be different based on page version
        self.mode_selector: Locator = page.locator("select[name='mode']").or_(page.locator("select#processingMode"))
        self.process_button: Locator = page.locator("#generateContextBtn")
        
        # Processing indicators
        self.loading_spinner: Locator = page.locator(".loading").or_(page.locator(".loading-spinner"))
        self.job_status: Locator = page.locator(".status").or_(page.locator("[data-testid='job-status']"))
        self.error_message: Locator = page.locator(".error-message")
        
        # Result elements
        self.output_area: Locator = page.locator("#output").or_(page.locator("#outputArea"))
        self.download_button: Locator = page.locator("#downloadBtn").or_(page.locator("button#downloadBtn"))
        self.copy_button: Locator = page.locator("#copyBtn").or_(page.locator("button#copyBtn"))
        
        # Profile selector
        self.profile_selector: Locator = page.locator("select#profile").or_(page.locator("select#profileSelect"))
    
    def navigate(self, base_url: str):
        """Navigate to the home page."""
        self.page.goto(base_url, wait_until="domcontentloaded")
        # Wait for a key element to be visible instead of networkidle
        self.page.wait_for_selector("#generateContextBtn", state="visible", timeout=30000)
    
    def submit_github_repo(
        self, 
        url: str, 
        branch: str = "main",
        mode: str = "standard"
    ):
        """Submit a GitHub repository for processing."""
        self.github_url_input.fill(url)
        self.branch_input.fill(branch)
        self.select_processing_mode(mode)
        self.process_button.click()
    
    def upload_files(self, file_paths: list):
        """Upload files for processing."""
        self.file_upload_input.set_input_files(file_paths)
    
    def select_processing_mode(self, mode: str):
        """Select a processing mode."""
        self.mode_selector.select_option(value=mode)
    
    def select_profile(self, profile: str):
        """Select a configuration profile."""
        self.profile_selector.select_option(value=profile)
    
    def wait_for_processing_start(self, timeout: int = 10000):
        """Wait for processing to start (loading spinner appears)."""
        self.loading_spinner.wait_for(state="visible", timeout=timeout)
    
    def wait_for_processing_complete(self, timeout: int = 60000):
        """Wait for processing to complete."""
        # Wait for loading spinner to disappear
        self.loading_spinner.wait_for(state="hidden", timeout=timeout)
        
        # Wait for status to show completion
        self.page.wait_for_selector(
            "[data-testid='job-status']:has-text('SUCCESS'), [data-testid='job-status']:has-text('FAILURE')",
            timeout=timeout
        )
    
    def get_job_status(self) -> str:
        """Get the current job status."""
        return self.job_status.inner_text()
    
    def get_output_text(self) -> str:
        """Get the output text from the result area."""
        return self.output_area.inner_text()
    
    def download_output(self):
        """Click the download button."""
        self.download_button.click()
    
    def copy_output(self):
        """Click the copy button."""
        self.copy_button.click()
    
    def has_error(self) -> bool:
        """Check if an error message is displayed."""
        return self.error_message.is_visible()
    
    def get_error_text(self) -> Optional[str]:
        """Get the error message text if displayed."""
        if self.has_error():
            return self.error_message.inner_text()
        return None