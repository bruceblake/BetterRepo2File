import os
import sys
import tempfile
import uuid
import subprocess
import shutil
import time
import atexit
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, jsonify, send_file, abort
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload size
app.config['UPLOAD_FOLDER'] = os.path.join(tempfile.gettempdir(), 'repo2file_uploads')
app.config['REPO2FILE_PATH'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'repo2file', 'dump.py')
app.config['REPO2FILE_SMART_PATH'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'repo2file', 'dump_smart.py')
app.config['REPO2FILE_TOKEN_PATH'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'repo2file', 'dump_token_aware.py')
app.config['REPO2FILE_ULTRA_PATH'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'repo2file', 'dump_ultra.py')
app.config['EXCLUDE_FILE'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'repo2file', 'exclude.txt')

# Ensure temporary upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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
            repo_dir = os.path.join(temp_dir, 'repo')
            
            # Clone the repository
            try:
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
        cmd = [
            sys.executable,  # Python interpreter
            script_path,  # Path to dump.py or dump_smart.py
            input_path,  # Input directory
            output_file,  # Output file
        ]
        
        # Add options based on version
        if use_ultra_mode:
            cmd.extend(['--model', llm_model, '--budget', token_budget])
        else:
            cmd.append(exclusion_file)  # Exclusion file (either .gitignore or default)
        
        # Add file types if specified
        if file_types and not use_ultra_mode:
            cmd.extend(file_types)
        
        # Run repo2file script
        process = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        
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
    app.run(debug=True, host='0.0.0.0', port=5000)