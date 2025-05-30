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

# Add parent directory to Python path for module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, jsonify, send_file, abort, Response
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import queue
import threading
import git

# Handle relative imports when running as module vs directly
if __name__ == '__main__':
    from logger import iteration_logger, log_iteration_start, log_step, log_error, log_metric, log_iteration_end
    from diff_visualizer import diff_visualizer, get_file_diff, get_git_diff
    from test_executor import test_executor, detect_test_framework, run_tests
    from job_manager import JobManager
    from storage_manager import StorageManager
else:
    from .logger import iteration_logger, log_iteration_start, log_step, log_error, log_metric, log_iteration_end
    from .diff_visualizer import diff_visualizer, get_file_diff, get_git_diff
    from .test_executor import test_executor, detect_test_framework, run_tests
    from .job_manager import JobManager
    from .storage_manager import StorageManager

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

# Session storage for Vibe Coder Loop
sessions = {}

def save_session_data(session_id: str, session_data: dict):
    """Save session data to file"""
    session_dir = os.path.join(app.config['UPLOAD_FOLDER'], f'session_{session_id}')
    os.makedirs(session_dir, exist_ok=True)
    
    session_file = os.path.join(session_dir, 'session_data.json')
    with open(session_file, 'w') as f:
        json.dump(session_data, f, indent=2)

def load_session_data(session_id: str) -> dict:
    """Load session data from file"""
    session_file = os.path.join(app.config['UPLOAD_FOLDER'], f'session_{session_id}', 'session_data.json')
    if os.path.exists(session_file):
        with open(session_file, 'r') as f:
            return json.load(f)
    return None

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

def process_job(job_id, job_folder, vibe, stage, repo_file, planner_output, previous_output, feedback_log, repo_type=None, repo_path_input=None, repo_url=None, repo_branch=None):
    """Process a job in the background"""
    print(f"Starting job {job_id} with stage {stage}, repo_url: {repo_url}, branch: {repo_branch}")
    
    # Start iteration logging
    iteration_description = f"Stage {stage} - {repo_url or repo_path_input or 'unknown repo'}"
    log_iteration_start(job_id, iteration_description)
    
    try:
        send_progress(job_id, 'extracting', 0, 0)
        log_step("Starting extraction phase", {
            "stage": stage,
            "repo_type": repo_type,
            "repo_url": repo_url,
            "repo_branch": repo_branch
        })
        
        # Handle repository selection
        repo_path = None
        
        if repo_type == 'local' and repo_path_input:
            # Use local repository path
            repo_path = repo_path_input
            if not os.path.exists(repo_path):
                raise Exception(f"Local repository path does not exist: {repo_path}")
            log_step("Using local repository", {"path": repo_path})
                
        elif repo_type == 'github' and repo_url:
            # Clone GitHub repository
            repo_path = os.path.join(job_folder, 'repo')
            print(f"Cloning GitHub repo: {repo_url} to {repo_path}")
            log_step("Cloning GitHub repository", {
                "url": repo_url,
                "branch": repo_branch,
                "destination": repo_path
            })
            
            try:
                if repo_branch:
                    # Clone specific branch
                    print(f"Cloning branch: {repo_branch}")
                    result = subprocess.run(['git', 'clone', '-b', repo_branch, repo_url, repo_path], 
                                  check=True, capture_output=True, text=True)
                else:
                    # Clone default branch
                    result = subprocess.run(['git', 'clone', repo_url, repo_path], 
                                  check=True, capture_output=True, text=True)
                print(f"Clone successful: {result}")
                log_step("Repository cloned successfully", {"stdout": result.stdout[:500]})
            except subprocess.CalledProcessError as e:
                print(f"Clone failed: {e}")
                log_error(f"Failed to clone repository", e)
                raise Exception(f"Failed to clone repository: {e.stderr}")
                
        elif repo_file:
            # Legacy file upload support
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
        
        # Save other uploaded files or string data
        if previous_output:
            if hasattr(previous_output, 'save'):
                # It's a file upload
                previous_output.save(os.path.join(job_folder, 'previous_output.txt'))
            else:
                # It's a string
                with open(os.path.join(job_folder, 'previous_output.txt'), 'w') as f:
                    f.write(str(previous_output))
        if feedback_log:
            if hasattr(feedback_log, 'save'):
                # It's a file upload
                feedback_log.save(os.path.join(job_folder, 'feedback.log'))
            else:
                # It's a string
                with open(os.path.join(job_folder, 'feedback.log'), 'w') as f:
                    f.write(str(feedback_log))
        
        send_progress(job_id, 'analyzing', 0, 0)
        
        # Clean the vibe statement to ensure no old repo references
        if vibe and repo_url:
            # Extract the repository name from URL
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            owner = repo_url.split('/')[-2] if len(repo_url.split('/')) > 1 else ''
            
            # Check if vibe references a different repository
            if 'MintWebsite' in vibe and 'MintWebsite' not in repo_url:
                print(f"Warning: Vibe references MintWebsite but analyzing {repo_url}")
                # Replace MintWebsite references with the actual repo name
                vibe = vibe.replace('MintWebsite', repo_name)
                vibe = vibe.replace('bruceblake/MintWebsite', f'{owner}/{repo_name}')
                print(f"Cleaned vibe: {vibe[:200]}...")
        
        # Build repo2file command based on stage
        # Run as module to handle relative imports correctly
        # Use the virtual environment Python if available
        venv_python = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'venv', 'bin', 'python')
        if os.path.exists(venv_python):
            python_executable = venv_python
        else:
            python_executable = sys.executable
        cmd = [python_executable, '-m', 'repo2file.dump_ultra']
        
        # Add repository path as the first positional argument
        if repo_path:
            cmd.append(repo_path)
        else:
            print("WARNING: No repository path specified, using current directory")
            cmd.append('.')
        
        # Use unique output file name to avoid caching issues
        output_filename = f'output_{job_id}.txt'
        output_path = os.path.join(job_folder, output_filename)
        
        # Add output path as the second positional argument
        cmd.append(output_path)
        
        # Now add the options
        cmd.extend(['--profile', 'vibe_coder_gemini_claude'])
        cmd.extend(['--vibe', vibe])
        
        if stage == 'B' and planner_output:
            # Save planner output to file
            planner_file = os.path.join(job_folder, 'planner_output.txt')
            with open(planner_file, 'w') as f:
                f.write(planner_output)
            cmd.extend(['--planner', planner_file])
            # Let the token manager handle budget automatically based on model
            # Since stage B uses Claude, it will automatically use a smaller budget
            # Note: We can still override if needed with --budget
        
        elif stage == 'C':
            # Stage C is for iteration planning (Gemini re-planning based on feedback)
            cmd = [python_executable, '-m', 'repo2file.dump_ultra', 'iterate']
            cmd.extend(['--current-repo-path', repo_path if repo_path else '.'])
            
            # We need the previous repo2file output from Stage B
            if planner_output:
                # Look for the previous output file
                prev_output_file = os.path.join(job_folder, 'previous_output.txt')
                with open(prev_output_file, 'w') as f:
                    f.write(planner_output)
                cmd.extend(['--previous-repo2file-output', prev_output_file])
            else:
                # Try to find a previous output file
                # Check if there's an existing Stage B output in the same session
                session_id = jobs.get(job_id, {}).get('session_id')
                if session_id:
                    for other_job_id, job_data in jobs.items():
                        if job_data.get('session_id') == session_id and other_job_id != job_id:
                            other_job_folder = os.path.join(app.config['UPLOAD_FOLDER'], f'job_{other_job_id}')
                            stage_b_file = os.path.join(other_job_folder, f'output_{other_job_id}.txt')
                            if os.path.exists(stage_b_file):
                                cmd.extend(['--previous-repo2file-output', stage_b_file])
                                print(f"Found previous Stage B output: {stage_b_file}")
                                break
                    else:
                        # Fallback: create minimal previous output
                        prev_output_file = os.path.join(job_folder, 'previous_output.txt')
                        with open(prev_output_file, 'w') as f:
                            f.write("# Previous Output\nNo previous output available.\n")
                        cmd.extend(['--previous-repo2file-output', prev_output_file])
            
            if feedback_log:
                feedback_file = os.path.join(job_folder, 'feedback.log')
                with open(feedback_file, 'w') as f:
                    f.write(feedback_log)
                cmd.extend(['--user-feedback-file', feedback_file])
            cmd.extend(['--output', output_path])
            # Let token manager handle budgeting - Gemini supports up to 2M tokens
            
        elif stage == 'D':
            # Stage D is for iteration coding (Claude implementation of updated plan)
            cmd = [python_executable, '-m', 'repo2file.dump_ultra']
            if repo_path:
                cmd.append(repo_path)
            else:
                cmd.append('.')
            cmd.append(output_path)
            cmd.extend(['--profile', 'vibe_coder_gemini_claude'])
            cmd.extend(['--vibe', vibe])
            
            # Save the updated planner output
            if planner_output:
                planner_file = os.path.join(job_folder, 'updated_planner_output.txt')
                with open(planner_file, 'w') as f:
                    f.write(planner_output)
                cmd.extend(['--planner', planner_file])
            
            # Save feedback for context
            if feedback_log:
                feedback_file = os.path.join(job_folder, 'feedback.log')
                with open(feedback_file, 'w') as f:
                    f.write(feedback_log)
                cmd.extend(['--feedback', feedback_file])
            
            # Let token manager handle budgeting - will auto-detect Claude's limits
        
        
        # Run the analysis with proper error handling
        print(f"Running command: {' '.join(cmd)}")
        log_step("Executing repo2file command", {"command": ' '.join(cmd), "stage": stage})
        
        # Set the working directory to the project root so modules can be found
        working_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        try:
            # Use subprocess with separate pipes to avoid buffer issues
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=working_dir,
                bufsize=1
            )
            
            # Read output in real-time to avoid buffer overflow
            stdout_lines = []
            stderr_lines = []
            
            # Use communicate() to avoid deadlock
            stdout, stderr = process.communicate(timeout=600)
            
            if stdout:
                stdout_lines = stdout.splitlines()
            if stderr:
                stderr_lines = stderr.splitlines()
            
            process_return_code = process.returncode
            
        except subprocess.TimeoutExpired:
            log_error("Command timed out after 10 minutes", None)
            process.terminate()
            process.wait()
            raise Exception("Process timed out after 10 minutes")
        except Exception as e:
            log_error(f"Failed to run command: {str(e)}", e)
            if 'process' in locals():
                process.terminate()
                process.wait()
            raise Exception(f"Failed to run process: {str(e)}")
        
        # Create a result object similar to subprocess.run
        class Result:
            def __init__(self, returncode, stdout, stderr):
                self.returncode = returncode
                self.stdout = stdout
                self.stderr = stderr
        
        process = Result(
            returncode=process_return_code,
            stdout='\n'.join(stdout_lines) if stdout_lines else stdout,
            stderr='\n'.join(stderr_lines) if stderr_lines else stderr
        )
        
        print(f"Process return code: {process.returncode}")
        if process.stdout:
            print(f"Stdout length: {len(process.stdout)}")
            print(f"Stdout: {process.stdout}")  # Show full stdout for debugging
        if process.stderr:
            print(f"Stderr: {process.stderr}")  # Show full stderr for debugging
            
        if process.returncode != 0:
            # Log the full error for debugging
            error_msg = f"Repo2File failed with return code {process.returncode}"
            if process.stderr:
                error_msg += f"\nStderr: {process.stderr}"
                # Check for specific error patterns
                if "Broken pipe" in process.stderr:
                    error_msg = "Connection to subprocess was lost. This may be due to resource constraints."
                elif "No module named" in process.stderr:
                    error_msg = "Missing Python module. Ensure all dependencies are installed."
            if process.stdout:
                error_msg += f"\nStdout: {process.stdout}"
            print(error_msg)
            log_error(f"Command returned non-zero exit code: {process.returncode}", None)
            log_step("Command stderr", {"stderr": process.stderr[:500] if process.stderr else "None"})
            log_step("Command stdout", {"stdout": process.stdout[:500] if process.stdout else "None"})
            raise Exception(error_msg)
        
        send_progress(job_id, 'finalizing', 100, 100)
        
        # Read the output and parse sections
        # First check the specific output file we requested
        output_file = os.path.join(job_folder, output_filename)
        print(f"Looking for output file at: {output_file}")
        
        if not os.path.exists(output_file) and repo_path:
            # Fallback to the profile name in the repo dir
            output_file = os.path.join(repo_path, 'vibe_coder_gemini_claude')
            print(f"Trying fallback location: {output_file}")
        
        # List all files in the job folder for debugging
        print(f"Files in job folder {job_folder}:")
        for root, dirs, files in os.walk(job_folder):
            for file in files:
                filepath = os.path.join(root, file)
                print(f"  {filepath} ({os.path.getsize(filepath)} bytes)")
        
        if not os.path.exists(output_file):
            # Last fallback to generic output.txt
            output_file = os.path.join(job_folder, 'output.txt')
            if not os.path.exists(output_file):
                raise Exception(f"Output file not found at any expected location")
            
        print(f"Output file size: {os.path.getsize(output_file)} bytes")
        
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                full_content = f.read()
                print(f"Read {len(full_content)} characters from output file")
        except Exception as e:
            print(f"Error reading output file: {e}")
            raise Exception(f"Failed to read output file: {e}")
        
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
        
        # Send completed phase before ending
        print(f"Job {job_id} completed successfully, sending completed signal")
        send_progress(job_id, 'completed', 100, 100)
        log_iteration_end('completed')
        
    except Exception as e:
        print(f"Job {job_id} failed with error: {str(e)}")
        jobs[job_id]['status'] = 'error'
        jobs[job_id]['error'] = str(e)
        send_progress(job_id, 'error', 0, 0)
        log_error(f"Job {job_id} failed", e)
        log_iteration_end('failed')
    
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

