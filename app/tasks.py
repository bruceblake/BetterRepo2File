"""
Celery tasks for RobustRepo v2.0
"""
import os
import sys
import tempfile
import shutil
import subprocess
from typing import Dict, Any, Optional
from .celery_app import celery_app
from .storage_manager import StorageManager
from .logger import logger
import git

# Add parent directory to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@celery_app.task(bind=True, name='process_repository_task', queue='default')
def process_repository_task(
    self,
    input_repo_type: str,
    input_repo_ref: str,
    github_branch: Optional[str] = None,
    processing_mode: str = 'standard',
    output_format: str = 'text',
    additional_options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process a repository asynchronously using repo2file
    
    Args:
        input_repo_type: Type of input ('github_url', 'local_path', 'minio_file')
        input_repo_ref: Reference to the input (URL, path, or MinIO key)
        github_branch: GitHub branch to use (if input is GitHub URL)
        processing_mode: Processing mode ('standard', 'smart', 'token', 'ultra', 'context_generation')
        output_format: Output format ('text', 'json', 'markdown')
        additional_options: Additional processing options
        
    Returns:
        dict: Processing result with output file references
    """
    storage_manager = StorageManager()
    temp_dir = None
    
    try:
        # Update task state to show initialization
        self.update_state(
            state='PROGRESS',
            meta={
                'phase': 'initializing',
                'current': 0,
                'total': 100,
                'message': 'Setting up repository processing'
            }
        )
        
        # Create temporary working directory
        temp_dir = tempfile.mkdtemp(prefix='repo2file_')
        logger.info(f"Processing job in temporary directory: {temp_dir}")
        
        # Step 1: Prepare input repository
        self.update_state(
            state='PROGRESS',
            meta={
                'phase': 'preparing_input',
                'current': 10,
                'total': 100,
                'message': 'Preparing input repository'
            }
        )
        
        if input_repo_type == 'github_url':
            # Clone GitHub repository
            repo_dir = os.path.join(temp_dir, 'repo')
            logger.info(f"Cloning GitHub repository: {input_repo_ref}")
            
            if github_branch:
                git.Repo.clone_from(input_repo_ref, repo_dir, branch=github_branch)
            else:
                git.Repo.clone_from(input_repo_ref, repo_dir)
            
            input_path = repo_dir
            
        elif input_repo_type == 'minio_file':
            # Download from MinIO
            logger.info(f"Downloading from MinIO: {input_repo_ref}")
            local_file = os.path.join(temp_dir, 'input.zip')
            storage_manager.download_file(input_repo_ref, local_file)
            
            # Extract zip file
            extract_dir = os.path.join(temp_dir, 'extracted')
            shutil.unpack_archive(local_file, extract_dir)
            input_path = extract_dir
            
        elif input_repo_type == 'local_path':
            input_path = input_repo_ref
        
        else:
            raise ValueError(f"Unknown input repository type: {input_repo_type}")
        
        # Step 2: Process repository
        self.update_state(
            state='PROGRESS',
            meta={
                'phase': 'processing',
                'current': 30,
                'total': 100,
                'message': f'Processing repository with {processing_mode} mode'
            }
        )
        
        output_file = os.path.join(temp_dir, 'output.txt')
        
        # Select appropriate dump script based on mode
        mode_scripts = {
            'standard': 'repo2file/dump.py',
            'smart': 'repo2file/dump_smart.py',
            'token': 'repo2file/dump_token_aware.py',
            'ultra': 'repo2file/dump_ultra.py'
        }
        
        if processing_mode not in mode_scripts:
            raise ValueError(f"Invalid processing mode: {processing_mode}")
        
        script_path = mode_scripts[processing_mode]
        
        # Build command
        cmd = [
            sys.executable,
            script_path,
            input_path,
            output_file
        ]
        
        # Add additional options for ultra mode
        if processing_mode == 'ultra' and additional_options:
            if 'model' in additional_options:
                cmd.extend(['--model', additional_options['model']])
            if 'token_budget' in additional_options:
                cmd.extend(['--budget', str(additional_options['token_budget'])])
            if 'binary_files' in additional_options:
                cmd.extend(['--binary-files', additional_options['binary_files']])
            if 'include_tests' in additional_options and additional_options['include_tests']:
                cmd.append('--include-tests')
            if 'semantic_analysis' in additional_options and additional_options['semantic_analysis']:
                cmd.append('--semantic-analysis')
        
        # Add file extensions if specified
        if additional_options and 'file_extensions' in additional_options:
            cmd.extend(additional_options['file_extensions'])
        
        # Execute processing
        logger.info(f"Executing command: {' '.join(cmd)}")
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if process.returncode != 0:
            error_msg = process.stderr if process.stderr else process.stdout
            raise Exception(f"Processing failed: {error_msg}")
        
        # Verify output was created
        if not os.path.exists(output_file):
            raise Exception("Failed to generate output file")
        
        # Step 3: Upload results to MinIO
        self.update_state(
            state='PROGRESS',
            meta={
                'phase': 'uploading_results',
                'current': 80,
                'total': 100,
                'message': 'Uploading results to storage'
            }
        )
        
        # Upload main output file
        output_key = f"outputs/{self.request.id}/output.txt"
        with open(output_file, 'rb') as f:
            storage_manager.upload_data_stream(
                object_name=output_key,
                data_stream=f,
                length=os.path.getsize(output_file)
            )
        
        output_files = {'output.txt': output_key}
        
        # Upload additional outputs if any
        additional_files = []
        
        # Check for manifest file (ultra mode)
        manifest_file = os.path.join(temp_dir, 'manifest.json')
        if os.path.exists(manifest_file):
            manifest_key = f"outputs/{self.request.id}/manifest.json"
            with open(manifest_file, 'rb') as f:
                storage_manager.upload_data_stream(
                    object_name=manifest_key,
                    data_stream=f,
                    length=os.path.getsize(manifest_file)
                )
            output_files['manifest.json'] = manifest_key
            additional_files.append('manifest.json')
        
        # Step 4: Prepare final result
        result = {
            'job_id': self.request.id,
            'status': 'success',
            'output_files': output_files,
            'additional_files': additional_files,
            'processing_mode': processing_mode,
            'output_format': output_format,
            'metadata': {
                'input_type': input_repo_type,
                'branch': github_branch if github_branch else 'default'
            }
        }
        
        # Add session ID if provided
        if additional_options and 'session_id' in additional_options:
            result['session_id'] = additional_options['session_id']
        
        # Update final state
        self.update_state(
            state='PROGRESS',
            meta={
                'phase': 'completed',
                'current': 100,
                'total': 100,
                'message': 'Processing completed successfully'
            }
        )
        
        logger.info(f"Job {self.request.id} completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Error processing repository: {e}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise
        
    finally:
        # Cleanup temporary directory
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                logger.error(f"Failed to cleanup temp directory: {e}")


@celery_app.task(bind=True, name='generate_llm_context_task', queue='default')
def generate_llm_context_task(
    self,
    repository_path: str,
    task_type: str,
    model: str,
    token_budget: int,
    output_format: str,
    focus_areas: list = None,
    additional_options: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Generate optimized context for LLM consumption
    
    Args:
        repository_path: Path to repository
        task_type: Type of task (code_review, debug, etc.)
        model: LLM model name
        token_budget: Token budget for context
        output_format: Output format
        focus_areas: Areas to focus on
        additional_options: Additional options
        
    Returns:
        dict: Processing result with context files
    """
    from app.llm_helpers import (
        ContextManager,
        FilePrioritizer,
        PromptTemplateManager,
        OutputFormatter,
        TaskType,
        FormatType
    )
    from repo2file.git_analyzer import GitAnalyzer
    
    storage_manager = StorageManager()
    temp_dir = None
    
    try:
        # Initialize components
        context_manager = ContextManager()
        file_prioritizer = FilePrioritizer()
        prompt_manager = PromptTemplateManager()
        output_formatter = OutputFormatter()
        
        # Create temporary working directory
        temp_dir = tempfile.mkdtemp(prefix='llm_context_')
        logger.info(f"Generating LLM context in: {temp_dir}")
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={
                'phase': 'analyzing_repository',
                'current': 20,
                'total': 100,
                'message': 'Analyzing repository structure'
            }
        )
        
        # Analyze repository
        git_analyzer = GitAnalyzer(repository_path)
        repo_info = {
            'name': os.path.basename(repository_path),
            'path': repository_path,
            'metadata': git_analyzer.get_repo_info()
        }
        
        # Get file hierarchy and list
        file_hierarchy = git_analyzer.get_file_tree()
        all_files = git_analyzer.get_tracked_files()
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={
                'phase': 'prioritizing_files',
                'current': 40,
                'total': 100,
                'message': 'Prioritizing files for task'
            }
        )
        
        # Configure and run file prioritization
        file_prioritizer.configure_for_task(
            task_type,
            focus_patterns=focus_areas or [],
            exclude_patterns=additional_options.get('exclude_patterns', []) if additional_options else []
        )
        
        included_files, excluded_files = file_prioritizer.prioritize_files(
            all_files,
            token_budget
        )
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={
                'phase': 'creating_context',
                'current': 60,
                'total': 100,
                'message': 'Creating LLM context'
            }
        )
        
        # Create context
        context = context_manager.create_context(
            task_type=task_type,
            repository_info=repo_info,
            file_hierarchy=file_hierarchy,
            selected_files=[f.path for f in included_files],
            token_budget=token_budget,
            model=model,
            additional_metadata={
                'focus_areas': focus_areas or [],
                'excluded_files': len(excluded_files),
                'total_files': len(all_files)
            }
        )
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={
                'phase': 'formatting_output',
                'current': 80,
                'total': 100,
                'message': 'Formatting output'
            }
        )
        
        # Format output
        format_type = FormatType(output_format)
        formatted_output = output_formatter.format_output(
            context.to_dict(),
            format_type
        )
        
        # Save formatted output
        output_file = os.path.join(temp_dir, f'llm_context.{output_format}')
        with open(output_file, 'w') as f:
            f.write(formatted_output)
        
        # Generate prompt template if requested
        prompt_file = None
        if additional_options and additional_options.get('include_prompt'):
            prompt = prompt_manager.create_context_prompt(
                context,
                task_specific_vars=additional_options.get('prompt_vars', {})
            )
            prompt_file = os.path.join(temp_dir, 'prompt.txt')
            with open(prompt_file, 'w') as f:
                f.write(prompt)
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={
                'phase': 'uploading_results',
                'current': 90,
                'total': 100,
                'message': 'Uploading results to storage'
            }
        )
        
        # Upload to MinIO
        context_key = f"llm_contexts/{self.request.id}/context.{output_format}"
        with open(output_file, 'rb') as f:
            storage_manager.upload_data_stream(
                object_name=context_key,
                data_stream=f,
                length=os.path.getsize(output_file)
            )
        
        output_files = {'context': context_key}
        
        if prompt_file:
            prompt_key = f"llm_contexts/{self.request.id}/prompt.txt"
            with open(prompt_file, 'rb') as f:
                storage_manager.upload_data_stream(
                    object_name=prompt_key,
                    data_stream=f,
                    length=os.path.getsize(prompt_file)
                )
            output_files['prompt'] = prompt_key
        
        # Prepare result
        result = {
            'job_id': self.request.id,
            'status': 'success',
            'output_files': output_files,
            'task_type': task_type,
            'model': model,
            'token_budget': token_budget,
            'estimated_tokens': context_manager.estimate_context_tokens(context),
            'files_included': len(included_files),
            'files_excluded': len(excluded_files),
            'total_files': len(all_files)
        }
        
        # Update final state
        self.update_state(
            state='PROGRESS',
            meta={
                'phase': 'completed',
                'current': 100,
                'total': 100,
                'message': 'LLM context generation completed'
            }
        )
        
        logger.info(f"LLM context job {self.request.id} completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Error generating LLM context: {e}")
        self.update_state(
            state='FAILURE',
            meta={'error': str(e)}
        )
        raise
        
    finally:
        # Cleanup
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                logger.error(f"Failed to cleanup temp directory: {e}")