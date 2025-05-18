"""
REST API for repo2file processing
"""
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import sys
import tempfile
import subprocess
import uuid
import shutil
from pathlib import Path
import time
from datetime import datetime

api = Blueprint('api', __name__, url_prefix='/api/v1')

# Configuration from main app
UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'repo2file_api')
SCRIPT_PATHS = {
    'standard': os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'repo2file', 'dump.py'),
    'smart': os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'repo2file', 'dump_smart.py'),
    'token': os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'repo2file', 'dump_token_aware.py'),
    'ultra': os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'repo2file', 'dump_ultra.py'),
}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@api.route('/process', methods=['POST'])
def process_files():
    """
    Process files or GitHub repository
    
    Request body:
    {
        "mode": "standard|smart|token|ultra",
        "github_url": "https://github.com/user/repo",  # OR
        "files": ["base64_encoded_file_contents"],
        "file_names": ["file1.py", "file2.js"],
        "options": {
            "file_types": [".py", ".js"],
            "use_gitignore": true,
            "model": "gpt-4",  # for ultra mode
            "token_budget": 500000  # for ultra mode
        }
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        mode = data.get('mode', 'smart')
        if mode not in SCRIPT_PATHS:
            return jsonify({'error': f'Invalid mode: {mode}'}), 400
        
        # Create operation ID
        operation_id = str(uuid.uuid4())
        temp_dir = os.path.join(UPLOAD_FOLDER, operation_id)
        os.makedirs(temp_dir, exist_ok=True)
        
        input_path = None
        output_file = os.path.join(temp_dir, 'output.txt')
        
        # Handle GitHub URL
        if 'github_url' in data:
            github_url = data['github_url']
            repo_dir = os.path.join(temp_dir, 'repo')
            
            # Clone repository
            try:
                subprocess.run(['git', 'clone', github_url, repo_dir], 
                              check=True, capture_output=True, text=True)
                input_path = repo_dir
            except subprocess.CalledProcessError as e:
                return jsonify({'error': f'Failed to clone repository: {e.stderr}'}), 400
        
        # Handle file uploads
        elif 'files' in data and 'file_names' in data:
            upload_dir = os.path.join(temp_dir, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            files = data['files']
            file_names = data['file_names']
            
            if len(files) != len(file_names):
                return jsonify({'error': 'Files and file_names must have same length'}), 400
            
            # Save files
            for i, (content, name) in enumerate(zip(files, file_names)):
                file_path = os.path.join(upload_dir, secure_filename(name))
                
                # Decode base64 content if needed
                import base64
                try:
                    if isinstance(content, str) and content.startswith('data:'):
                        # Remove data URL prefix
                        content = content.split(',', 1)[1]
                    
                    if isinstance(content, str):
                        # Try base64 decode
                        try:
                            content = base64.b64decode(content)
                        except:
                            # If not base64, treat as text
                            content = content.encode('utf-8')
                    
                    with open(file_path, 'wb') as f:
                        f.write(content)
                except Exception as e:
                    return jsonify({'error': f'Failed to save file {name}: {str(e)}'}), 400
            
            input_path = upload_dir
        else:
            return jsonify({'error': 'No input provided. Provide github_url or files'}), 400
        
        # Get options
        options = data.get('options', {})
        file_types = options.get('file_types', [])
        use_gitignore = options.get('use_gitignore', True)
        
        # Prepare command
        cmd = [sys.executable, SCRIPT_PATHS[mode], input_path, output_file]
        
        # Add mode-specific options
        if mode == 'ultra':
            model = options.get('model', 'gpt-4')
            budget = options.get('token_budget', 500000)
            cmd.extend(['--model', model, '--budget', str(budget)])
        else:
            # Standard modes use exclusion file
            gitignore_path = os.path.join(input_path, '.gitignore')
            if use_gitignore and os.path.exists(gitignore_path):
                cmd.append(gitignore_path)
            else:
                cmd.append('repo2file/exclude.txt')
            
            if file_types:
                cmd.extend(file_types)
        
        # Run processing
        start_time = time.time()
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        if process.returncode != 0:
            return jsonify({'error': f'Processing failed: {process.stderr}'}), 500
        
        # Read output
        if not os.path.exists(output_file):
            return jsonify({'error': 'Failed to generate output'}), 500
        
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Gather statistics
        stats = {
            'operation_id': operation_id,
            'mode': mode,
            'processing_time': time.time() - start_time,
            'output_size': len(content),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'operation_id': operation_id,
            'content': content,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/download/<operation_id>', methods=['GET'])
def download_output(operation_id):
    """Download processed output file"""
    # Validate operation_id
    if not operation_id or not all(c.isalnum() or c == '-' for c in operation_id):
        return jsonify({'error': 'Invalid operation ID'}), 400
    
    output_file = os.path.join(UPLOAD_FOLDER, operation_id, 'output.txt')
    
    if not os.path.exists(output_file):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(output_file, as_attachment=True, 
                    download_name=f'repo2file_{operation_id}.txt')

@api.route('/cleanup/<operation_id>', methods=['DELETE'])
def cleanup_operation(operation_id):
    """Clean up temporary files for an operation"""
    # Validate operation_id
    if not operation_id or not all(c.isalnum() or c == '-' for c in operation_id):
        return jsonify({'error': 'Invalid operation ID'}), 400
    
    temp_dir = os.path.join(UPLOAD_FOLDER, operation_id)
    
    if os.path.exists(temp_dir):
        try:
            shutil.rmtree(temp_dir)
            return jsonify({'success': True, 'message': 'Cleanup successful'})
        except Exception as e:
            return jsonify({'error': f'Cleanup failed: {str(e)}'}), 500
    
    return jsonify({'success': True, 'message': 'Directory not found'})

@api.route('/modes', methods=['GET'])
def get_modes():
    """Get available processing modes and their capabilities"""
    modes = {
        'standard': {
            'name': 'Standard Mode',
            'description': 'Basic file consolidation',
            'features': ['Simple file merging', 'Basic exclusion patterns'],
            'options': ['file_types', 'use_gitignore']
        },
        'smart': {
            'name': 'Smart Mode',
            'description': 'AI-optimized with intelligent filtering',
            'features': ['Binary file detection', 'Auto-generated file filtering', 
                        'Smart truncation', 'Lock file summarization'],
            'options': ['file_types', 'use_gitignore']
        },
        'token': {
            'name': 'Token-Aware Mode',
            'description': 'Manages 500K token budget',
            'features': ['Pathspec gitignore matching', 'Priority-based inclusion',
                        'Token budget management', 'Statistical reporting'],
            'options': ['file_types', 'use_gitignore']
        },
        'ultra': {
            'name': 'Ultra Mode',
            'description': 'Most advanced with semantic analysis',
            'features': ['Exact token counting', 'Semantic code analysis',
                        'Caching system', 'Multi-model support'],
            'options': ['model', 'token_budget'],
            'models': ['gpt-4', 'gpt-3.5-turbo', 'claude-3', 'llama']
        }
    }
    
    return jsonify(modes)

@api.route('/health', methods=['GET'])
def health_check():
    """API health check"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })

