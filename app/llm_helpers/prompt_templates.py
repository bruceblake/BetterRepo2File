"""Prompt templates for different LLM tasks."""
from enum import Enum
from typing import Dict, Any, Optional
import json


class TaskType(Enum):
    """Types of tasks for LLM interactions."""
    CODE_REVIEW = "code_review"
    DEBUG = "debug"
    DOCUMENTATION = "documentation"
    REFACTOR = "refactor"
    SECURITY_AUDIT = "security_audit"
    EXPLAIN_CODE = "explain_code"
    GENERATE_CODE = "generate_code"
    OPTIMIZE_PERFORMANCE = "optimize_performance"
    MIGRATE_CODE = "migrate_code"
    GENERAL = "general"


class PromptTemplateManager:
    """Manages prompt templates for different LLM tasks."""
    
    TEMPLATES = {
        TaskType.CODE_REVIEW: """
You are reviewing code from the {repository_name} repository.
Focus on: {focus_areas}

Repository structure:
{file_hierarchy}

Files to review:
{file_list}

Please provide a comprehensive code review covering:
1. Code quality and best practices
2. Potential bugs or edge cases
3. Performance considerations
4. Security concerns
5. Suggestions for improvements

{additional_instructions}
""",
        
        TaskType.DEBUG: """
You are debugging an issue in the {repository_name} repository.
Issue description: {issue_description}

Repository structure:
{file_hierarchy}

Relevant files:
{file_list}

Error logs or stack traces:
{error_logs}

Please help identify:
1. Root cause of the issue
2. Potential fixes
3. Files that need to be modified
4. Test cases to prevent regression

{additional_instructions}
""",
        
        TaskType.DOCUMENTATION: """
You are creating/updating documentation for the {repository_name} repository.
Documentation type: {doc_type}

Repository structure:
{file_hierarchy}

Key files to document:
{file_list}

Please create documentation that includes:
1. Overview of the repository/module
2. Key components and their purposes
3. API references where applicable
4. Usage examples
5. Configuration options

{additional_instructions}
""",
        
        TaskType.REFACTOR: """
You are refactoring code in the {repository_name} repository.
Refactoring goals: {refactor_goals}

Repository structure:
{file_hierarchy}

Files to refactor:
{file_list}

Please suggest refactoring changes that:
1. Improve code organization and maintainability
2. Eliminate code duplication
3. Apply design patterns where appropriate
4. Maintain backward compatibility
5. Include necessary tests

{additional_instructions}
""",
        
        TaskType.SECURITY_AUDIT: """
You are conducting a security audit of the {repository_name} repository.
Security focus areas: {security_focus}

Repository structure:
{file_hierarchy}

Files to audit:
{file_list}

Dependencies:
{dependencies}

Please identify:
1. Security vulnerabilities
2. Insecure coding practices
3. Exposed sensitive data
4. Dependency vulnerabilities
5. Recommended fixes and mitigations

{additional_instructions}
""",
        
        TaskType.EXPLAIN_CODE: """
You are explaining code from the {repository_name} repository.
Explanation level: {explanation_level}

Repository structure:
{file_hierarchy}

Files to explain:
{file_list}

Please provide:
1. High-level overview of the code's purpose
2. Detailed explanation of key functions/classes
3. Data flow and architecture
4. Dependencies and integrations
5. Examples of how the code is used

{additional_instructions}
""",
        
        TaskType.GENERATE_CODE: """
You are generating code for the {repository_name} repository.
Code requirements: {requirements}

Repository structure:
{file_hierarchy}

Existing related files:
{file_list}

Please generate code that:
1. Follows the repository's coding standards
2. Integrates with existing architecture
3. Includes appropriate tests
4. Has proper error handling
5. Is well-documented

{additional_instructions}
""",
        
        TaskType.OPTIMIZE_PERFORMANCE: """
You are optimizing performance in the {repository_name} repository.
Performance goals: {performance_goals}

Repository structure:
{file_hierarchy}

Files to optimize:
{file_list}

Performance metrics:
{performance_metrics}

Please suggest optimizations for:
1. Algorithm efficiency
2. Resource usage (memory, CPU)
3. Database queries
4. Caching strategies
5. Async/parallel processing opportunities

{additional_instructions}
""",
        
        TaskType.MIGRATE_CODE: """
You are migrating code in the {repository_name} repository.
Migration details: {migration_details}

Repository structure:
{file_hierarchy}

Files to migrate:
{file_list}

Target environment:
{target_environment}

Please provide:
1. Migration strategy
2. Required code changes
3. Compatibility considerations
4. Testing approach
5. Rollback plan

{additional_instructions}
""",
        
        TaskType.GENERAL: """
Repository: {repository_name}
Task: {task_description}

Repository structure:
{file_hierarchy}

Relevant files:
{file_list}

{additional_instructions}
"""
    }
    
    def __init__(self):
        """Initialize the prompt template manager."""
        self.custom_templates: Dict[str, str] = {}
    
    def get_template(
        self,
        task_type: TaskType,
        custom_template: Optional[str] = None
    ) -> str:
        """Get prompt template for a task type."""
        if custom_template:
            return custom_template
        
        if task_type in self.TEMPLATES:
            return self.TEMPLATES[task_type]
        
        # Fall back to general template
        return self.TEMPLATES[TaskType.GENERAL]
    
    def create_prompt(
        self,
        task_type: TaskType,
        template_vars: Dict[str, Any],
        custom_template: Optional[str] = None
    ) -> str:
        """Create a prompt from template and variables."""
        template = self.get_template(task_type, custom_template)
        
        # Prepare variables with defaults
        vars_with_defaults = {
            'repository_name': 'Unknown Repository',
            'file_hierarchy': '{}',
            'file_list': '[]',
            'additional_instructions': '',
            'focus_areas': 'general code quality',
            'issue_description': 'No specific issue described',
            'error_logs': 'No error logs provided',
            'doc_type': 'general documentation',
            'refactor_goals': 'improve code quality',
            'security_focus': 'general security best practices',
            'explanation_level': 'intermediate',
            'requirements': 'No specific requirements',
            'performance_goals': 'general performance improvements',
            'performance_metrics': 'No metrics provided',
            'migration_details': 'No migration details provided',
            'target_environment': 'Unknown target',
            'task_description': 'General analysis',
            **template_vars
        }
        
        # Convert complex objects to strings
        for key, value in vars_with_defaults.items():
            if isinstance(value, (dict, list)):
                vars_with_defaults[key] = json.dumps(value, indent=2)
        
        # Format the template
        try:
            return template.format(**vars_with_defaults)
        except KeyError as e:
            # Handle missing variables gracefully
            missing_var = str(e).strip("'")
            vars_with_defaults[missing_var] = f"[{missing_var} not provided]"
            return template.format(**vars_with_defaults)
    
    def add_custom_template(self, name: str, template: str) -> None:
        """Add a custom template."""
        self.custom_templates[name] = template
    
    def get_custom_template(self, name: str) -> Optional[str]:
        """Get a custom template by name."""
        return self.custom_templates.get(name)
    
    def create_context_prompt(
        self,
        context: 'LLMContext',
        task_specific_vars: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a prompt from an LLMContext object."""
        # Extract task type from context
        task_type_str = context.task_type.lower()
        task_type = TaskType.GENERAL
        
        # Try to match to enum
        for t in TaskType:
            if t.value == task_type_str:
                task_type = t
                break
        
        # Prepare template variables from context
        template_vars = {
            'repository_name': context.repository_info.get('name', 'Repository'),
            'file_hierarchy': context.file_hierarchy,
            'file_list': context.selected_files,
            **context.additional_metadata
        }
        
        # Add task-specific variables
        if task_specific_vars:
            template_vars.update(task_specific_vars)
        
        return self.create_prompt(task_type, template_vars)