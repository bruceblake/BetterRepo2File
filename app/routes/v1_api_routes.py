"""
Public API v1 Routes Blueprint for BetterRepo2File v2.0
Provides the standalone REST API for external integrations
"""
from flask import Blueprint, request, jsonify, Response, current_app, abort
from werkzeug.utils import secure_filename
import os
import sys
import uuid
import shutil
import base64
import tempfile
from datetime import datetime

api_v1_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')


@api_v1_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'BetterRepo2File API v1',
        'version': '2.0',
        'timestamp': datetime.utcnow().isoformat()
    })


@api_v1_bp.route('/modes', methods=['GET'])
def modes():
    """List available processing modes and their capabilities"""
    return jsonify({
        'modes': {
            'standard': {
                'description': 'Basic file consolidation',
                'token_aware': False,
                'ai_optimized': False,
                'supports_profiles': False
            },
            'smart': {
                'description': 'AI-optimized with intelligent filtering',
                'token_aware': False,
                'ai_optimized': True,
                'supports_profiles': False,
                'features': [
                    'Binary file detection',
                    'Intelligent truncation',
                    'Auto-generated file filtering',
                    'Lock file summarization'
                ]
            },
            'token': {
                'description': 'Token-aware with budget management',
                'token_aware': True,
                'ai_optimized': True,
                'supports_profiles': False,
                'default_budget': 500000
            },
            'ultra': {
                'description': 'Most advanced with exact token counting',
                'token_aware': True,
                'ai_optimized': True,
                'supports_profiles': True,
                'features': [
                    'Exact token counting',
                    'Semantic code analysis',
                    'Multi-model support',
                    'Caching system',
                    'Parallel processing',
                    'Advanced truncation'
                ],
                'supported_models': [
                    'gpt-4', 'gpt-3.5-turbo', 'claude-3',
                    'llama', 'gemini-1.5-pro'
                ]
            }
        }
    })


