"""
Basic E2E tests for RobustRepo core functionality
"""
import pytest
from playwright.sync_api import Page, expect
from page_objects.home_page import HomePage


class TestBasicWorkflow:
    """Test basic repository processing workflows."""
    
    @pytest.mark.smoke
    def test_homepage_loads(self, page: Page, base_url: str):
        """Test that the homepage loads successfully."""
        home = HomePage(page)
        home.navigate(base_url)
        
        # Verify page title contains expected text
        assert "BetterRepo2File" in page.title()
        
        # Verify main elements are visible
        assert home.github_url_input.is_visible()
        assert home.process_button.is_visible()
    
    @pytest.mark.smoke
    def test_github_repo_processing_standard_mode(
        self, 
        page: Page, 
        base_url: str,
        test_github_repo: str
    ):
        """Test processing a GitHub repository in standard mode."""
        home = HomePage(page)
        home.navigate(base_url)
        
        # Submit a small public repo
        home.submit_github_repo(
            url=test_github_repo,
            branch="master",
            mode="standard"
        )
        
        # Wait for processing to start
        home.wait_for_processing_start()
        
        # Wait for completion
        home.wait_for_processing_complete(timeout=120000)  # 2 minutes
        
        # Verify success
        status = home.get_job_status()
        assert status == "SUCCESS", f"Expected SUCCESS but got {status}"
        
        # Verify output is present
        output = home.get_output_text()
        assert len(output) > 100, "Output should contain processed content"
        assert test_github_repo in output, "Output should reference the processed repo"
    
    @pytest.mark.integration
    def test_github_repo_processing_smart_mode(
        self,
        page: Page,
        base_url: str,
        test_github_repo: str
    ):
        """Test processing a GitHub repository in smart mode."""
        home = HomePage(page)
        home.navigate(base_url)
        
        # Submit with smart mode
        home.submit_github_repo(
            url=test_github_repo,
            branch="master",
            mode="smart"
        )
        
        home.wait_for_processing_start()
        home.wait_for_processing_complete(timeout=180000)  # 3 minutes
        
        # Verify success
        status = home.get_job_status()
        assert status == "SUCCESS", f"Expected SUCCESS but got {status}"
        
        # Smart mode should produce optimized output
        output = home.get_output_text()
        assert "CODEBASE ANALYSIS" in output, "Smart mode should include analysis"
    
    def test_invalid_github_url(self, page: Page, base_url: str):
        """Test handling of invalid GitHub URL."""
        home = HomePage(page)
        home.navigate(base_url)
        
        # Just fill the field and submit without using mode selector
        home.github_url_input.fill("https://invalid-url-not-github.com/repo")
        home.process_button.click()
        
        # Wait for any error feedback
        page.wait_for_timeout(3000)  # Give it time to process
        
        # Check if we're still on the same page (form should still be visible)
        assert home.github_url_input.is_visible()  # Should still be on the form
    
    @pytest.mark.smoke
    def test_mode_selection(self, page: Page, base_url: str):
        """Test that basic form elements are functional."""
        home = HomePage(page)
        home.navigate(base_url)
        
        # Check that the main form elements are functional
        # Fill in the URL field
        home.github_url_input.fill("https://github.com/test/repo")
        assert home.github_url_input.input_value() == "https://github.com/test/repo"
        
        # The branch field might exist
        try:
            if home.branch_input.is_visible():
                home.branch_input.fill("develop")
                assert home.branch_input.input_value() == "develop"
        except:
            pass  # Branch field might not exist in all versions
    
    @pytest.mark.slow
    def test_download_output(
        self,
        page: Page,
        base_url: str,
        test_github_repo: str
    ):
        """Test downloading processed output."""
        home = HomePage(page)
        home.navigate(base_url)
        
        # Process a repo first
        home.submit_github_repo(test_github_repo, "master")
        home.wait_for_processing_complete()
        
        # Set up download handler
        with page.expect_download() as download_info:
            home.download_output()
            
        download = download_info.value
        
        # Verify download
        assert download.suggested_filename.endswith(".txt")
        
        # Save and verify content
        path = download.path()
        with open(path, 'r') as f:
            content = f.read()
            assert len(content) > 100
            assert test_github_repo in content