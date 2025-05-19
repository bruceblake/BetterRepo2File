"""
Page Object for the Vibe Coder Workflow Page
"""
from playwright.sync_api import Page, Locator
from typing import Optional


class VibeCoderPage:
    """Page Object for the Vibe Coder workflow page."""
    
    def __init__(self, page: Page):
        self.page = page
        
        # Stage A - Planning Context Generation
        self.stage_a_section: Locator = page.locator("#step1")
        self.vibe_statement_input: Locator = page.locator("#vibeStatement")
        self.github_url_input_a: Locator = page.locator("#githubUrlInputRepo")
        self.branch_input_a: Locator = page.locator("#githubBranch")
        self.generate_planning_btn: Locator = page.locator("#generateContextBtn")
        self.stage_a_output: Locator = page.locator("#outputPrimer")
        
        # Stage B - Implementation Context Generation
        self.stage_b_section: Locator = page.locator("#step2")
        self.planner_output_input: Locator = page.locator("#plannerOutput")
        self.generate_coding_btn: Locator = page.locator("#generateCoderContextBtn")
        self.stage_b_output: Locator = page.locator("#outputCoder")
        
        # Stage C - Iteration & Refinement
        self.stage_c_section: Locator = page.locator("#step3")
        self.generate_iteration_btn: Locator = page.locator("#generateIterationBtn")
        self.iteration_output: Locator = page.locator("#iterationOutput")
        
        # Progress indicators
        self.progress_steps: Locator = page.locator(".progress-step")
        self.active_step: Locator = page.locator(".progress-step.active")
        
        # API interaction buttons
        self.api_keys_btn: Locator = page.locator("button:has-text('API Keys')")
        self.profiles_btn: Locator = page.locator("button:has-text('Profiles')")
        
    def navigate(self, base_url: str):
        """Navigate to the Vibe Coder page."""
        self.page.goto(f"{base_url}/vibe-coder")
        self.page.wait_for_load_state("networkidle")
    
    def start_stage_a(
        self, 
        github_url: str,
        branch: str,
        vibe_statement: str
    ):
        """Start Stage A - Planning Context Generation."""
        # Fill in repository details
        self.github_url_input_a.fill(github_url)
        self.branch_input_a.fill(branch)
        
        # Enter vibe statement
        self.vibe_statement_input.fill(vibe_statement)
        
        # Click generate button
        self.generate_planning_btn.click()
    
    def wait_for_stage_a_complete(self, timeout: int = 60000):
        """Wait for Stage A to complete."""
        self.stage_a_output.wait_for(state="visible", timeout=timeout)
        # Wait for content to load
        self.page.wait_for_function(
            "document.querySelector('#outputPrimer').innerText.length > 100",
            timeout=timeout
        )
    
    def get_stage_a_output(self) -> str:
        """Get the Stage A output text."""
        return self.stage_a_output.inner_text()
    
    def start_stage_b(self, planner_output: str = None):
        """Start Stage B - Implementation Context Generation."""
        if planner_output:
            self.planner_output_input.fill(planner_output)
        
        self.generate_coding_btn.click()
    
    def wait_for_stage_b_complete(self, timeout: int = 60000):
        """Wait for Stage B to complete."""
        self.stage_b_output.wait_for(state="visible", timeout=timeout)
        # Wait for content to load
        self.page.wait_for_function(
            "document.querySelector('#outputCoder').innerText.length > 100",
            timeout=timeout
        )
    
    def get_stage_b_output(self) -> str:
        """Get the Stage B output text."""
        return self.stage_b_output.inner_text()
    
    def start_stage_c(self):
        """Start Stage C - Iteration & Refinement."""
        self.generate_iteration_btn.click()
    
    def wait_for_stage_c_complete(self, timeout: int = 60000):
        """Wait for Stage C to complete."""
        self.iteration_output.wait_for(state="visible", timeout=timeout)
    
    def get_stage_c_output(self) -> str:
        """Get the Stage C output text."""
        return self.iteration_output.inner_text()
    
    def get_active_step_number(self) -> int:
        """Get the currently active step number."""
        active_step_text = self.active_step.locator(".step-circle").inner_text()
        return int(active_step_text)
    
    def is_step_completed(self, step_number: int) -> bool:
        """Check if a specific step is completed."""
        step = self.page.locator(f".progress-step[data-step='{step_number}']")
        return "completed" in step.get_attribute("class", "")