@app.route('/loop-dashboard')
def loop_dashboard():
    return render_template('loop_dashboard.html')

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
    
    # Get repository information
    repo_type = request.form.get('repo_type', 'github')  # Default to github
    repo_path = request.form.get('repo_path', '')  # Local path
    repo_url = request.form.get('repo_url', '')    # GitHub URL
    repo_branch = request.form.get('repo_branch', '')  # GitHub branch
    
    # Session management for vibe coder workflow
    session_id = request.form.get('session_id', '')
    if not session_id and vibe and (stage == 'A' or (stage == 'B' and not previous_output)):
        # Create new session for vibe coder workflow
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            'id': session_id,
            'feature_vibe': vibe,
            'repo_type': repo_type,
            'repo_path': repo_path,
            'repo_url': repo_url,
            'created_at': time.time(),
            'phases': {},
            'iterations': [],
            'current_phase': 'started',
            'last_gemini_plan': None,
            'commit_history': []
        }
        
        # Get initial commit SHA if local repo
        if repo_type == 'local' and repo_path and os.path.exists(repo_path):
            try:
                import git
                repo = git.Repo(repo_path)
                sessions[session_id]['initial_sha'] = repo.head.commit.hexsha
                sessions[session_id]['current_sha'] = repo.head.commit.hexsha
            except Exception as e:
                print(f"Warning: Could not get git SHA: {e}")
    
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
        'result': None,
        'session_id': session_id if session_id else None
    }
    
    # Update session if exists
    if session_id and session_id in sessions:
        sessions[session_id]['current_phase'] = f'processing_{stage}'
        sessions[session_id]['latest_job_id'] = job_id
    
    # Start processing in background thread
    thread = threading.Thread(target=process_job, args=(job_id, job_folder, vibe, stage, repo_file, planner_output, previous_output, feedback_log, repo_type, repo_path, repo_url, repo_branch))
    thread.start()
    
    return jsonify({
        'job_id': job_id, 
        'session_id': session_id if session_id else None
    }), 200

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
    """Get the final result of a Celery job with MinIO output file references"""
    job_manager = JobManager()
    storage_manager = StorageManager()
    
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

@app.route('/api/v1/loop/status/<session_id>')
def loop_status(session_id):
    """Get the current status of a vibe coder loop session"""
    # Try to load from memory first, then from file
    session = sessions.get(session_id)
    if not session:
        session = load_session_data(session_id)
        if session:
            sessions[session_id] = session  # Cache in memory
    
    if not session:
        return jsonify({'error': 'Invalid session ID'}), 404
    
    # Prepare response data
    response = {
        'session_id': session_id,
        'feature_vibe': session['feature_vibe'],
        'current_phase': session['current_phase'],
        'repo_type': session['repo_type'],
        'repo_path': session.get('repo_path'),
        'repo_url': session.get('repo_url'),
        'iterations': len(session['iterations']),
        'latest_job_id': session.get('latest_job_id'),
        'initial_sha': session.get('initial_sha'),
        'current_sha': session.get('current_sha'),
        'commit_history': session.get('commit_history', [])
    }
    
    # Add latest iteration data if available
    if session['iterations'] and session['current_phase'] in ['diff_analysis_complete', 'section_c_ready']:
        latest_iteration = session['iterations'][-1]
        response['latest_iteration_data'] = {
            'iteration_number': latest_iteration.get('iteration_number'),
            'sha': latest_iteration.get('new_sha'),
            'diff_summary': latest_iteration.get('diff_summary'),
            'test_results': latest_iteration.get('test_results'),
            'is_section_c_ready': bool(latest_iteration.get('section_c_output_file'))
        }
    
    return jsonify(response), 200