@api_v1_bp.route('/process', methods=['POST'])
def process():
    """
    Process files or GitHub repository asynchronously
    
    Request body:
    {
        "mode": "standard|smart|token|ultra",
        "github_url": "https://github.com/user/repo",  # OR
        "files": ["base64_encoded_file_contents"],
        "file_names": ["file1.py", "file2.js"],
        "options": {
            "file_types": [".py", ".js"],
            "use_gitignore": true,
            "github_branch": "develop",
            "model": "gpt-4",
            "token_budget": 500000,
            "profile": "frontend",
            "intended_query": "What you plan to ask the LLM"
        }
    }
    
    Returns:
    {
        "operation_id": "uuid",
        "status": "accepted"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        mode = data.get('mode', 'smart')
        valid_modes = ['standard', 'smart', 'token', 'ultra']
        if mode not in valid_modes:
            return jsonify({'error': f'Invalid mode: {mode}'}), 400
        
        job_manager = current_app.job_manager
        storage_manager = current_app.storage_manager
        
        # Determine input type
        if 'github_url' in data:
            # GitHub repository processing
            github_url = data['github_url']
            github_branch = data.get('options', {}).get('github_branch', 'main')
            
            input_repo_type = 'github_url'
            input_repo_ref = github_url
            
        elif 'files' in data and 'file_names' in data:
            # File upload processing
            files = data['files']
            file_names = data['file_names']
            
            if len(files) != len(file_names):
                return jsonify({'error': 'Files and file_names must have same length'}), 400
            
            # Create temporary directory
            temp_dir = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
            os.makedirs(temp_dir, exist_ok=True)
            
            # Save base64-encoded files
            for i, (file_content, file_name) in enumerate(zip(files, file_names)):
                try:
                    # Decode base64 content
                    decoded_content = base64.b64decode(file_content)
                    file_path = os.path.join(temp_dir, secure_filename(file_name))
                    
                    with open(file_path, 'wb') as f:
                        f.write(decoded_content)
                except Exception as e:
                    return jsonify({'error': f'Failed to decode file {file_name}: {str(e)}'}), 400
            
            # Upload to MinIO
            zip_path = shutil.make_archive(temp_dir, 'zip', temp_dir)
            minio_key = storage_manager.upload_data_stream(
                object_name=f"api-uploads/{os.path.basename(zip_path)}",
                data_stream=open(zip_path, 'rb'),
                length=os.path.getsize(zip_path)
            )
            
            input_repo_type = 'minio_file'
            input_repo_ref = minio_key
            
            # Cleanup
            shutil.rmtree(temp_dir)
            os.remove(zip_path)
            
        else:
            return jsonify({'error': 'Must provide either github_url or files/file_names'}), 400
        
        # Prepare processing options
        options = data.get('options', {})
        additional_options = {
            'file_types': options.get('file_types', []),
            'use_gitignore': options.get('use_gitignore', True),
            'profile': options.get('profile', '')
        }
        
        # Add mode-specific options
        if mode == 'ultra':
            additional_options.update({
                'llm_model': options.get('model', 'gpt-4'),
                'token_budget': options.get('token_budget', 500000),
                'intended_query': options.get('intended_query', ''),
                'generate_manifest': options.get('generate_manifest', True)
            })
        
        # Submit job to Celery
        job_id = job_manager.submit_repo_processing_job(
            input_repo_type=input_repo_type,
            input_repo_ref=input_repo_ref,
            github_branch=github_branch if input_repo_type == 'github_url' else None,
            processing_mode=mode,
            output_format='text',
            additional_options=additional_options
        )
        
        return jsonify({
            'operation_id': job_id,
            'status': 'accepted'
        }), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_v1_bp.route('/status/<operation_id>', methods=['GET'])
def status(operation_id):
    """
    Get the status of a processing operation
    
    Returns:
    {
        "status": "pending|processing|completed|failed",
        "progress": {
            "phase": "initializing|processing|uploading",
            "current": 50,
            "total": 100,
            "message": "Processing files..."
        }
    }
    """
    job_manager = current_app.job_manager
    
    try:
        job_status = job_manager.get_job_status(operation_id)
        
        # Map Celery states to API states
        state_mapping = {
            'PENDING': 'pending',
            'PROGRESS': 'processing',
            'SUCCESS': 'completed',
            'FAILURE': 'failed',
            'RETRY': 'processing',
            'REVOKED': 'failed'
        }
        
        response = {
            'status': state_mapping.get(job_status['state'], 'unknown')
        }
        
        # Add progress info if available
        if job_status['state'] == 'PROGRESS':
            response['progress'] = {
                'phase': job_status['info'].get('phase', 'unknown'),
                'current': job_status['info'].get('current', 0),
                'total': job_status['info'].get('total', 100),
                'message': job_status['info'].get('message', '')
            }
        elif job_status['state'] == 'FAILURE':
            response['error'] = job_status['info'].get('error', 'Unknown error')
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'Failed to get status: {str(e)}'}), 500


@api_v1_bp.route('/result/<operation_id>', methods=['GET'])
def result(operation_id):
    """
    Get the result of a completed operation
    
    Returns:
    {
        "status": "completed",
        "download_url": "pre-signed URL for downloading result",
        "expires_in": 3600,
        "metadata": {
            "processing_mode": "ultra",
            "file_count": 42,
            "total_tokens": 125000
        }
    }
    """
    job_manager = current_app.job_manager
    storage_manager = current_app.storage_manager
    
    try:
        # Check job status
        status = job_manager.get_job_status(operation_id)
        
        if status['state'] != 'SUCCESS':
            return jsonify({'error': 'Operation not completed'}), 400
        
        # Get job result
        result = job_manager.get_job_result(operation_id)
        if not result:
            return jsonify({'error': 'No result available'}), 404
        
        # Get output file reference
        output_files = result.get('output_files', {})
        if 'output.txt' not in output_files:
            return jsonify({'error': 'Output file not found'}), 404
        
        minio_key = output_files['output.txt']
        
        # Generate presigned URL
        download_url = storage_manager.generate_presigned_url(minio_key, expires_in=3600)
        
        return jsonify({
            'status': 'completed',
            'download_url': download_url,
            'expires_in': 3600,
            'metadata': {
                'processing_mode': result.get('processing_mode', 'unknown'),
                'job_id': operation_id,
                'additional_files': result.get('additional_files', [])
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get result: {str(e)}'}), 500


@api_v1_bp.route('/download/<operation_id>', methods=['GET'])
def download(operation_id):
    """
    Download the result file directly
    
    Returns: The processed file as an attachment
    """
    job_manager = current_app.job_manager
    storage_manager = current_app.storage_manager
    
    try:
        # Check job status
        status = job_manager.get_job_status(operation_id)
        if status['state'] != 'SUCCESS':
            abort(404)
        
        # Get result
        result = job_manager.get_job_result(operation_id)
        output_files = result.get('output_files', {})
        
        if 'output.txt' not in output_files:
            abort(404)
        
        minio_key = output_files['output.txt']
        
        # Stream from MinIO
        stream = storage_manager.download_stream(minio_key)
        return Response(
            stream,
            mimetype='text/plain',
            headers={
                'Content-Disposition': 'attachment; filename=repo2file_output.txt'
            }
        )
        
    except Exception as e:
        abort(404)


@api_v1_bp.route('/cleanup/<operation_id>', methods=['DELETE'])
def cleanup(operation_id):
    """
    Cleanup operation data and free resources
    
    Returns:
    {
        "status": "cleaned"
    }
    """
    job_manager = current_app.job_manager
    storage_manager = current_app.storage_manager
    
    try:
        # Get job result to find all files
        result = job_manager.get_job_result(operation_id)
        
        if result:
            # Delete all output files from MinIO
            output_files = result.get('output_files', {})
            for file_name, minio_key in output_files.items():
                try:
                    storage_manager.client.remove_object(
                        storage_manager.bucket_name,
                        minio_key
                    )
                except Exception as e:
                    print(f"Failed to delete {minio_key}: {e}")
        
        # Cleanup Celery task result
        job_manager.cleanup_job(operation_id)
        
        return jsonify({'status': 'cleaned'})
        
    except Exception as e:
        return jsonify({'error': f'Cleanup failed: {str(e)}'}), 500