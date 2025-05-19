"""
Job API Routes Blueprint for BetterRepo2File v2.0
Handles internal API routes for job management and processing
"""
from flask import Blueprint, request, jsonify, Response, abort, current_app
from werkzeug.utils import secure_filename
import os
import sys
import uuid
import shutil
import json
import time

job_api_bp = Blueprint('job_api', __name__, url_prefix='/api')


@job_api_bp.route('/process', methods=['POST'])
def process():
    """Process files or GitHub repository using Celery async tasks"""
    try:
        job_manager = current_app.job_manager
        storage_manager = current_app.storage_manager
        
        github_branch = None  # Initialize variable
        
        # Determine input type and prepare input reference
        if 'files[]' in request.files:
            # Handle file uploads
            files = request.files.getlist('files[]')
            if not files or files[0].filename == '':
                return jsonify({"error": "No files selected"}), 400
            
            # Create temporary directory for uploads
            temp_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(uuid.uuid4()))
            os.makedirs(temp_dir, exist_ok=True)
            
            # Save files to temp directory
            for file in files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(temp_dir, filename)
                    file.save(file_path)
            
            # Upload to MinIO
            zip_path = shutil.make_archive(temp_dir, 'zip', temp_dir)
            minio_key = storage_manager.upload_data_stream(
                object_name=f"uploads/{os.path.basename(zip_path)}",
                data_stream=open(zip_path, 'rb'),
                length=os.path.getsize(zip_path)
            )
            
            input_repo_type = 'minio_file'
            input_repo_ref = minio_key
            
            # Cleanup temp files
            shutil.rmtree(temp_dir)
            os.remove(zip_path)
        
        elif 'github_url' in request.form and request.form['github_url']:
            # Handle GitHub repository URL
            github_url = request.form['github_url']
            github_branch = request.form.get('github_branch', '').strip() or 'main'
            
            input_repo_type = 'github_url'
            input_repo_ref = github_url
        
        else:
            return jsonify({"error": "No input provided. Please upload files or provide a GitHub URL."}), 400
        
        # Get processing options from form
        file_types = request.form.get('file_types', '').split() if request.form.get('file_types') else []
        use_gitignore = request.form.get('use_gitignore', 'true').lower() in ('true', 't', 'yes', 'y', '1', 'on')
        use_smart_mode = request.form.get('smart_mode', 'true').lower() in ('true', 't', 'yes', 'y', '1', 'on')
        use_token_mode = request.form.get('token_mode', 'false').lower() in ('true', 't', 'yes', 'y', '1', 'on')
        use_ultra_mode = request.form.get('ultra_mode', 'false').lower() in ('true', 't', 'yes', 'y', '1', 'on')
        profile = request.form.get('profile', '')
        
        # Determine processing mode
        processing_mode = 'standard'
        if use_ultra_mode:
            processing_mode = 'ultra'
        elif use_token_mode:
            processing_mode = 'token'
        elif use_smart_mode:
            processing_mode = 'smart'
        
        # Prepare additional options
        additional_options = {
            'file_types': file_types,
            'use_gitignore': use_gitignore,
            'profile': profile
        }
        
        # Add ultra mode specific options
        if use_ultra_mode:
            additional_options.update({
                'llm_model': request.form.get('llm_model', 'gpt-4'),
                'token_budget': int(request.form.get('token_budget', '500000')),
                'intended_query': request.form.get('intended_query', '').strip(),
                'vibe_statement': request.form.get('vibe_statement', '').strip(),
                'planner_output': request.form.get('planner_output', '').strip()
            })
        
        # Submit job to Celery
        job_id = job_manager.submit_repo_processing_job(
            input_repo_type=input_repo_type,
            input_repo_ref=input_repo_ref,
            github_branch=github_branch if input_repo_type == 'github_url' else None,
            processing_mode=processing_mode,
            output_format='text',
            additional_options=additional_options
        )
        
        return jsonify({
            "success": True,
            "job_id": job_id,
            "processing_mode": processing_mode
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@job_api_bp.route('/generate_context', methods=['POST'])
def generate_context():
    """Generate context for different stages of the workflow using Celery tasks"""
    try:
        data = request.get_json()
        print(f"Received generate_context request: {data}")
        
        repo_url = data.get('repo_url')
        repo_branch = data.get('repo_branch', 'main')
        vibe = data.get('vibe')
        stage = data.get('stage')
        planner_output = data.get('planner_output', '') or data.get('previous_planner_output', '')
        feedback_log = data.get('feedback_log', '')
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        print(f"Parameters: repo_url={repo_url}, branch={repo_branch}, stage={stage}")
        
        # Use JobManager to submit async task
        job_manager = current_app.job_manager
        
        # Submit repository processing job to Celery
        job_id = job_manager.submit_repo_processing_job(
            input_repo_type='github_url',
            input_repo_ref=repo_url,
            github_branch=repo_branch,
            processing_mode='context_generation',
            output_format='markdown',
            additional_options={
                'vibe': vibe,
                'stage': stage,
                'planner_output': planner_output,
                'feedback_log': feedback_log,
                'session_id': session_id
            }
        )
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'session_id': session_id
        })
        
    except Exception as e:
        print(f"Error in generate_context: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@job_api_bp.route('/job_status/<job_id>')
def job_status(job_id):
    """Stream job status updates using Server-Sent Events for Celery tasks"""
    # Capture the job manager outside the generator to avoid context issues
    job_manager = current_app.job_manager
    
    def generate():
        last_state = None
        
        while True:
            try:
                # Get job status from Celery via JobManager
                status = job_manager.get_job_status(job_id)
                
                # Only send update if state changed
                if status['state'] != last_state:
                    last_state = status['state']
                    yield f"data: {json.dumps(status)}\n\n"
                
                # If job is complete, send result and finish
                if status['state'] in ['SUCCESS', 'FAILURE']:
                    result = job_manager.get_job_result(job_id)
                    yield f"data: {json.dumps(result)}\n\n"
                    break
                
                # Check for specific progress updates
                if status['state'] == 'PROGRESS':
                    yield f"data: {json.dumps(status)}\n\n"
                
                time.sleep(1)  # Poll every second
                
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                break
                
    return Response(generate(), content_type='text/event-stream')


@job_api_bp.route('/result/<job_id>')
def result(job_id):
    """Get the final result of a Celery job with MinIO output file references"""
    job_manager = current_app.job_manager
    storage_manager = current_app.storage_manager
    
    # Get job status from Celery
    status = job_manager.get_job_status(job_id)
    
    if not status:
        return jsonify({'error': 'Invalid job ID'}), 404
    
    # Check if job is still processing
    if status['state'] in ['PENDING', 'PROGRESS', 'RETRY']:
        return jsonify({'status': status['state'], 'info': status.get('info')}), 202
    
    # Check if job failed
    if status['state'] == 'FAILURE':
        return jsonify({'error': status.get('info', 'Job failed')}), 500
    
    # Job succeeded - get result
    result = job_manager.get_job_result(job_id)
    if not result:
        return jsonify({'error': 'No result available'}), 404
    
    # Extract output file references from result
    output_files = result.get('output_files', {})
    
    # Generate access URLs for each output file
    file_access = {}
    for name, minio_key in output_files.items():
        try:
            # Generate presigned URL for download
            presigned_url = storage_manager.generate_presigned_url(minio_key)
            file_access[name] = {
                'minio_key': minio_key,
                'download_url': presigned_url
            }
        except Exception as e:
            file_access[name] = {
                'minio_key': minio_key,
                'error': f'Failed to generate download URL: {str(e)}'
            }
    
    return jsonify({
        'status': 'completed',
        'result': result,
        'file_access': file_access
    }), 200


@job_api_bp.route('/download/<job_id>')
def download(job_id):
    """Download processed output file from MinIO via job result"""
    storage_manager = current_app.storage_manager
    job_manager = current_app.job_manager
    
    # Validate job_id
    if not job_id or not all(c.isalnum() or c == '-' for c in job_id):
        abort(400)
    
    # Get job result to find output file reference
    try:
        status = job_manager.get_job_status(job_id)
        if status['state'] != 'SUCCESS':
            abort(404)
        
        result = job_manager.get_job_result(job_id)
        output_files = result.get('output_files', {})
        
        # Get the main output file (typically 'output.txt')
        if 'output.txt' in output_files:
            minio_key = output_files['output.txt']
        else:
            # Fallback to first file if specific name not found
            minio_key = list(output_files.values())[0]
        
        # Download from MinIO and stream to client
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


@job_api_bp.route('/preview', methods=['POST'])
def preview():
    """Generate a quick preview of the first few files"""
    try:
        # Similar to process but limited
        temp_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'preview_' + str(uuid.uuid4()))
        os.makedirs(temp_dir, exist_ok=True)
        
        # Get form data
        file_types = []
        if 'file_types' in request.form and request.form['file_types']:
            file_types = request.form['file_types'].split()
        
        # For preview, just list files that would be included
        files_to_preview = []
        
        if 'files[]' in request.files:
            files = request.files.getlist('files[]')
            for file in files[:10]:  # Limit to 10 files for preview
                if file and file.filename:
                    files_to_preview.append({
                        'name': file.filename,
                        'size': len(file.read()),
                        'type': os.path.splitext(file.filename)[1]
                    })
                    file.seek(0)  # Reset file pointer
        
        return jsonify({
            'success': True,
            'files': files_to_preview,
            'total_files': len(files_to_preview)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Cleanup preview directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)