@app.route('/api/v1/loop/analyze_changes/<session_id>', methods=['POST'])
def analyze_changes(session_id):
    """Analyze recent commits and changes for a vibe coder loop session"""
    if session_id not in sessions:
        return jsonify({'error': 'Invalid session ID'}), 404
    
    session = sessions[session_id]
    
    # Only analyze if we have a local repository
    if session['repo_type'] != 'local' or not session.get('repo_path'):
        return jsonify({'error': 'Only local repositories supported for analysis'}), 400
    
    repo_path = session['repo_path']
    if not os.path.exists(repo_path):
        return jsonify({'error': 'Repository path not found'}), 404
    
    try:
        # Update the current phase
        session['current_phase'] = 'analyzing_changes'
        
        # Get the diff summary
        from repo2file.git_analyzer import GitAnalyzer
        git_analyzer = GitAnalyzer(repo_path)
        
        # Get current HEAD SHA
        current_sha = git_analyzer.get_head_sha()
        old_sha = session.get('current_sha', session.get('initial_sha'))
        
        if not old_sha:
            return jsonify({'error': 'No previous commit SHA found'}), 400
        
        # Generate diff summary
        diff_summary = git_analyzer.get_diff_summary(old_sha, current_sha)
        
        # Run tests if configured
        test_results = {}
        profile_test_command = None
        
        # Try to get test command from profile
        try:
            if hasattr(app, 'profile') and hasattr(app.profile, 'test_command'):
                profile_test_command = app.profile.test_command
        except:
            pass
        
        if profile_test_command:
            from repo2file.test_runner import run_project_tests
            test_results = run_project_tests(repo_path, profile_test_command)
        
        # Store analysis results
        iteration_num = len(session['iterations']) + 1
        iteration_data = {
            'iteration_number': iteration_num,
            'old_sha': old_sha,
            'new_sha': current_sha,
            'diff_summary': diff_summary,
            'test_results': test_results,
            'timestamp': time.time(),
            'user_feedback_file': None,
            'section_c_output_file': None
        }
        
        session['iterations'].append(iteration_data)
        session['current_sha'] = current_sha
        session['current_phase'] = 'diff_analysis_complete'
        
        # Extract commit message if available
        try:
            commit_msg = git_analyzer.repo.commit(current_sha).message.strip() if git_analyzer.repo else None
        except:
            commit_msg = None
        
        # Update commit history for UI
        commit_info = {
            'sha': current_sha,
            'message': commit_msg or 'No commit message',
            'tests_passed': test_results.get('passed', False),
            'test_summary': test_results.get('summary', '')
        }
        session['commit_history'].append(commit_info)
        
        # Save full session data to file
        save_session_data(session_id, session)
        
        # Save iteration analysis to separate file
        session_dir = os.path.join(app.config['UPLOAD_FOLDER'], f'session_{session_id}')
        os.makedirs(session_dir, exist_ok=True)
        
        iteration_file = os.path.join(session_dir, f'iteration_{iteration_num}_analysis.json')
        with open(iteration_file, 'w') as f:
            json.dump(iteration_data, f, indent=2)
        
        return jsonify({
            'success': True,
            'iteration': iteration_num,
            'diff_summary': diff_summary,
            'test_results': test_results,
            'new_sha': current_sha
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/loop/generate_section_c/<session_id>', methods=['POST'])
def generate_section_c(session_id):
    """Generate Section C (Iteration Brief) for a vibe coder loop session"""
    if session_id not in sessions:
        return jsonify({'error': 'Invalid session ID'}), 404
    
    session = sessions[session_id]
    
    # Ensure we have at least one iteration
    if not session.get('iterations'):
        return jsonify({'error': 'No iterations available. Run /analyze_changes first.'}), 400
    
    try:
        data = request.get_json() or {}
        planner_output = data.get('planner_output')
        user_feedback = data.get('user_feedback')
        
        # Create an instance of RepoToFileGenerator
        from repo2file.dump_ultra import RepoToFileGenerator
        repo2file_gen = RepoToFileGenerator()
        
        # Generate the iteration brief (Section C)
        section_c_content = repo2file_gen.generate_iteration_brief(session, planner_output, user_feedback)
        
        # Save Section C to file  
        iteration_num = len(session['iterations'])
        session_dir = os.path.join(app.config['UPLOAD_FOLDER'], f'session_{session_id}')
        os.makedirs(session_dir, exist_ok=True)
        
        section_c_file = os.path.join(session_dir, f'iteration_{iteration_num}_section_c.txt')
        with open(section_c_file, 'w') as f:
            f.write(section_c_content)
        
        # Update the latest iteration with the file path
        if session['iterations']:
            session['iterations'][-1]['section_c_output_file'] = section_c_file
        
        # Update session phase
        session['current_phase'] = 'section_c_generated'
        
        # Save full session data
        save_session_data(session_id, session)
        
        return jsonify({
            'success': True,
            'section_c_content': section_c_content,
            'file_path': section_c_file,
            'iteration': iteration_num
        }), 200
        
    except Exception as e:
        app.logger.error(f"Error generating Section C: {str(e)}")
        session['current_phase'] = 'error_generating_section_c'
        return jsonify({'error': str(e)}), 500

@app.route('/api/v1/loop/status/<session_id>', methods=['GET'])
def get_loop_status(session_id):
    """Get the current status of a vibe coder loop session"""
    if session_id not in sessions:
        return jsonify({'error': 'Invalid session ID'}), 404
    
    session = sessions[session_id]
    
    # Load full session data from file if available
    session_data = load_session_data(session_id)
    if session_data:
        session = session_data
    
    # Prepare response data
    response_data = {
        'session_id': session_id,
        'feature_vibe': session.get('feature_vibe', ''),
        'repo_path': session.get('repo_path', ''),
        'repo_type': session.get('repo_type', ''),
        'current_phase': session.get('current_phase', 'uninitialized'),
        'initial_sha': session.get('initial_sha', ''),
        'current_sha': session.get('current_sha', ''),
        'iterations': session.get('iterations', []),
        'commit_history': session.get('commit_history', []),
        'last_section_a': None,
        'last_section_b': None
    }
    
    # Try to load section files
    session_dir = os.path.join(app.config['UPLOAD_FOLDER'], f'session_{session_id}')
    
    # Load Section A content
    section_a_file = os.path.join(session_dir, 'section_a.txt')
    if os.path.exists(section_a_file):
        with open(section_a_file, 'r') as f:
            response_data['last_section_a'] = f.read()
    
    # Load Section B content  
    section_b_file = os.path.join(session_dir, 'section_b.txt')
    if os.path.exists(section_b_file):
        with open(section_b_file, 'r') as f:
            response_data['last_section_b'] = f.read()
    
    # Add Section C content from the last iteration
    if response_data['iterations']:
        last_iteration = response_data['iterations'][-1]
        section_c_file = last_iteration.get('section_c_output_file')
        if section_c_file and os.path.exists(section_c_file):
            with open(section_c_file, 'r') as f:
                last_iteration['section_c_content'] = f.read()
    
    return jsonify(response_data), 200

@app.route('/process', methods=['POST'])
def process():
    """Process files or GitHub repository using Celery async tasks"""
    try:
        job_manager = JobManager()
        storage_manager = StorageManager()
        
        github_branch = None  # Initialize variable
        
        # Determine input type and prepare input reference
        if 'files[]' in request.files:
            # Handle file uploads
            files = request.files.getlist('files[]')
            if not files or files[0].filename == '':
                return jsonify({"error": "No files selected"}), 400
            
            # Create temporary directory for uploads
            temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(uuid.uuid4()))
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

@app.route('/download/<job_id>')
def download(job_id):
    """Download processed output file from MinIO via job result"""
    storage_manager = StorageManager()
    job_manager = JobManager()
    
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

# Docker endpoints
@app.route('/api/parse-compose', methods=['POST'])
def parse_compose():
    """Parse docker-compose file to extract services"""
    try:
        compose_file = request.files.get('compose_file')
        if not compose_file:
            return jsonify({'error': 'No compose file provided'}), 400
        
        # Save temporarily and parse
        temp_path = os.path.join(tempfile.gettempdir(), 'temp_compose.yml')
        compose_file.save(temp_path)
        
        from repo2file.compose_parser import ComposeParser
        parser = ComposeParser(Path(temp_path))
        config = parser.parse()
        
        services = list(config.services.keys())
        
        # Clean up
        os.unlink(temp_path)
        
        return jsonify({'services': services})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/docker/logs/<service>')
def docker_logs(service):
    """Get logs from a Docker service"""
    try:
        # Run docker logs command
        cmd = ['docker', 'logs', '--tail', '100', service]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        logs = result.stdout
        if result.stderr:
            logs += '\n--- STDERR ---\n' + result.stderr
        
        return jsonify({'logs': logs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/docker/exec', methods=['POST'])
def docker_exec():
    """Execute command in a Docker container"""
    try:
        data = request.get_json()
        service = data.get('service')
        command = data.get('command')
        
        if not service or not command:
            return jsonify({'error': 'Service and command required'}), 400
        
        # Run docker exec command
        cmd = ['docker', 'exec', service] + command.split()
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        return jsonify({
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Commit watching endpoints
@app.route('/api/watch-commits/start', methods=['POST'])
def start_commit_watch():
    """Start watching commits on the current repository"""
    try:
        data = request.get_json()
        repo_path = data.get('repo_path', '.')
        last_commit = data.get('last_commit')
        
        # Import here to avoid issues if gitpython not installed
        from repo2file.git_diff_summarizer import CommitWatcher
        
        # Initialize commit watcher
        watcher = CommitWatcher(Path(repo_path))
        new_commits = watcher.get_commits_since(last_commit)
        
        return jsonify({
            'success': True,
            'commits': [
                {
                    'hash': str(commit),
                    'message': commit.message.strip(),
                    'author': str(commit.author),
                    'timestamp': commit.committed_date
                }
                for commit in new_commits
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-diff', methods=['POST'])
def analyze_diff():
    """Analyze git diff for a commit"""
    try:
        data = request.get_json()
        repo_path = data.get('repo_path', '.')
        commit_hash = data.get('commit_hash')
        
        # Import here to avoid issues if gitpython not installed
        from repo2file.git_diff_summarizer import GitDiffSummarizer
        
        # Initialize summarizer
        summarizer = GitDiffSummarizer(Path(repo_path))
        summary = summarizer.summarize_commit(commit_hash)
        
        return jsonify({
            'success': True,
            'summary': {
                'files_changed': summary.files_changed,
                'additions': summary.additions,
                'deletions': summary.deletions,
                'functions_modified': summary.functions_modified,
                'test_paths': summary.test_paths,
                'non_test_paths': summary.non_test_paths,
                'summary_text': summary.summary_text,
                'high_level_summary': summary.high_level_summary
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-iteration-brief', methods=['POST'])
def generate_iteration_brief():
    """Generate iteration brief (Section C) from diff and test results"""
    try:
        data = request.get_json()
        planner_output = data.get('planner_output', '')
        diff_summary = data.get('diff_summary', {})
        test_results = data.get('test_results', {})
        feature_vibe = data.get('feature_vibe', '')
        
        # Construct the iteration brief
        brief = f"## Feature Implementation Progress\n\n"
        brief += f"**Feature Vibe**: {feature_vibe}\n\n"
        
        # Add planner context
        if planner_output:
            brief += "### Previous Planning Context\n"
            brief += f"{planner_output[:500]}...\n\n"
        
        # Add diff summary
        brief += "### Changes Made\n"
        if diff_summary:
            brief += f"- Files changed: {', '.join(diff_summary.get('files_changed', []))}\n"
            brief += f"- Lines added: {diff_summary.get('additions', 0)}\n"
            brief += f"- Lines deleted: {diff_summary.get('deletions', 0)}\n"
            if diff_summary.get('functions_modified'):
                brief += f"- Functions modified: {', '.join(diff_summary['functions_modified'])}\n"
            brief += f"\n{diff_summary.get('high_level_summary', '')}\n\n"
        
        # Add test results
        brief += "### Test Results\n"
        if test_results:
            if test_results.get('passed'):
                brief += f"✅ Passed: {test_results['passed']}\n"
            if test_results.get('failed'):
                brief += f"❌ Failed: {test_results['failed']}\n"
            if test_results.get('errors'):
                brief += f"⚠️ Errors: {test_results['errors']}\n"
            if test_results.get('failure_details'):
                brief += "\nFailure Details:\n"
                for failure in test_results['failure_details']:
                    brief += f"- {failure}\n"
        else:
            brief += "No test results available.\n"
        
        # Add next steps
        brief += "\n### Next Steps\n"
        brief += "Please review the above changes and test results, then:\n"
        brief += "1. Fix any failing tests or errors\n"
        brief += "2. Complete any unfinished implementation\n"
        brief += "3. Add any missing functionality\n"
        brief += "4. Ensure all edge cases are handled\n"
        
        return jsonify({
            'success': True,
            'iteration_brief': brief
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/run-tests', methods=['POST'])
def run_tests():
    """Run tests and parse results"""
    # Start test execution logging
    test_id = str(uuid.uuid4())
    log_iteration_start(test_id, "Test Execution")
    
    try:
        data = request.get_json()
        repo_path = data.get('repo_path', '.')
        session_id = data.get('session_id')
        test_framework = data.get('framework', 'auto')  # auto-detect by default
        use_docker = data.get('use_docker', None)  # None = auto-detect
        
        print(f"Test runner - Initial repo_path: {repo_path}, session_id: {session_id}")
        log_step("Test runner initialized", {
            "repo_path": repo_path,
            "session_id": session_id,
            "framework": test_framework,
            "use_docker": use_docker
        })
        
        # Handle GitHub URL similar to get-commits
        if repo_path and repo_path.startswith('https://github.com'):
            if session_id:
                # Try multiple folder patterns
                folders_to_check = [
                    os.path.join(app.config['UPLOAD_FOLDER'], f'session_{session_id}'),
                    os.path.join(app.config['UPLOAD_FOLDER'], f'job_{session_id}')
                ]
                
                # Also check all job folders for matching session_id
                for job_id, job_data in jobs.items():
                    if job_data.get('session_id') == session_id:
                        folders_to_check.append(os.path.join(app.config['UPLOAD_FOLDER'], f'job_{job_id}'))
                
                # Check each folder for repo
                for folder in folders_to_check:
                    potential_repo = os.path.join(folder, 'repo')
                    if os.path.exists(potential_repo):
                        repo_path = potential_repo
                        print(f"Test runner - Found repo at: {repo_path}")
                        break
                else:
                    # Last resort: check all job folders for any repo
                    all_folders = os.listdir(app.config['UPLOAD_FOLDER'])
                    for folder_name in all_folders:
                        if folder_name.startswith('job_'):
                            folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
                            potential_repo = os.path.join(folder_path, 'repo')
                            if os.path.exists(potential_repo):
                                # Verify it's a git repo and matches our URL
                                try:
                                    check_cmd = ['git', '-C', potential_repo, 'config', '--get', 'remote.origin.url']
                                    result = subprocess.run(check_cmd, capture_output=True, text=True)
                                    if result.returncode == 0 and repo_path in result.stdout:
                                        repo_path = potential_repo
                                        print(f"Test runner - Found matching repo at: {repo_path}")
                                        break
                                except:
                                    pass
                
                if not os.path.exists(repo_path):
                    return jsonify({'error': 'Repository not found for session'}), 404
            else:
                return jsonify({'error': 'Session ID required for GitHub repos'}), 400
        
        print(f"Test runner - Final repo_path: {repo_path}")
        
        # Check Docker availability
        docker_available = False
        has_dockerfile = False
        has_compose = False
        
        try:
            # Check if Docker is available
            docker_check = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            docker_available = docker_check.returncode == 0
            
            if docker_available:
                print(f"Docker is available: {docker_check.stdout.strip()}")
                
                # Check for existing Docker files in the repo and subdirectories
                import glob
                
                # Search for Dockerfile in repo and subdirectories
                dockerfile_patterns = [
                    os.path.join(repo_path, 'Dockerfile'),
                    os.path.join(repo_path, '**/Dockerfile'),
                    os.path.join(repo_path, 'Dockerfile.*'),
                    os.path.join(repo_path, '**/Dockerfile.*')
                ]
                
                dockerfile_path = None
                for pattern in dockerfile_patterns:
                    matches = glob.glob(pattern, recursive=True)
                    if matches:
                        has_dockerfile = True
                        dockerfile_path = matches[0]  # Use the first match
                        print(f"Found Dockerfile(s): {matches}")
                        break
                
                # Search for docker-compose files
                compose_patterns = [
                    os.path.join(repo_path, 'docker-compose.yml'),
                    os.path.join(repo_path, 'docker-compose.yaml'),
                    os.path.join(repo_path, '**/docker-compose.yml'),
                    os.path.join(repo_path, '**/docker-compose.yaml'),
                    os.path.join(repo_path, 'docker-compose.*.yml'),
                    os.path.join(repo_path, 'docker-compose.*.yaml')
                ]
                
                compose_file = None
                for pattern in compose_patterns:
                    matches = glob.glob(pattern, recursive=True)
                    if matches:
                        has_compose = True
                        compose_file = matches[0]  # Use the first match
                        print(f"Found docker-compose file(s): {matches}")
                        break
                
                print(f"Dockerfile exists: {has_dockerfile}, docker-compose exists: {has_compose}")
        except Exception as e:
            print(f"Docker check error: {e}")
        
        # Use Docker if requested or if available and repo has Docker setup
        if use_docker or (docker_available and (has_dockerfile or has_compose)):
            if not docker_available:
                return jsonify({'error': 'Docker requested but not available'}), 400
                
            print(f"Using Docker for tests")
            
            # Build and run tests in Docker
            try:
                if has_compose:
                    # Use docker-compose with the found file
                    if not compose_file:
                        # Fallback if compose_file wasn't set (shouldn't happen)
                        compose_file = 'docker-compose.yml' if os.path.exists(os.path.join(repo_path, 'docker-compose.yml')) else 'docker-compose.yaml'
                    
                    # Get relative path for docker-compose command
                    compose_file_rel = os.path.relpath(compose_file, repo_path)
                    
                    # Check if there's a test service
                    compose_check = subprocess.run(
                        ['docker-compose', '-f', compose_file_rel, 'config'],
                        cwd=repo_path,
                        capture_output=True,
                        text=True
                    )
                    
                    # Run tests with docker-compose
                    cmd = ['docker-compose', '-f', compose_file_rel, 'run', '--rm', 'test']
                    if 'test' not in compose_check.stdout:
                        # Try default service name or app
                        # Check if package.json exists before trying npm test
                        package_json_path = os.path.join(repo_path, 'package.json')
                        if os.path.exists(package_json_path):
                            cmd = ['docker-compose', '-f', compose_file_rel, 'run', '--rm', 'app', 'npm', 'test']
                        else:
                            # Try Python tests
                            cmd = ['docker-compose', '-f', compose_file_rel, 'run', '--rm', 'app', 'pytest']
                    
                    result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True, timeout=600)
                    
                elif has_dockerfile:
                    # Build Docker image using the found Dockerfile
                    image_name = f"test-{uuid.uuid4().hex[:8]}"
                    dockerfile_dir = os.path.dirname(dockerfile_path)
                    dockerfile_name = os.path.basename(dockerfile_path)
                    
                    # Change to the directory containing the Dockerfile
                    build_cmd = ['docker', 'build', '-t', image_name, '-f', dockerfile_name, '.']
                    build_result = subprocess.run(build_cmd, cwd=dockerfile_dir, capture_output=True, text=True)
                    
                    if build_result.returncode != 0:
                        return jsonify({'error': f'Docker build failed: {build_result.stderr}'}), 500
                    
                    # Run tests in container
                    # Try to detect test command from Dockerfile
                    test_cmd = None
                    with open(dockerfile_path, 'r') as f:
                        dockerfile_content = f.read()
                        if 'RUN npm test' in dockerfile_content or 'CMD ["npm", "test"]' in dockerfile_content:
                            test_cmd = ['npm', 'test']
                        elif 'RUN pytest' in dockerfile_content or 'CMD ["pytest"]' in dockerfile_content:
                            test_cmd = ['pytest']
                        elif 'RUN go test' in dockerfile_content:
                            test_cmd = ['go', 'test', './...']
                    
                    if not test_cmd:
                        # Default based on detected files
                        if os.path.exists(os.path.join(repo_path, 'package.json')):
                            test_cmd = ['npm', 'test']
                        elif os.path.exists(os.path.join(repo_path, 'requirements.txt')):
                            test_cmd = ['pytest']
                        elif os.path.exists(os.path.join(repo_path, 'go.mod')):
                            test_cmd = ['go', 'test', './...']
                        else:
                            test_cmd = ['echo', 'No test command found']
                    
                    run_cmd = ['docker', 'run', '--rm', image_name] + test_cmd
                    result = subprocess.run(run_cmd, cwd=repo_path, capture_output=True, text=True, timeout=600)
                    
                    # Cleanup image
                    subprocess.run(['docker', 'rmi', image_name], capture_output=True)
                    
                else:
                    # No Docker files, create a temporary one based on detected language
                    return jsonify({'error': 'No Dockerfile or docker-compose.yml found'}), 400
                
                # Parse results
                output = result.stdout + result.stderr
                passed = result.returncode == 0
                
                # Try to extract test counts
                passed_count = 0
                failed_count = 0
                
                # Common patterns
                import re
                if 'passed' in output.lower():
                    match = re.search(r'(\d+)\s*passed', output, re.IGNORECASE)
                    if match:
                        passed_count = int(match.group(1))
                
                if 'failed' in output.lower():
                    match = re.search(r'(\d+)\s*failed', output, re.IGNORECASE)
                    if match:
                        failed_count = int(match.group(1))
                
                return jsonify({
                    'success': True,
                    'docker': True,
                    'results': {
                        'framework': 'docker',
                        'passed': passed_count if passed_count else (1 if passed else 0),
                        'failed': failed_count if failed_count else (0 if passed else 1),
                        'errors': 0,
                        'skipped': 0,
                        'output': output[:5000],
                        'success': passed
                    }
                })
                
            except subprocess.TimeoutExpired:
                return jsonify({'error': 'Docker test execution timed out'}), 500
            except Exception as e:
                print(f"Docker test error: {e}")
                import traceback
                traceback.print_exc()
                return jsonify({'error': f'Docker test failed: {str(e)}'}), 500
        
        # Original test running logic for non-Docker mode
        results = {}
        
        # Run tests based on framework or auto-detect
        if test_framework == 'auto':
            # Try common test commands
            test_commands = [
                ('pytest', ['pytest', '--tb=short']),
                ('npm', ['npm', 'test']),
                ('yarn', ['yarn', 'test']),
                ('make', ['make', 'test']),
                ('go', ['go', 'test', './...']),
                ('cargo', ['cargo', 'test']),
                ('dotnet', ['dotnet', 'test'])
            ]
            
            for framework, cmd in test_commands:
                try:
                    print(f"Test runner - Trying {framework} with command: {cmd}")
                    result = subprocess.run(cmd, 
                                          capture_output=True, 
                                          text=True,
                                          cwd=repo_path,
                                          timeout=300)  # 5 minute timeout
                    print(f"Test runner - {framework} return code: {result.returncode}")
                    
                    if result.returncode != -1:  # Command exists
                        # Simple test result parsing based on return code and output
                        output = result.stdout + result.stderr
                        test_passed = result.returncode == 0
                        
                        # Try to extract test counts from output
                        passed_count = 0
                        failed_count = 0
                        
                        # Common test output patterns
                        if 'pytest' in cmd[0] or framework == 'pytest':
                            # Look for pytest summary
                            import re
                            summary_match = re.search(r'(\d+) passed', output)
                            if summary_match:
                                passed_count = int(summary_match.group(1))
                            fail_match = re.search(r'(\d+) failed', output)
                            if fail_match:
                                failed_count = int(fail_match.group(1))
                        
                        elif 'npm' in cmd[0] or 'yarn' in cmd[0]:
                            # Look for jest/mocha output  
                            import re
                            if 'Test Suites:' in output:  # Jest
                                pass_match = re.search(r'(\d+) passed', output)
                                if pass_match:
                                    passed_count = int(pass_match.group(1))
                                fail_match = re.search(r'(\d+) failed', output)
                                if fail_match:
                                    failed_count = int(fail_match.group(1))
                        
                        # Only report success if we found actual test output
                        if passed_count > 0 or failed_count > 0:
                            results = {
                                'framework': framework,
                                'passed': passed_count,
                                'failed': failed_count,
                                'errors': failed_count,  # Simplified
                                'skipped': 0,
                                'output': output[:5000],  # Limit output size
                                'success': test_passed
                            }
                            break
                        elif test_passed:
                            # Test command succeeded but no specific counts found
                            results = {
                                'framework': framework,
                                'passed': 1,
                                'failed': 0,
                                'errors': 0,
                                'skipped': 0,
                                'output': output[:5000],
                                'success': True
                            }
                            break
                except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                    print(f"Test runner - {framework} error: {e}")
                    continue
        else:
            # Run specific framework
            framework_commands = {
                'pytest': ['pytest', '--tb=short'],
                'jest': ['npm', 'test'],
                'mocha': ['npm', 'test'],
                'go': ['go', 'test', './...'],
                'cargo': ['cargo', 'test'],
                'dotnet': ['dotnet', 'test']
            }
            
            cmd = framework_commands.get(test_framework)
            if cmd:
                result = subprocess.run(cmd,
                                      capture_output=True,
                                      text=True,
                                      cwd=repo_path,
                                      timeout=300)
                
                # Simple test result parsing
                output = result.stdout + result.stderr
                test_passed = result.returncode == 0
                
                results = {
                    'framework': test_framework,
                    'passed': 1 if test_passed else 0,
                    'failed': 0 if test_passed else 1,
                    'errors': 0,
                    'skipped': 0,
                    'output': output[:5000],
                    'success': test_passed
                }
        
        if not results:
            return jsonify({'error': 'No test framework detected or tests found'}), 404
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        print(f"Test runner error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-docker', methods=['GET'])
def check_docker():
    """Check if Docker is available for test running"""
    try:
        # Simple Docker check
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        docker_available = result.returncode == 0
        return jsonify({
            'can_use_docker': docker_available,
            'docker_version': result.stdout.strip() if docker_available else None
        })
    except Exception as e:
        return jsonify({'can_use_docker': False, 'error': str(e)})
    
    docker_available = check_docker_available()
    dockerfile_exists = os.path.exists(os.path.join(os.path.dirname(__file__), '..', 'Dockerfile'))
    
    return jsonify({
        'docker_available': docker_available,
        'dockerfile_exists': dockerfile_exists,
        'can_use_docker': docker_available and dockerfile_exists
    })

@app.route('/api/refine-prompt', methods=['POST'])
def refine_prompt():
    """Refine user prompt using LLM"""
    try:
        data = request.get_json()
        prompt_text = data.get('prompt_text', '')
        repo_info = data.get('repo_info', {})
        target = data.get('target', 'planning')
        
        # Get repository context
        context_summary = ''
        try:
            if repo_info.get('type') == 'local':
                repo_path = repo_info.get('path')
                if repo_path and os.path.exists(repo_path):
                    # Analyze repository to get context
                    from repo2file.code_analyzer import CodeAnalyzer
                    analyzer = CodeAnalyzer()
                    
                    # Get basic project info
                    project_info = analyzer._detect_project_type(Path(repo_path))
                    language = analyzer._detect_primary_language(Path(repo_path))
                    
                    context_summary = f"Project type: {project_info}, Primary language: {language}"
                else:
                    context_summary = "Repository path not found"
            elif repo_info.get('type') == 'github':
                # Get repository name from URL
                url = repo_info.get('url', '')
                repo_parts = url.split('/')
                if len(repo_parts) >= 2:
                    repo_name = repo_parts[-1].replace('.git', '')
                    owner = repo_parts[-2]
                    context_summary = f"GitHub repository: {owner}/{repo_name} ({url})"
                else:
                    context_summary = f"GitHub repository: {url}"
            else:
                context_summary = "Unknown repository type"
        except Exception as e:
            print(f"Error getting repo context: {e}")
            context_summary = "Unable to analyze repository"
        
        # Import LLMAugmenter
        from repo2file.llm_augmenter import LLMAugmenter
        
        # Initialize augmenter with explicit provider
        augmenter = LLMAugmenter(provider="gemini")
        
        if not augmenter.is_available():
            return jsonify({'error': 'LLM service not available. Please set GEMINI_API_KEY environment variable.'}), 503
        
        # Refine the prompt
        refined = augmenter.refine_user_prompt(prompt_text, context_summary, target)
        
        # Check if prompt is large and needs chunking
        if len(refined) > 1500:  # Character threshold
            chunks = augmenter.chunk_large_prompt(refined)
            return jsonify({
                'refined_prompt': refined,
                'chunks': chunks,
                'is_chunked': True
            })
        
        return jsonify({
            'refined_prompt': refined,
            'is_chunked': False
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/audit-code', methods=['POST'])
def audit_code():
    """Perform security and quality audit on code changes"""
    try:
        data = request.get_json()
        diff_text = data.get('diff_text', '')
        changed_files = data.get('changed_files', {})
        checklist = data.get('checklist', '')
        
        # Import LLMAugmenter
        from repo2file.llm_augmenter import LLMAugmenter
        
        # Initialize augmenter
        augmenter = LLMAugmenter()
        
        if not augmenter.is_available():
            return jsonify({'error': 'LLM service not available'}), 503
        
        # Perform audit
        result = augmenter.perform_code_audit(diff_text, changed_files, checklist)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/archive-feature', methods=['POST']) 
def archive_feature():
    """Archive completed feature for future reference"""
    try:
        data = request.get_json()
        feature_vibe = data.get('feature_vibe')
        planner_outputs = data.get('planner_outputs', [])
        commits = data.get('commits', [])
        test_results = data.get('test_results', {})
        
        # Create archive directory
        archive_dir = os.path.join(app.config['JOBS_FOLDER'], 'archives')
        os.makedirs(archive_dir, exist_ok=True)
        
        # Generate archive ID
        archive_id = f"{time.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        feature_dir = os.path.join(archive_dir, archive_id)
        os.makedirs(feature_dir, exist_ok=True)
        
        # Save feature metadata
        metadata = {
            'id': archive_id,
            'feature_vibe': feature_vibe,
            'archived_at': time.time(),
            'commits_count': len(commits),
            'test_results': test_results
        }
        
        with open(os.path.join(feature_dir, 'metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Save planner outputs
        for i, output in enumerate(planner_outputs):
            with open(os.path.join(feature_dir, f'planner_{i}.txt'), 'w') as f:
                f.write(output)
        
        # Save commit history
        with open(os.path.join(feature_dir, 'commits.json'), 'w') as f:
            json.dump(commits, f, indent=2)
        
        return jsonify({
            'success': True,
            'archive_id': archive_id,
            'path': feature_dir
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/list-rules')
def list_rules():
    """List markdown files in the instructions directory"""
    try:
        # First check if request has repo_path
        repo_path = request.args.get('repo_path', '.')
        instructions_dir = os.path.join(repo_path, 'instructions')
        
        # Create directory if it doesn't exist
        if not os.path.exists(instructions_dir):
            os.makedirs(instructions_dir, exist_ok=True)
        
        rules = []
        if os.path.exists(instructions_dir):
            for filename in os.listdir(instructions_dir):
                if filename.endswith('.md'):
                    filepath = os.path.join(instructions_dir, filename)
                    stat = os.stat(filepath)
                    rules.append({
                        'id': filename.replace('.md', '').replace(' ', '-').lower(),
                        'filename': filename,
                        'name': filename.replace('.md', '').replace('_', ' ').title(),
                        'size': stat.st_size,
                        'modified': stat.st_mtime
                    })
        
        return jsonify({
            'success': True,
            'rules': sorted(rules, key=lambda x: x['name'])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-commits', methods=['POST'])
def get_commits():
    """Get commit history for a repository"""
    try:
        data = request.get_json()
        repo_path = data.get('repo_path')
        branch = data.get('branch', 'main')
        session_id = data.get('session_id')
        
        # Handle GitHub URL
        if repo_path and repo_path.startswith('https://github.com'):
            # Extract repo name from URL
            repo_name = repo_path.split('/')[-1].replace('.git', '')
            # Use the cached cloned repo - try multiple strategies
            if session_id:
                # Try multiple folder patterns
                folders_to_check = [
                    os.path.join(app.config['UPLOAD_FOLDER'], f'session_{session_id}'),
                    os.path.join(app.config['UPLOAD_FOLDER'], f'job_{session_id}')
                ]
                
                # Also check all job folders for matching session_id
                for job_id, job_data in jobs.items():
                    if job_data.get('session_id') == session_id:
                        folders_to_check.append(os.path.join(app.config['UPLOAD_FOLDER'], f'job_{job_id}'))
                
                # Check each folder for repo
                for folder in folders_to_check:
                    potential_repo = os.path.join(folder, 'repo')
                    if os.path.exists(potential_repo):
                        repo_path = potential_repo
                        print(f"Found repo at: {repo_path}")
                        break
                else:
                    # Last resort: check all job folders for any repo
                    all_folders = os.listdir(app.config['UPLOAD_FOLDER'])
                    for folder_name in all_folders:
                        if folder_name.startswith('job_'):
                            folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)
                            potential_repo = os.path.join(folder_path, 'repo')
                            if os.path.exists(potential_repo):
                                # Verify it's a git repo and matches our URL
                                try:
                                    check_cmd = ['git', '-C', potential_repo, 'config', '--get', 'remote.origin.url']
                                    result = subprocess.run(check_cmd, capture_output=True, text=True)
                                    if result.returncode == 0 and repo_path in result.stdout:
                                        repo_path = potential_repo
                                        print(f"Found matching repo at: {repo_path}")
                                        break
                                except:
                                    pass
                
                if not os.path.exists(repo_path):
                    return jsonify({'error': 'Repository not found for session'}), 404
            else:
                return jsonify({'error': 'Session ID required for GitHub repos'}), 400
        
        if not os.path.exists(repo_path):
            return jsonify({'error': 'Repository not found'}), 404
            
        # Get commits using git command directly
        try:
            # Get the list of recent commits
            cmd = ['git', '-C', repo_path, 'log', '--oneline', '-n', '10', '--format=%H|%an|%ae|%at|%s']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|', 4)
                    if len(parts) >= 5:
                        commit = {
                            'sha': parts[0],
                            'author': parts[1],
                            'email': parts[2],
                            'timestamp': int(parts[3]),
                            'message': parts[4]
                        }
                        commits.append(commit)
            
            return jsonify({'commits': commits, 'success': True})
        except subprocess.CalledProcessError as e:
            return jsonify({'error': f'Git command failed: {e.stderr}'}), 500
        
    except Exception as e:
        print(f"Error getting commits: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/get-diff', methods=['POST'])
def get_diff():
    """Get diff for a specific commit"""
    try:
        data = request.get_json()
        repo_path = data.get('repo_path')
        sha = data.get('sha')
        session_id = data.get('session_id')
        
        print(f"get-diff: repo_path={repo_path}, sha={sha}, session_id={session_id}")
        
        # Handle GitHub URL
        if repo_path and repo_path.startswith('https://github.com'):
            if session_id:
                # Try multiple folder patterns
                folders_to_check = [
                    os.path.join(app.config['UPLOAD_FOLDER'], f'session_{session_id}'),
                    os.path.join(app.config['UPLOAD_FOLDER'], f'session_{session_id}', 'repo'),
                    os.path.join(app.config['UPLOAD_FOLDER'], f'job_{session_id}'),
                    os.path.join(app.config['UPLOAD_FOLDER'], f'job_{session_id}', 'repo')
                ]
                
                # Also check all job folders for matching session_id
                for job_id, job_data in jobs.items():
                    if job_data.get('session_id') == session_id:
                        folders_to_check.append(os.path.join(app.config['UPLOAD_FOLDER'], f'job_{job_id}'))
                        folders_to_check.append(os.path.join(app.config['UPLOAD_FOLDER'], f'job_{job_id}', 'repo'))
                
                # Check each folder for repo
                for folder in folders_to_check:
                    if os.path.exists(folder) and os.path.exists(os.path.join(folder, '.git')):
                        repo_path = folder
                        print(f"Found repo at: {repo_path}")
                        break
                else:
                    print(f"Repository not found for session_id: {session_id}")
                    print(f"Checked folders: {folders_to_check}")
                    return jsonify({'error': 'Repository not found for session'}), 404
            else:
                return jsonify({'error': 'Session ID required for GitHub repos'}), 400
        
        if not os.path.exists(repo_path):
            print(f"Repository path does not exist: {repo_path}")
            return jsonify({'error': f'Repository not found at {repo_path}'}), 404
            
        # Import git analyzer
        from git_analyzer import GitAnalyzer
        analyzer = GitAnalyzer(repo_path)
        
        # Get diff data
        diff_data = analyzer.get_commit_diff(sha)
        
        return jsonify({
            'sha': sha,
            'additions': diff_data.get('stats', {}).get('additions', 0),
            'deletions': diff_data.get('stats', {}).get('deletions', 0),
            'files': list(diff_data.get('stats', {}).get('files', {}).keys()),
            'content': diff_data.get('diff_content', '')
        })
        
    except Exception as e:
        print(f"Error getting diff: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate_context', methods=['POST'])
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
        job_manager = JobManager()
        
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

@app.route('/api/refine_prompt_v2', methods=['POST'])
def refine_prompt_v2():
    """Refine a user's feature description using AI"""
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        repo_url = data.get('repo_url')
        
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400
            
        # Import the LLM augmenter
        from repo2file.llm_augmenter import LLMAugmenter
        
        # Check if API key is available in environment
        has_gemini_key = bool(os.getenv('GEMINI_API_KEY'))
        has_google_key = bool(os.getenv('GOOGLE_API_KEY'))
        
        print(f"Checking API keys - GEMINI_API_KEY: {has_gemini_key}, GOOGLE_API_KEY: {has_google_key}")
        
        if not has_gemini_key and not has_google_key:
            print("No API keys found, using fallback")
            # Provide a helpful enhancement without AI
            repo_name = repo_url.split('/')[-1].replace('.git', '') if repo_url else 'current repository'
            return jsonify({
                'success': True,
                'refined_prompt': f"Enhanced Feature Description:\n\n{prompt}\n\nImplementation Details:\n- Repository: {repo_name}\n- Focus on clean, maintainable code\n- Include comprehensive tests\n- Consider edge cases and error handling\n- Document any API changes"
            })
        
        try:
            # Create augmenter instance (it will use env vars)
            augmenter = LLMAugmenter(
                provider="gemini",
                api_key_env_var="GOOGLE_API_KEY" if has_google_key else "GEMINI_API_KEY"
            )
            
            # Check if the augmenter is available
            if not augmenter.is_available():
                print("LLM augmenter not available")
                raise Exception("LLM provider not available")
            
            # Create a simple repo context if URL provided
            repo_context = ""
            if repo_url:
                repo_name = repo_url.split('/')[-1].replace('.git', '')
                repo_context = f"Repository: {repo_name}"
            
            # Refine the prompt
            print(f"Attempting to refine prompt: {prompt[:100]}...")
            refined = augmenter.refine_user_prompt(prompt, repo_context)
            print(f"Successfully refined prompt")
            
            return jsonify({
                'success': True,
                'refined_prompt': refined
            })
            
        except Exception as llm_error:
            print(f"LLM error: {llm_error}")
            # Try the existing refine endpoint as fallback
            try:
                print("Trying original refine endpoint")
                response = refine_prompt()
                return response
            except Exception:
                # Final fallback
                raise llm_error
        
    except Exception as e:
        print(f"Error refining prompt: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback to simple enhancement if AI fails
        repo_name = repo_url.split('/')[-1].replace('.git', '') if repo_url else 'current repository'
        refined = f"Enhanced Feature Description:\n\n{prompt}\n\nImplementation notes:\n- Target repository: {repo_name}\n- Implement with clean, testable code\n- Include proper error handling\n- Add comprehensive documentation"
        
        return jsonify({
            'success': True,
            'refined_prompt': refined
        })

@app.route('/api/job_status_old/<job_id>')
def job_status_old(job_id):
    """Stream job status updates using Server-Sent Events for Celery tasks"""
    def generate():
        job_manager = JobManager()
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

@app.route('/api/check-session-repo', methods=['POST'])
def check_session_repo():
    """Debug endpoint to check if a session has a cloned repo"""
    data = request.get_json()
    session_id = data.get('session_id')
    
    result = {
        'session_id': session_id,
        'jobs_with_session': [],
        'repos_found': []
    }
    
    # Check which jobs have this session ID
    for job_id, job_data in jobs.items():
        if job_data.get('session_id') == session_id:
            result['jobs_with_session'].append(job_id)
            
            # Check if repo exists
            job_folder = os.path.join(app.config['UPLOAD_FOLDER'], f'job_{job_id}')
            repo_path = os.path.join(job_folder, 'repo')
            if os.path.exists(repo_path):
                result['repos_found'].append(repo_path)
    
    return jsonify(result)

@app.route('/api/detect-docker', methods=['POST'])
def detect_docker():
    """Detect if a repository has Docker setup"""
    try:
        data = request.get_json()
        repo_path = data.get('repo_path')
        session_id = data.get('session_id')
        
        # Handle repo path resolution similar to other endpoints
        if repo_path and repo_path.startswith('https://github.com'):
            if not session_id:
                return jsonify({'error': 'Session ID required for GitHub repos'}), 400
            
            # Find the cloned repo
            folders_to_check = [
                os.path.join(app.config['UPLOAD_FOLDER'], f'session_{session_id}'),
                os.path.join(app.config['UPLOAD_FOLDER'], f'job_{session_id}')
            ]
            
            for job_id, job_data in jobs.items():
                if job_data.get('session_id') == session_id:
                    folders_to_check.append(os.path.join(app.config['UPLOAD_FOLDER'], f'job_{job_id}'))
            
            for folder in folders_to_check:
                potential_repo = os.path.join(folder, 'repo')
                if os.path.exists(potential_repo):
                    repo_path = potential_repo
                    break
            else:
                return jsonify({'error': 'Repository not found'}), 404
        
        # Check for Docker files
        dockerfile_exists = os.path.exists(os.path.join(repo_path, 'Dockerfile'))
        compose_exists = os.path.exists(os.path.join(repo_path, 'docker-compose.yml')) or \
                        os.path.exists(os.path.join(repo_path, 'docker-compose.yaml'))
        
        # Check if Docker is available on the system
        docker_available = False
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True)
            docker_available = result.returncode == 0
        except:
            pass
        
        return jsonify({
            'docker_available': docker_available,
            'has_dockerfile': dockerfile_exists,
            'has_compose': compose_exists,
            'can_use_docker': docker_available and (dockerfile_exists or compose_exists)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-llm-status')
def check_llm_status():
    """Check if LLM APIs are configured and available"""
    try:
        # Check environment variables
        has_gemini_key = bool(os.getenv('GEMINI_API_KEY'))
        has_google_key = bool(os.getenv('GOOGLE_API_KEY'))
        has_openai_key = bool(os.getenv('OPENAI_API_KEY'))
        
        # Try to create an augmenter and check availability
        from repo2file.llm_augmenter import LLMAugmenter
        
        provider_status = {}
        
        if has_gemini_key or has_google_key:
            try:
                augmenter = LLMAugmenter(
                    provider="gemini",
                    api_key_env_var="GOOGLE_API_KEY" if has_google_key else "GEMINI_API_KEY"
                )
                provider_status['gemini'] = {
                    'configured': True,
                    'available': augmenter.is_available(),
                    'key_env': "GOOGLE_API_KEY" if has_google_key else "GEMINI_API_KEY"
                }
            except Exception as e:
                provider_status['gemini'] = {
                    'configured': True,
                    'available': False,
                    'error': str(e)
                }
        else:
            provider_status['gemini'] = {
                'configured': False,
                'available': False
            }
        
        return jsonify({
            'success': True,
            'env_vars': {
                'GEMINI_API_KEY': has_gemini_key,
                'GOOGLE_API_KEY': has_google_key,
                'OPENAI_API_KEY': has_openai_key
            },
            'providers': provider_status
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/detect-docker-compose', methods=['POST'])
def detect_docker_compose():
    """Detect docker-compose file in GitHub repository"""
    try:
        data = request.get_json()
        repo_url = data.get('repo_url')
        repo_branch = data.get('repo_branch')
        
        if not repo_url:
            return jsonify({'error': 'Repository URL required'}), 400
        
        # Create a temporary directory to clone the repo
        with tempfile.TemporaryDirectory() as temp_dir:
            # Clone repository
            try:
                if repo_branch:
                    subprocess.run(['git', 'clone', '-b', repo_branch, '--depth', '1', repo_url, temp_dir],
                                 check=True, capture_output=True, text=True)
                else:
                    subprocess.run(['git', 'clone', '--depth', '1', repo_url, temp_dir],
                                 check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                return jsonify({'error': f'Failed to clone repository: {e.stderr}'}), 400
            
            # Check for docker-compose files
            compose_files = []
            for filename in ['docker-compose.yml', 'docker-compose.yaml']:
                filepath = os.path.join(temp_dir, filename)
                if os.path.exists(filepath):
                    compose_files.append(filename)
                    
                    # Parse the compose file for services
                    try:
                        import yaml
                        with open(filepath, 'r') as f:
                            compose_config = yaml.safe_load(f)
                            services = list(compose_config.get('services', {}).keys())
                            return jsonify({
                                'has_compose': True,
                                'compose_file': filename,
                                'services': services
                            })
                    except Exception as e:
                        return jsonify({
                            'has_compose': True,
                            'compose_file': filename,
                            'services': [],
                            'error': str(e)
                        })
            
            return jsonify({'has_compose': False})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/list-rule-templates')
def list_rule_templates():
    """List available rule templates"""
    try:
        templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'starter_rules')
        
        templates = []
        template_info = {
            'general_ai_coding_guardrails.md': 'General best practices for AI-assisted coding',
            'nextjs_supabase_tailwind_best_practices.md': 'Best practices for Next.js + Supabase + Tailwind stack',
            'react_typescript_patterns.md': 'React with TypeScript patterns and conventions'
        }
        
        if os.path.exists(templates_dir):
            for filename in os.listdir(templates_dir):
                if filename.endswith('.md'):
                    templates.append({
                        'filename': filename,
                        'name': filename.replace('.md', '').replace('_', ' ').title(),
                        'description': template_info.get(filename, 'Custom rule template')
                    })
        
        return jsonify({
            'success': True,
            'templates': sorted(templates, key=lambda x: x['name'])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/import-rule-template', methods=['POST'])
def import_rule_template():
    """Import a rule template to the project"""
    try:
        data = request.get_json()
        template_filename = data.get('template_filename')
        repo_path = data.get('repo_path', '.')
        
        # Source and destination paths
        templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'starter_rules')
        source_path = os.path.join(templates_dir, template_filename)
        
        instructions_dir = os.path.join(repo_path, 'instructions')
        os.makedirs(instructions_dir, exist_ok=True)
        
        dest_path = os.path.join(instructions_dir, template_filename)
        
        # Check if template exists
        if not os.path.exists(source_path):
            return jsonify({'error': 'Template not found'}), 404
        
        # Copy the template
        shutil.copy2(source_path, dest_path)
        
        return jsonify({
            'success': True,
            'imported_as': template_filename
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# New logging and monitoring endpoints
@app.route('/api/logs/stream')
def stream_logs():
    """Stream real-time logs using Server-Sent Events"""
    def generate():
        log_queue = queue.Queue()
        iteration_logger.add_queue(log_queue)
        
        try:
            while True:
                try:
                    if not log_queue.empty():
                        log_entry = log_queue.get()
                        yield f"data: {json.dumps(log_entry)}\n\n"
                    else:
                        # Send heartbeat to keep connection alive
                        yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
                    time.sleep(0.5)
                except Exception as e:
                    print(f"Error in log streaming: {e}")
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
        except GeneratorExit:
            iteration_logger.remove_queue(log_queue)
        finally:
            iteration_logger.remove_queue(log_queue)
    
    response = Response(generate(), mimetype='text/event-stream')
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['X-Accel-Buffering'] = 'no'
    response.headers['Connection'] = 'keep-alive'
    return response

@app.route('/api/iterations/history')
def get_iteration_history():
    """Get iteration history and metrics"""
    try:
        logs = iteration_logger.get_session_logs()
        return jsonify({
            'success': True,
            'iterations': logs['metrics'].get('iterations', []),
            'current_iteration': iteration_logger.current_iteration,
            'session_id': logs['session_id'],
            'metrics': logs['metrics']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/iterations/<iteration_id>/diff')
def get_iteration_diff(iteration_id):
    """Get code changes for a specific iteration"""
    try:
        # Get diff for the iteration
        repo_path = request.args.get('repo_path', '.')
        diff_visualizer.repo_path = Path(repo_path)
        
        # Get git diff for the iteration
        diff_data = diff_visualizer.get_git_diff()
        
        return jsonify({
            'success': True,
            'diff': diff_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test/detect')
def detect_tests():
    """Detect available test frameworks and test files"""
    try:
        repo_path = request.args.get('repo_path', '.')
        test_executor.repo_path = Path(repo_path)
        
        frameworks = test_executor.detect_test_framework()
        
        return jsonify({
            'success': True,
            'frameworks': frameworks
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test/run', methods=['POST'])
def run_user_tests():
    """Run user's tests with detailed output"""
    try:
        data = request.get_json()
        repo_path = data.get('repo_path', '.')
        framework = data.get('framework')
        verbose = data.get('verbose', True)
        use_docker = data.get('use_docker', False)
        
        test_executor.repo_path = Path(repo_path)
        
        if use_docker:
            result = test_executor.run_docker_tests(data.get('docker_image'))
        else:
            result = test_executor.run_tests(framework, verbose)
        
        return jsonify({
            'success': result.get('success', False),
            'result': result
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/diff/file', methods=['POST'])
def get_file_diff_api():
    """Get diff between two versions of a file"""
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        original_content = data.get('original_content', '')
        modified_content = data.get('modified_content', '')
        
        diff_data = diff_visualizer.get_file_diff(file_path, original_content, modified_content)
        
        return jsonify({
            'success': True,
            'diff': diff_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/session/<session_id>/metrics')
def get_session_metrics(session_id):
    """Get detailed metrics for a session"""
    try:
        session = sessions.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        metrics = {
            'session_id': session_id,
            'start_time': session.get('start_time'),
            'iterations': session.get('iterations', []),
            'current_state': session.get('current_state'),
            'errors': session.get('errors', []),
            'performance': session.get('performance', {})
        }
        
        return jsonify({
            'success': True,
            'metrics': metrics
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting BetterRepo2File UI server...")
    print("Access the application at: http://localhost:5001")
    app.run(debug=True, host='0.0.0.0', port=5001)
