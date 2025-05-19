"""LLM-specific routes for enhanced context generation."""
from flask import Blueprint, request, jsonify
from typing import Dict, Any, Optional
import os
import logging

from app.llm_helpers import (
    ContextManager,
    LLMContext,
    FilePrioritizer,
    PromptTemplateManager,
    OutputFormatter,
    TaskType,
    FormatType
)
from app.job_manager import JobManager
from app.storage_manager import StorageManager
from repo2file.git_analyzer import GitAnalyzer
from repo2file.token_manager import TokenManager

logger = logging.getLogger(__name__)

# Create blueprint
llm_bp = Blueprint('llm', __name__, url_prefix='/api/llm')

# Initialize helpers
context_manager = ContextManager()
file_prioritizer = FilePrioritizer()
prompt_manager = PromptTemplateManager()
output_formatter = OutputFormatter()


@llm_bp.route('/generate-context', methods=['POST'])
def generate_llm_context():
    """Generate optimized context for LLM consumption."""
    try:
        data = request.json
        
        # Extract parameters
        repository_path = data.get('repository_path')
        task_type = data.get('task_type', 'general')
        model = data.get('model', 'gpt-4')
        token_budget = data.get('token_budget', 100000)
        output_format = data.get('output_format', 'structured_text')
        focus_areas = data.get('focus_areas', [])
        additional_options = data.get('options', {})
        
        if not repository_path:
            return jsonify({'error': 'repository_path is required'}), 400
        
        # Get job and storage managers from app context
        job_manager: JobManager = request.app.config.get('job_manager')
        storage_manager: StorageManager = request.app.config.get('storage_manager')
        
        # Submit job for LLM context generation
        job_id = job_manager.submit_job(
            task_type='llm_context_generation',
            input_data={
                'repository_path': repository_path,
                'task_type': task_type,
                'model': model,
                'token_budget': token_budget,
                'output_format': output_format,
                'focus_areas': focus_areas,
                'additional_options': additional_options
            }
        )
        
        return jsonify({
            'job_id': job_id,
            'status': 'submitted',
            'message': 'LLM context generation job submitted'
        }), 202
        
    except Exception as e:
        logger.error(f"Error generating LLM context: {e}")
        return jsonify({'error': str(e)}), 500


@llm_bp.route('/task-templates', methods=['GET'])
def get_task_templates():
    """Get available task templates."""
    try:
        templates = []
        for task_type in TaskType:
            template = prompt_manager.get_template(task_type)
            templates.append({
                'task_type': task_type.value,
                'name': task_type.name,
                'template': template.strip()
            })
        
        return jsonify({
            'templates': templates,
            'custom_templates': list(prompt_manager.custom_templates.keys())
        })
        
    except Exception as e:
        logger.error(f"Error getting task templates: {e}")
        return jsonify({'error': str(e)}), 500


@llm_bp.route('/output-formats', methods=['GET'])
def get_output_formats():
    """Get available output formats."""
    try:
        formats = []
        for format_type in FormatType:
            formats.append({
                'format': format_type.value,
                'name': format_type.name,
                'description': f"Output in {format_type.value} format"
            })
        
        return jsonify({'formats': formats})
        
    except Exception as e:
        logger.error(f"Error getting output formats: {e}")
        return jsonify({'error': str(e)}), 500


@llm_bp.route('/preview-context', methods=['POST'])
def preview_context():
    """Preview LLM context without saving."""
    try:
        data = request.json
        
        # Extract parameters
        repository_path = data.get('repository_path')
        task_type = data.get('task_type', 'general')
        model = data.get('model', 'gpt-4')
        token_budget = data.get('token_budget', 10000)  # Smaller for preview
        output_format = data.get('output_format', 'structured_text')
        
        if not repository_path:
            return jsonify({'error': 'repository_path is required'}), 400
        
        # Analyze repository
        git_analyzer = GitAnalyzer(repository_path)
        repo_info = {
            'name': os.path.basename(repository_path),
            'path': repository_path,
            'metadata': git_analyzer.get_repo_info()
        }
        
        # Get file hierarchy
        file_hierarchy = git_analyzer.get_file_tree()
        
        # Prioritize files
        file_prioritizer.configure_for_task(task_type)
        all_files = git_analyzer.get_tracked_files()
        included_files, _ = file_prioritizer.prioritize_files(
            all_files,
            token_budget
        )
        
        # Create context
        context = context_manager.create_context(
            task_type=task_type,
            repository_info=repo_info,
            file_hierarchy=file_hierarchy,
            selected_files=[f.path for f in included_files],
            token_budget=token_budget,
            model=model
        )
        
        # Format output
        format_type = FormatType(output_format)
        output = output_formatter.format_output(
            context.to_dict(),
            format_type
        )
        
        # Estimate tokens
        estimated_tokens = context_manager.estimate_context_tokens(context)
        
        return jsonify({
            'preview': output[:5000],  # Limit preview size
            'estimated_tokens': estimated_tokens,
            'included_files': len(included_files),
            'total_files': len(all_files)
        })
        
    except Exception as e:
        logger.error(f"Error previewing context: {e}")
        return jsonify({'error': str(e)}), 500


@llm_bp.route('/optimize-context', methods=['POST'])
def optimize_context():
    """Optimize existing context for token budget."""
    try:
        data = request.json
        
        # Extract parameters
        context_data = data.get('context')
        max_tokens = data.get('max_tokens')
        
        if not context_data or not max_tokens:
            return jsonify({'error': 'context and max_tokens are required'}), 400
        
        # Recreate context from data
        context = LLMContext(**context_data)
        
        # Optimize
        optimized = context_manager.optimize_context(context, max_tokens)
        
        # Return optimized context
        return jsonify({
            'optimized_context': optimized.to_dict(),
            'original_tokens': context_manager.estimate_context_tokens(context),
            'optimized_tokens': context_manager.estimate_context_tokens(optimized),
            'files_removed': len(context.selected_files) - len(optimized.selected_files)
        })
        
    except Exception as e:
        logger.error(f"Error optimizing context: {e}")
        return jsonify({'error': str(e)}), 500


@llm_bp.route('/task-profiles', methods=['GET'])
def get_task_profiles():
    """Get predefined task profiles for common use cases."""
    profiles = {
        'code_review': {
            'task_type': 'code_review',
            'model': 'gpt-4',
            'token_budget': 100000,
            'output_format': 'markdown',
            'focus_areas': ['*.py', '*.js', '*.ts'],
            'options': {
                'include_tests': True,
                'include_configs': False
            }
        },
        'bug_fixing': {
            'task_type': 'debug',
            'model': 'gpt-4',
            'token_budget': 80000,
            'output_format': 'structured_text',
            'focus_areas': ['error', 'exception', 'bug'],
            'options': {
                'include_logs': True,
                'include_tests': True
            }
        },
        'documentation': {
            'task_type': 'documentation',
            'model': 'gpt-3.5-turbo',
            'token_budget': 50000,
            'output_format': 'markdown',
            'focus_areas': ['*.md', 'README', '*.py'],
            'options': {
                'include_examples': True,
                'include_api_docs': True
            }
        },
        'security_scan': {
            'task_type': 'security_audit',
            'model': 'gpt-4',
            'token_budget': 100000,
            'output_format': 'json',
            'focus_areas': ['.env', 'config', 'auth', 'security'],
            'options': {
                'include_dependencies': True,
                'scan_vulnerabilities': True
            }
        }
    }
    
    return jsonify({'profiles': profiles})