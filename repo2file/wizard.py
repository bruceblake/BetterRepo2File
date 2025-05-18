"""
Interactive workflow wizard for the Vibe Coder workflow
"""
import os
import sys
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

console = Console()

class WorkflowWizard:
    """Interactive wizard for guiding users through the Vibe Coder workflow"""
    
    STAGES = {
        'A': 'Fresh Start / Planning (Need context for AI Planner)',
        'B': 'Coding Phase (Have a plan from AI Planner)',
        'C': 'Iteration / Feedback (Have results from AI Coder)'
    }
    
    # Noise suppression patterns (requirement N-1)
    NOISE_PATTERNS = [
        '.git/**',
        '*.png', '*.jpg', '*.jpeg', '*.gif', '*.svg', '*.ico',
        '*.pyc', '*.pyo', '__pycache__/**',
        'node_modules/**',
        '*.pdf', '*.doc', '*.docx',
        'venv/**', '.venv/**',
        '*.zip', '*.tar', '*.gz', '*.7z',
        '*.exe', '*.dll', '*.so', '*.dylib',
    ]
    
    # Large file threshold (requirement N-1)
    MAX_FILE_SIZE = 1048576  # 1 MiB
    
    def __init__(self, repo_path: Optional[str] = None):
        self.repo_path = Path(repo_path) if repo_path else None
        self.vibe_statement = ""
        self.stage = None
        self.planner_output = ""
        self.previous_output_path = None
        self.feedback_text = ""
        
    def run(self):
        """Run the interactive wizard workflow"""
        console.clear()
        
        # Welcome message
        console.print(Panel.fit(
            "[bold cyan]Repo2File Vibe Coder Workflow Assistant[/bold cyan]\n\n"
            "I'll help you prepare the perfect context for your AI planning and coding workflow.",
            title="Welcome"
        ))
        
        # Get repository path if not provided
        if not self.repo_path:
            self.get_repo_path()
        
        # Get vibe/goal
        self.get_vibe_statement()
        
        # Get workflow stage
        self.get_workflow_stage()
        
        # Collect stage-specific inputs
        if self.stage == 'B':
            self.get_planner_output()
        elif self.stage == 'C':
            self.get_iteration_inputs()
        
        # Generate output
        self.generate_output()
    
    def get_repo_path(self):
        """Prompt for repository path"""
        console.print("\n[bold]First, which repository are we working with?[/bold]")
        
        default_path = os.getcwd()
        path = Prompt.ask(
            "Repository path",
            default=default_path
        )
        
        self.repo_path = Path(path)
        if not self.repo_path.exists():
            console.print(f"[red]Error: Path '{path}' does not exist[/red]")
            sys.exit(1)
    
    def get_vibe_statement(self):
        """Prompt for vibe/goal statement"""
        console.print("\n[bold]What's your primary vibe/goal for this session?[/bold]")
        console.print("[dim]Example: 'Improve checkout speed' or 'Add dark mode support'[/dim]")
        
        self.vibe_statement = Prompt.ask("Your vibe/goal")
        
    def get_workflow_stage(self):
        """Prompt for workflow stage"""
        console.print("\n[bold]What stage are you at in your workflow?[/bold]")
        
        # Display options as a table
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Choice", style="cyan")
        table.add_column("Description")
        
        for key, desc in self.STAGES.items():
            table.add_row(f"[{key}]", desc)
        
        console.print(table)
        
        choice = Prompt.ask(
            "Select stage",
            choices=list(self.STAGES.keys()),
            default='A'
        ).upper()
        
        self.stage = choice
        console.print(f"\n[green]Selected: {self.STAGES[choice]}[/green]")
    
    def get_planner_output(self):
        """Get AI Planner's output for Stage B"""
        console.print("\n[bold]I need the AI Planner's output/instructions.[/bold]")
        console.print("[dim]You can either paste the plan directly or provide a file path.[/dim]")
        
        input_type = Prompt.ask(
            "Input method",
            choices=['paste', 'file'],
            default='paste'
        )
        
        if input_type == 'paste':
            console.print("[dim]Paste your planner's output below (press Ctrl+D when done):[/dim]")
            lines = []
            try:
                while True:
                    lines.append(input())
            except EOFError:
                pass
            self.planner_output = '\n'.join(lines)
        else:
            file_path = Prompt.ask("Path to planner output file")
            try:
                with open(file_path, 'r') as f:
                    self.planner_output = f.read()
            except Exception as e:
                console.print(f"[red]Error reading file: {e}[/red]")
                self.get_planner_output()  # Retry
    
    def get_iteration_inputs(self):
        """Get inputs for Stage C (iteration)"""
        console.print("\n[bold]For iteration, I need information about your previous work.[/bold]")
        
        # Get previous repo2file output
        self.previous_output_path = Prompt.ask(
            "Path to previous repo2file output file"
        )
        
        if not Path(self.previous_output_path).exists():
            console.print(f"[red]File not found: {self.previous_output_path}[/red]")
            self.get_iteration_inputs()  # Retry
            return
        
        # Get feedback
        console.print("\n[bold]Do you have feedback/logs from your AI Coder's results?[/bold]")
        has_feedback = Confirm.ask("Do you have feedback to include?", default=True)
        
        if has_feedback:
            input_type = Prompt.ask(
                "How would you like to provide feedback?",
                choices=['paste', 'file'],
                default='paste'
            )
            
            if input_type == 'paste':
                console.print("[dim]Paste your feedback below (press Ctrl+D when done):[/dim]")
                lines = []
                try:
                    while True:
                        lines.append(input())
                except EOFError:
                    pass
                self.feedback_text = '\n'.join(lines)
            else:
                file_path = Prompt.ask("Path to feedback file")
                try:
                    with open(file_path, 'r') as f:
                        self.feedback_text = f.read()
                except Exception as e:
                    console.print(f"[red]Error reading file: {e}[/red]")
    
    def generate_output(self):
        """Generate stage-specific output"""
        console.print("\n[bold cyan]Generating output...[/bold cyan]")
        
        output_path = f"vibe-coder-output-stage-{self.stage.lower()}.txt"
        
        # Import the ultra mode processor and profile manager
        from repo2file.dump_ultra import UltraRepo2File, ProcessingProfile
        import sys
        sys.path.append(str(Path(__file__).parent.parent))
        from app.profiles import ProfileManager
        
        # Get the vibe-coder profile
        manager = ProfileManager()
        profile = manager.get_profile('vibe_coder_gemini_claude')
        
        # Add runtime attributes
        profile.vibe_statement = self.vibe_statement
        profile.enable_git_insights = True
        
        processor = UltraRepo2File(profile)
        
        if self.stage == 'A':
            # Stage A: Generate planner primer
            output = self._generate_stage_a_output(processor)
        elif self.stage == 'B':
            # Stage B: Generate coder context
            profile.planner_output = self.planner_output
            output = self._generate_stage_b_output(processor)
        elif self.stage == 'C':
            # Stage C: Generate iteration brief
            output = self._generate_stage_c_output(processor)
        
        # Write output
        with open(output_path, 'w') as f:
            f.write(output)
        
        # Display success message
        console.print(Panel.fit(
            f"[green]✓ Output generated successfully![/green]\n\n"
            f"File saved to: [cyan]{output_path}[/cyan]\n\n"
            f"[bold]NEXT STEP:[/bold] {self._get_next_step_instruction()}",
            title="Complete"
        ))
    
    def _generate_stage_a_output(self, processor) -> str:
        """Generate output for Stage A (Planning)"""
        sections = []
        
        # Header for AI Planner
        sections.append("=" * 50)
        sections.append("SECTION FOR AI PLANNING AGENT (GEMINI)")
        sections.append("Copy everything below this line into AI Studio.")
        sections.append("=" * 50)
        sections.append("")
        
        # Vibe/Goal
        sections.append("MY VIBE/GOAL:")
        sections.append(self.vibe_statement)
        sections.append("")
        
        # Project overview
        sections.append("PROJECT OVERVIEW & KEY AREAS:")
        
        # Use processor to analyze repo
        from repo2file.dump_ultra import CodebaseAnalyzer
        analyzer = CodebaseAnalyzer(processor.code_analyzer)
        
        # Quick scan for analysis
        from repo2file.dump_ultra import UltraFileScanner, Cache, ExclusionSpec
        import pathspec
        
        cache = Cache()
        scanner = UltraFileScanner(cache, processor.token_manager, processor.code_analyzer, processor.profile)
        
        # Basic exclusion patterns
        patterns = ['.git', '__pycache__', 'node_modules', '.venv', 'venv']
        exclusion_spec = pathspec.PathSpec.from_lines('gitwildmatch', patterns)
        
        files = scanner.scan_directory(self.repo_path, exclusion_spec)
        analysis = analyzer.analyze_codebase(files)
        
        # Add analysis results
        sections.append(f"- Primary Language: {analysis.get('primary_language', 'Mixed')}")
        sections.append(f"- Frameworks: {', '.join(analysis.get('frameworks', []))}")
        sections.append(f"- Total Files: {analysis.get('total_files', 0)}")
        sections.append("")
        
        # Top-level modules
        sections.append("TOP-LEVEL MODULES/DIRECTORIES:")
        file_groups = processor.manifest_generator._group_files_by_directory(files)
        for i, (dir_path, dir_files) in enumerate(sorted(file_groups.items())[:7]):
            if dir_files:
                purpose = processor.manifest_generator._determine_directory_purpose(dir_path, dir_files)
                sections.append(f"- {dir_path or 'Root'}: {purpose or 'General'}")
        sections.append("")
        
        # TODOs and recent activity
        if processor.profile.enable_git_insights and processor.git_analyzer:
            sections.append("RECENT ACTIVITY:")
            recent_files = processor.git_analyzer.get_recent_changes(days=7)
            for i, (file, changes) in enumerate(recent_files[:5]):
                sections.append(f"- {file}: {changes} changes")
            sections.append("")
        
        sections.append("--- END OF SECTION FOR AI PLANNING AGENT ---")
        sections.append("")
        sections.append("NEXT STEP: Copy the section above and paste it into your AI Planning tool")
        sections.append("(e.g., Gemini in AI Studio) along with your planning query.")
        
        return '\n'.join(sections)
    
    def _generate_stage_b_output(self, processor) -> str:
        """Generate output for Stage B (Coding)"""
        sections = []
        
        # Header for AI Coder
        sections.append("=" * 50)
        sections.append("SECTION FOR AI CODING AGENT (CLAUDE)")
        sections.append("This combines the AI Planner's instructions with detailed codebase context.")
        sections.append("=" * 50)
        sections.append("")
        
        # Include planner's instructions
        sections.append("AI PLANNER'S INSTRUCTIONS (From Gemini):")
        sections.append(self.planner_output)
        sections.append("")
        sections.append("--- DETAILED CODEBASE CONTEXT (Anchored & Annotated) ---")
        sections.append("")
        
        # Generate full repo2file output
        processor.process_repository(self.repo_path, Path("temp_stage_b.txt"))
        
        with open("temp_stage_b.txt", 'r') as f:
            content = f.read()
        
        # Extract the relevant parts (skip headers, focus on manifest and content)
        # This is a simplified approach - in production, we'd parse more carefully
        sections.append(content)
        
        sections.append("")
        sections.append("--- END OF SECTION FOR AI CODING AGENT ---")
        sections.append("")
        sections.append("NEXT STEP: Use the AI Planner's Instructions and the Detailed Codebase Context")
        sections.append("above to craft your prompts for your local AI Coding Agent (e.g., Claude).")
        sections.append("Use the [[ANCHORS]] to refer to specific code locations.")
        
        # Cleanup temp file
        os.remove("temp_stage_b.txt")
        
        return '\n'.join(sections)
    
    def _generate_stage_c_output(self, processor) -> str:
        """Generate output for Stage C (Iteration)"""
        # Use the existing iteration functionality
        from repo2file.dump_ultra import main_iterate
        
        # Mock sys.argv for the iteration mode
        original_argv = sys.argv
        sys.argv = [
            'dump_ultra.py',
            'iterate',
            '--current-repo-path', str(self.repo_path),
            '--previous-repo2file-output', self.previous_output_path,
            '--output', 'temp_iteration_brief.md'
        ]
        
        if self.feedback_text:
            # Write feedback to temp file
            with open('temp_feedback.txt', 'w') as f:
                f.write(self.feedback_text)
            sys.argv.extend(['--user-feedback-file', 'temp_feedback.txt'])
        
        try:
            main_iterate()
            
            # Read the generated iteration brief
            with open('temp_iteration_brief.md', 'r') as f:
                content = f.read()
            
            # Wrap with stage-specific headers
            sections = []
            sections.append("=" * 50)
            sections.append("ITERATION FEEDBACK FOR AI PLANNING AGENT (GEMINI)")
            sections.append("Copy everything below this line into AI Studio for your next planning cycle.")
            sections.append("=" * 50)
            sections.append("")
            sections.append(content)
            sections.append("")
            sections.append("--- END OF ITERATION FEEDBACK ---")
            sections.append("")
            sections.append("NEXT STEP: Copy the section above and paste it into your AI Planning tool")
            sections.append("(e.g., Gemini in AI Studio) to plan the next iteration.")
            
            return '\n'.join(sections)
            
        finally:
            # Restore argv and cleanup
            sys.argv = original_argv
            if os.path.exists('temp_feedback.txt'):
                os.remove('temp_feedback.txt')
            if os.path.exists('temp_iteration_brief.md'):
                os.remove('temp_iteration_brief.md')
    
    def _get_next_step_instruction(self) -> str:
        """Get stage-specific next step instruction"""
        if self.stage == 'A':
            return "Copy the AI PLANNER section and paste into Gemini AI Studio"
        elif self.stage == 'B':
            return "Use the generated context to prompt your local Claude instance"
        elif self.stage == 'C':
            return "Copy the ITERATION FEEDBACK section back to Gemini for next planning cycle"
        return ""


def run_workflow_wizard(repo_path: Optional[str] = None):
    """Entry point for the workflow wizard"""
    wizard = WorkflowWizard(repo_path)
    try:
        wizard.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Wizard cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)