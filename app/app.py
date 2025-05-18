import os
import sys
import tempfile
import uuid
import subprocess
import shutil
import time
import atexit
import json
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, jsonify, send_file, abort, Response
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import queue
import threading

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload size
app.config['UPLOAD_FOLDER'] = os.path.join(tempfile.gettempdir(), 'repo2file_uploads')
app.config['JOBS_FOLDER'] = os.path.join(tempfile.gettempdir(), 'repo2file_jobs')
app.config['REPO2FILE_PATH'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'repo2file', 'dump.py')
app.config['REPO2FILE_SMART_PATH'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'repo2file', 'dump_smart.py')
app.config['REPO2FILE_TOKEN_PATH'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'repo2file', 'dump_token_aware.py')
app.config['REPO2FILE_ULTRA_PATH'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'repo2file', 'dump_ultra.py')
app.config['EXCLUDE_FILE'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'repo2file', 'exclude.txt')

# Ensure temporary directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['JOBS_FOLDER'], exist_ok=True)

# Job storage
jobs = {}
job_queues = {}

def send_progress(job_id, phase, current=0, total=0):
    """Send progress update to the job queue"""
    if job_id in job_queues:
        jobs[job_id]['phase'] = phase
        jobs[job_id]['current'] = current
        jobs[job_id]['total'] = total
        job_queues[job_id].put({
            'phase': phase,
            'current': current,
            'total': total
        })

def process_job(job_id, job_folder, vibe, stage, repo_file, planner_output, previous_output, feedback_log):
    """Process a job in the background"""
    try:
        send_progress(job_id, 'extracting', 0, 0)
        
        # Handle file uploads
        repo_path = None
        if repo_file:
            if repo_file.filename.endswith('.zip'):
                # Extract zip
                zip_path = os.path.join(job_folder, 'repo.zip')
                repo_file.save(zip_path)
                
                import zipfile
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(os.path.join(job_folder, 'repo'))
                repo_path = os.path.join(job_folder, 'repo')
            else:
                # Save single file
                repo_path = os.path.join(job_folder, 'repo')
                os.makedirs(repo_path, exist_ok=True)
                repo_file.save(os.path.join(repo_path, repo_file.filename))
        
        # Save other uploaded files
        if previous_output:
            previous_output.save(os.path.join(job_folder, 'previous_output.txt'))
        if feedback_log:
            feedback_log.save(os.path.join(job_folder, 'feedback.log'))
        
        send_progress(job_id, 'analyzing', 0, 0)
        
        # Build repo2file command based on stage
        cmd = [sys.executable, app.config['REPO2FILE_ULTRA_PATH']]
        cmd.extend(['--profile', 'vibe_coder_gemini_claude'])
        cmd.extend(['--vibe', vibe])
        cmd.extend(['--output', os.path.join(job_folder, 'output.txt')])
        
        if stage == 'B' and planner_output:
            # Save planner output to file
            planner_file = os.path.join(job_folder, 'planner_output.txt')
            with open(planner_file, 'w') as f:
                f.write(planner_output)
            cmd.extend(['--planner', planner_file])
        
        elif stage == 'C':
            if previous_output:
                cmd.extend(['--iterate', os.path.join(job_folder, 'previous_output.txt')])
            if feedback_log:
                cmd.extend(['--feedback', os.path.join(job_folder, 'feedback.log')])
        
        cmd.append(repo_path or '.')
        
        # Run the analysis
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        if process.returncode != 0:
            raise Exception(f"Repo2File failed: {process.stderr}")
        
        send_progress(job_id, 'finalizing', 100, 100)
        
        # Read the output and parse sections
        output_file = os.path.join(job_folder, 'output.txt')
        with open(output_file, 'r') as f:
            full_content = f.read()
        
        # Parse sections (simplified for now)
        sections = {
            'copy_text': extract_copy_section(full_content, stage),
            'manifest_html': extract_manifest(full_content),
            'skipped_md': extract_skipped_report(full_content),
            'stats': extract_token_stats(full_content)
        }
        
        # Update job result
        jobs[job_id]['status'] = 'completed'
        jobs[job_id]['result'] = sections
        
    except Exception as e:
        jobs[job_id]['status'] = 'error'
        jobs[job_id]['error'] = str(e)
        send_progress(job_id, 'error', 0, 0)
    
    finally:
        if job_id in job_queues:
            job_queues[job_id].put('END')