# CLI tool for testing API
if __name__ == '__main__':
    import requests
    import argparse
    
    parser = argparse.ArgumentParser(description='Test repo2file API')
    parser.add_argument('--url', default='http://localhost:5000/api/v1',
                       help='API base URL')
    parser.add_argument('--github', help='GitHub repository URL')
    parser.add_argument('--mode', default='smart', 
                       choices=['standard', 'smart', 'token', 'ultra'])
    parser.add_argument('--model', default='gpt-4', help='LLM model for ultra mode')
    parser.add_argument('--budget', type=int, default=500000, 
                       help='Token budget for ultra mode')
    
    args = parser.parse_args()
    
    # Test API
    if args.github:
        data = {
            'mode': args.mode,
            'github_url': args.github,
            'options': {
                'model': args.model,
                'token_budget': args.budget
            }
        }
        
        response = requests.post(f'{args.url}/process', json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success! Operation ID: {result['operation_id']}")
            print(f"Output size: {result['stats']['output_size']} bytes")
            print(f"Processing time: {result['stats']['processing_time']:.2f} seconds")
            
            # Save output
            with open(f"output_{result['operation_id']}.txt", 'w') as f:
                f.write(result['content'])
        else:
            print(f"Error: {response.json()}")
    else:
        # Just check health
        response = requests.get(f'{args.url}/health')
        print(response.json())