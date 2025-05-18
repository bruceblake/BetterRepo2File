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

def process_job(job_id, job_folder, vibe, stage, repo_file, planner_output, previous_output, feedback_log, repo_type=None, repo_path_input=None, repo_url=None):
    """Process a job in the background"""
    try:
        send_progress(job_id, 'extracting', 0, 0)
        
        # Handle repository selection
        repo_path = None
        
        if repo_type == 'local' and repo_path_input:
            # Use local repository path
            repo_path = repo_path_input
            if not os.path.exists(repo_path):
                raise Exception(f"Local repository path does not exist: {repo_path}")
                
        elif repo_type == 'github' and repo_url:
            # Clone GitHub repository
            repo_path = os.path.join(job_folder, 'repo')
            try:
                subprocess.run(['git', 'clone', repo_url, repo_path], 
                              check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
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
    
    # Get repository information
    repo_type = request.form.get('repo_type', '')  # 'local' or 'github'
    repo_path = request.form.get('repo_path', '')  # Local path
    repo_url = request.form.get('repo_url', '')    # GitHub URL
    
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
    thread = threading.Thread(target=process_job, args=(job_id, job_folder, vibe, stage, repo_file, planner_output, previous_output, feedback_log, repo_type, repo_path, repo_url))
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
    try:
        data = request.get_json()
        repo_path = data.get('repo_path', '.')
        test_framework = data.get('framework', 'auto')  # auto-detect by default
        
        # Import test parser
        from repo2file.git_diff_summarizer import TestResultParser
        
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
                    result = subprocess.run(cmd, 
                                          capture_output=True, 
                                          text=True,
                                          cwd=repo_path,
                                          timeout=300)  # 5 minute timeout
                    
                    if result.returncode != -1:  # Command exists
                        parser = TestResultParser()
                        test_result = parser.parse_output(result.stdout + result.stderr, framework)
                        
                        if test_result.total_tests > 0:  # Found actual tests
                            results = {
                                'framework': framework,
                                'passed': test_result.passed,
                                'failed': test_result.failed,
                                'errors': test_result.errors,
                                'skipped': test_result.skipped,
                                'failure_details': test_result.failure_details,
                                'raw_output': result.stdout + result.stderr
                            }
                            break
                except (subprocess.TimeoutExpired, FileNotFoundError):
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
                
                parser = TestResultParser()
                test_result = parser.parse_output(result.stdout + result.stderr, test_framework)
                
                results = {
                    'framework': test_framework,
                    'passed': test_result.passed,
                    'failed': test_result.failed,
                    'errors': test_result.errors,
                    'skipped': test_result.skipped,
                    'failure_details': test_result.failure_details,
                    'raw_output': result.stdout + result.stderr
                }
        
        if not results:
            return jsonify({'error': 'No test framework detected or tests found'}), 404
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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
                # For GitHub, we'd need to clone first or use the GitHub API
                context_summary = f"GitHub repository: {repo_info.get('url')}"
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

if __name__ == '__main__':
    print("Starting BetterRepo2File UI server...")
    print("Access the application at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