def extract_copy_section(content, stage):
    """Extract the section that should be copied to AI"""
    # Simple extraction for now - we'll refine this based on actual output format
    if stage == 'A':
        # Extract planning section
        return content
    elif stage == 'B':
        # Extract coding section 
        return content
    else:
        # Extract iteration section
        return content

def extract_manifest(content):
    """Extract and format the manifest as HTML"""
    # Simple extraction for now
    return "<pre>" + content[:5000] + "</pre>"

def extract_skipped_report(content):
    """Extract the skipped files report"""
    # Look for skip report section
    if "SKIPPED FILES REPORT" in content:
        start = content.find("SKIPPED FILES REPORT")
        end = content.find("\n\n", start)
        return content[start:end] if end > start else content[start:]
    return "No files were skipped."

def extract_token_stats(content):
    """Extract token usage statistics"""
    # Simple extraction for now
    stats = {
        'used': 0,
        'budget': 2000000
    }
    
    # Look for token stats
    if "Token usage:" in content:
        # Parse actual stats from output
        pass
    
    return stats

# Setup background cleanup job
def cleanup_old_dirs():
    current_time = time.time()
    for dir_name in os.listdir(app.config['UPLOAD_FOLDER']):
        dir_path = os.path.join(app.config['UPLOAD_FOLDER'], dir_name)
        if os.path.isdir(dir_path) and (current_time - os.path.getmtime(dir_path)) > 3600:  # 1 hour
            try:
                shutil.rmtree(dir_path)
            except Exception:
                pass

# Run cleanup every hour
scheduler = BackgroundScheduler()
scheduler.add_job(cleanup_old_dirs, 'interval', hours=1)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

@app.route('/')
def index():
    return render_template('index.html')

