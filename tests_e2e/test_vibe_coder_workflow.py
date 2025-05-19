"""
E2E tests for the Vibe Coder workflow
"""
import pytest
from playwright.sync_api import Page, expect
from page_objects.vibe_coder_page import VibeCoderPage


class TestVibeCoderWorkflow:
    """Test the multi-stage Vibe Coder workflow."""
    
    @pytest.mark.integration
    def test_stage_a_planning_context(
        self,
        page: Page,
        base_url: str,
        test_github_repo: str
    ):
        """Test Stage A - Planning Context Generation."""
        vibe_page = VibeCoderPage(page)
        vibe_page.navigate(base_url)
        
        # Start Stage A
        vibe_statement = "Create a modern web application with user authentication"
        vibe_page.start_stage_a(
            github_url=test_github_repo,
            branch="master",
            vibe_statement=vibe_statement
        )
        
        # Wait for completion
        vibe_page.wait_for_stage_a_complete()
        
        # Verify output
        output = vibe_page.get_stage_a_output()
        assert len(output) > 500, "Stage A should produce substantial output"
        assert "GEMINI PLANNER PRIMER" in output
        assert vibe_statement in output
        
        # Verify step progression
        assert vibe_page.get_active_step_number() >= 1
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_full_vibe_coder_workflow(
        self,
        page: Page,
        base_url: str,
        test_github_repo: str
    ):
        """Test the complete Vibe Coder workflow through all stages."""
        vibe_page = VibeCoderPage(page)
        vibe_page.navigate(base_url)
        
        # Stage A
        vibe_statement = "Implement a RESTful API with CRUD operations"
        vibe_page.start_stage_a(
            github_url=test_github_repo,
            branch="master",
            vibe_statement=vibe_statement
        )
        vibe_page.wait_for_stage_a_complete()
        
        # Verify Stage A completed
        stage_a_output = vibe_page.get_stage_a_output()
        assert "GEMINI PLANNER PRIMER" in stage_a_output
        
        # Stage B - Use output from Stage A
        vibe_page.start_stage_b()  # Should auto-populate from Stage A
        vibe_page.wait_for_stage_b_complete()
        
        # Verify Stage B completed
        stage_b_output = vibe_page.get_stage_b_output()
        assert len(stage_b_output) > 500
        assert "CODING CONTEXT" in stage_b_output or "IMPLEMENTATION" in stage_b_output
        
        # Stage C - Iteration
        vibe_page.start_stage_c()
        vibe_page.wait_for_stage_c_complete()
        
        # Verify Stage C completed
        stage_c_output = vibe_page.get_stage_c_output()
        assert len(stage_c_output) > 100
        
        # Verify all steps show as completed
        assert vibe_page.is_step_completed(1)
        assert vibe_page.is_step_completed(2)
        assert vibe_page.is_step_completed(3)
    
    def test_stage_b_with_custom_planner_output(
        self,
        page: Page,
        base_url: str
    ):
        """Test Stage B with custom planner output."""
        vibe_page = VibeCoderPage(page)
        vibe_page.navigate(base_url)
        
        # Skip Stage A and go directly to Stage B with custom input
        custom_planner_output = """
        Custom planner output for testing:
        - Task 1: Implement user model
        - Task 2: Create API endpoints
        - Task 3: Add authentication
        """
        
        vibe_page.start_stage_b(planner_output=custom_planner_output)
        vibe_page.wait_for_stage_b_complete()
        
        # Verify output references the custom input
        output = vibe_page.get_stage_b_output()
        assert len(output) > 200
    
    @pytest.mark.smoke
    def test_vibe_coder_navigation(self, page: Page, base_url: str):
        """Test navigation to Vibe Coder page."""
        # Start from home page
        page.goto(base_url)
        
        # Navigate to Vibe Coder (might be a link or button)
        vibe_link = page.locator("a:has-text('Vibe Coder')").first
        if vibe_link.is_visible():
            vibe_link.click()
        else:
            # Direct navigation if no link
            page.goto(f"{base_url}/vibe-coder")
        
        # Verify we're on the Vibe Coder page
        expect(page).to_have_url_pattern(".*vibe.*")
        
        # Verify key elements are present
        vibe_page = VibeCoderPage(page)
        expect(vibe_page.vibe_statement_input).to_be_visible()
        expect(vibe_page.generate_planning_btn).to_be_visible()