# New UI API endpoints
@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Start a new analysis job"""
    job_id = str(uuid.uuid4())
    job_queue = queue.Queue()
    job_queues[job_id] = job_queue
    
    # Get form data
    vibe = request.form.get('vibe', '')
    stage = request.form.get('stage', 'A')
    repo_file = request.files.get('repo_zip')
    planner_output = request.form.get('planner_output', '')
    previous_output = request.files.get('previous_output')
    feedback_log = request.files.get('feedback_log')
    
    # Create job folder
    job_folder = os.path.join(app.config['JOBS_FOLDER'], job_id)
    os.makedirs(job_folder, exist_ok=True)
    
    # Initialize job status
    jobs[job_id] = {
        'status': 'processing',
        'phase': 'initializing',
        'current': 0,
        'total': 0,
        'error': None,
        'result': None
    }
    
    # Start processing in background thread
    thread = threading.Thread(target=process_job, args=(job_id, job_folder, vibe, stage, repo_file, planner_output, previous_output, feedback_log))
    thread.start()
    
    return jsonify({'job_id': job_id}), 200

@app.route('/api/status/<job_id>')
def status(job_id):
    """Server-sent events for job progress"""
    def generate():
        if job_id not in job_queues:
            yield f"data: {json.dumps({'error': 'Invalid job ID'})}\n\n"
            return
            
        q = job_queues[job_id]
        while True:
            try:
                event = q.get(timeout=30)  # 30 second timeout
                if event == 'END':
                    break
                yield f"data: {json.dumps(event)}\n\n"
            except queue.Empty:
                yield f"data: {json.dumps({'keepalive': True})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/result/<job_id>')
def result(job_id):
    """Get the final result of a job"""
    if job_id not in jobs:
        return jsonify({'error': 'Invalid job ID'}), 404
    
    job = jobs[job_id]
    if job['status'] == 'processing':
        return jsonify({'error': 'Job still processing'}), 202
    
    if job['status'] == 'error':
        return jsonify({'error': job['error']}), 500
    
    return jsonify(job['result']), 200

@app.route('/process', methods=['POST'])
def process():
    # Create a unique ID for this operation
    operation_id = str(uuid.uuid4())
    temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], operation_id)
    os.makedirs(temp_dir, exist_ok=True)
    
    output_file = os.path.join(temp_dir, 'output.txt')
    
    try:
        if 'files[]' in request.files:
            # Handle file uploads
            files = request.files.getlist('files[]')
            if not files or files[0].filename == '':
                return jsonify({"error": "No files selected"}), 400
            
            upload_dir = os.path.join(temp_dir, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            for file in files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(upload_dir, filename)
                    file.save(file_path)
            
            input_path = upload_dir
        
        elif 'github_url' in request.form and request.form['github_url']:
            # Handle GitHub repository URL
            github_url = request.form['github_url']
            github_branch = request.form.get('github_branch', '').strip()
            repo_dir = os.path.join(temp_dir, 'repo')
            
            # Clone the repository
            try:
                # Clone with specific branch if provided
                if github_branch:
                    subprocess.run(['git', 'clone', '-b', github_branch, github_url, repo_dir], 
                                  check=True, capture_output=True, text=True)
                else:
                    subprocess.run(['git', 'clone', github_url, repo_dir], 
                                  check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                return jsonify({"error": f"Failed to clone repository: {e.stderr}"}), 400
            
            input_path = repo_dir
        
        else:
            return jsonify({"error": "No input provided. Please upload files or provide a GitHub URL."}), 400
        
        # Determine if file types were specified
        file_types = []
        if 'file_types' in request.form and request.form['file_types']:
            file_types = request.form['file_types'].split()
        
        # Check for .gitignore in the input directory
        gitignore_path = os.path.join(input_path, '.gitignore')
        use_gitignore = request.form.get('use_gitignore', 'true').lower() in ('true', 't', 'yes', 'y', '1', 'on')
        use_smart_mode = request.form.get('smart_mode', 'true').lower() in ('true', 't', 'yes', 'y', '1', 'on')
        
        # Determine which exclusion file to use
        if use_gitignore and os.path.exists(gitignore_path):
            exclusion_file = gitignore_path
        else:
            exclusion_file = app.config['EXCLUDE_FILE']
        
        # Check for token-aware mode
        use_token_mode = request.form.get('token_mode', 'false').lower() in ('true', 't', 'yes', 'y', '1', 'on')
        use_ultra_mode = request.form.get('ultra_mode', 'false').lower() in ('true', 't', 'yes', 'y', '1', 'on')
        
        # Get profile if selected
        profile = request.form.get('profile', '')
        
        # Determine which script to use
        if use_ultra_mode:
            script_path = app.config['REPO2FILE_ULTRA_PATH']
            # Add model and token budget options
            llm_model = request.form.get('llm_model', 'gpt-4')
            token_budget = request.form.get('token_budget', '500000')
        elif use_token_mode:
            script_path = app.config['REPO2FILE_TOKEN_PATH']
        else:
            script_path = app.config['REPO2FILE_SMART_PATH'] if use_smart_mode else app.config['REPO2FILE_PATH']
        
        # Prepare command to run repo2file
        if use_ultra_mode:
            # Run as module to avoid import issues
            cmd = [
                sys.executable,  # Python interpreter
                '-m', 'repo2file.dump_ultra',
                input_path,  # Input directory
                output_file,  # Output file
            ]
        else:
            cmd = [
                sys.executable,  # Python interpreter
                script_path,  # Path to dump.py or dump_smart.py
                input_path,  # Input directory
                output_file,  # Output file
            ]
        
        # Add options based on version
        if use_ultra_mode:
            if profile:
                cmd.extend(['--profile', profile])
            # Only add model and budget if they differ from profile defaults or no profile
            if llm_model and (not profile or llm_model != 'gpt-4'):
                cmd.extend(['--model', llm_model])
            if token_budget != '500000':
                cmd.extend(['--budget', token_budget])
            # Add intended query if provided
            intended_query = request.form.get('intended_query', '').strip()
            if intended_query:
                cmd.extend(['--query', intended_query])
            
            # Add vibe statement if provided
            vibe_statement = request.form.get('vibe_statement', '').strip()
            if vibe_statement:
                cmd.extend(['--vibe', vibe_statement])
            
            # Add planner output if provided
            planner_output = request.form.get('planner_output', '').strip()
            if planner_output:
                # Save planner output to a temporary file
                planner_file = os.path.join(temp_dir, 'planner_output.txt')
                with open(planner_file, 'w') as f:
                    f.write(planner_output)
                cmd.extend(['--planner', planner_file])
        else:
            cmd.append(exclusion_file)  # Exclusion file (either .gitignore or default)
        
        # Add file types if specified
        if file_types and not use_ultra_mode:
            cmd.extend(file_types)
        
        # Run repo2file script
        process = subprocess.run(
            cmd,
            check=False,  # Don't raise exception, handle error manually
            capture_output=True,
            text=True
        )
        
        if process.returncode != 0:
            error_msg = process.stderr if process.stderr else process.stdout
            return jsonify({"error": f"Script failed: {error_msg}"}), 500
        
        # Check if output file was created
        if not os.path.exists(output_file):
            return jsonify({"error": "Failed to generate output file"}), 500
        
        # Read the content of the output file
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Determine which exclusion file and mode was used
        used_gitignore = exclusion_file == gitignore_path
        
        return jsonify({
            "success": True,
            "operation_id": operation_id,
            "content": content,
            "used_gitignore": used_gitignore,
            "exclusion_file": os.path.basename(exclusion_file),
            "smart_mode": use_smart_mode,
            "token_mode": use_token_mode,
            "ultra_mode": use_ultra_mode,
            "llm_model": llm_model if use_ultra_mode else None,
            "token_budget": token_budget if use_ultra_mode else None
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/<operation_id>')
def download(operation_id):
    # Validate operation_id to prevent directory traversal
    if not operation_id or not all(c.isalnum() or c == '-' for c in operation_id):
        abort(400)
    
    output_file = os.path.join(app.config['UPLOAD_FOLDER'], operation_id, 'output.txt')
    
    if not os.path.exists(output_file):
        abort(404)
    
    return send_file(output_file, as_attachment=True, download_name='repo2file_output.txt')

@app.route('/preview', methods=['POST'])
def preview():
    """Generate a quick preview of the first few files"""
    try:
        # Similar to process but limited
        temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'preview_' + str(uuid.uuid4()))
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

@app.route('/cleanup', methods=['POST'])
def cleanup():
    operation_id = request.json.get('operation_id')
    
    # Validate operation_id to prevent directory traversal
    if not operation_id or not all(c.isalnum() or c == '-' for c in operation_id):
        return jsonify({"error": "Invalid operation ID"}), 400
    
    temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], operation_id)
    
    if os.path.exists(temp_dir):
        try:
            shutil.rmtree(temp_dir)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"error": f"Failed to cleanup: {str(e)}"}), 500
    
    return jsonify({"success": True})

# Import API blueprint
try:
    from api import api
    app.register_blueprint(api)
except ImportError:
    pass  # API module not available

# Import profiles blueprint
try:
    from profiles import profiles_api
    app.register_blueprint(profiles_api)
except ImportError:
    pass  # Profiles module not available

if __name__ == '__main__':
    print("Starting BetterRepo2File UI server...")
    print("Access the application at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)