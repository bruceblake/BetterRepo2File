"""
Profile Routes Blueprint for BetterRepo2File v2.0
Handles configuration profile management
"""
from flask import Blueprint, jsonify, request, current_app
import os
import json

profile_bp = Blueprint('profiles', __name__, url_prefix='/api/profiles')


# Default profiles
DEFAULT_PROFILES = {
    'frontend': {
        'name': 'Frontend Development',
        'description': 'Optimized for React, Vue, Angular projects',
        'extensions': ['.js', '.jsx', '.ts', '.tsx', '.css', '.scss', '.html', '.vue'],
        'ignore_patterns': ['node_modules', 'dist', 'build', '.next', 'coverage'],
        'token_budget': 200000,
        'llm_model': 'claude-3-sonnet'
    },
    'backend': {
        'name': 'Backend Development',
        'description': 'Optimized for Python, Java, Go backend services',
        'extensions': ['.py', '.java', '.go', '.rb', '.php', '.rs', '.scala'],
        'ignore_patterns': ['__pycache__', 'venv', 'target', 'vendor'],
        'token_budget': 300000,
        'llm_model': 'gpt-4'
    },
    'fullstack': {
        'name': 'Full Stack Development',
        'description': 'Balanced for full stack applications',
        'extensions': ['.js', '.ts', '.py', '.java', '.html', '.css', '.jsx', '.tsx'],
        'ignore_patterns': ['node_modules', '__pycache__', 'dist', 'build'],
        'token_budget': 400000,
        'llm_model': 'claude-3-opus'
    },
    'data-science': {
        'name': 'Data Science',
        'description': 'Optimized for notebooks and data analysis',
        'extensions': ['.ipynb', '.py', '.r', '.sql', '.csv', '.json'],
        'ignore_patterns': ['__pycache__', '.ipynb_checkpoints', 'data'],
        'token_budget': 350000,
        'llm_model': 'gemini-1.5-pro'
    },
    'documentation': {
        'name': 'Documentation',
        'description': 'Focus on documentation and markdown files',
        'extensions': ['.md', '.mdx', '.rst', '.txt', '.adoc'],
        'ignore_patterns': ['node_modules', '_build', 'site'],
        'token_budget': 150000,
        'llm_model': 'gpt-3.5-turbo'
    }
}


@profile_bp.route('/', methods=['GET'])
def list_profiles():
    """List all available profiles"""
    profiles = {}
    
    # Add default profiles
    profiles.update(DEFAULT_PROFILES)
    
    # Load custom profiles if they exist
    custom_profiles_path = os.path.join(
        current_app.config.get('PROFILES_DIR', 'profiles'),
        'custom_profiles.json'
    )
    
    if os.path.exists(custom_profiles_path):
        try:
            with open(custom_profiles_path, 'r') as f:
                custom_profiles = json.load(f)
                profiles.update(custom_profiles)
        except Exception as e:
            print(f"Error loading custom profiles: {e}")
    
    return jsonify(profiles)


@profile_bp.route('/<profile_name>', methods=['GET'])
def get_profile(profile_name):
    """Get a specific profile by name"""
    # Check default profiles
    if profile_name in DEFAULT_PROFILES:
        return jsonify(DEFAULT_PROFILES[profile_name])
    
    # Check custom profiles
    custom_profiles_path = os.path.join(
        current_app.config.get('PROFILES_DIR', 'profiles'),
        'custom_profiles.json'
    )
    
    if os.path.exists(custom_profiles_path):
        try:
            with open(custom_profiles_path, 'r') as f:
                custom_profiles = json.load(f)
                if profile_name in custom_profiles:
                    return jsonify(custom_profiles[profile_name])
        except Exception:
            pass
    
    return jsonify({'error': f'Profile "{profile_name}" not found'}), 404


@profile_bp.route('/', methods=['POST'])
def create_profile():
    """Create a new custom profile"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'description', 'extensions']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        profile_name = data.get('profile_name', data['name'].lower().replace(' ', '-'))
        
        # Check if profile already exists
        if profile_name in DEFAULT_PROFILES:
            return jsonify({'error': 'Cannot override default profile'}), 400
        
        # Load existing custom profiles
        profiles_dir = current_app.config.get('PROFILES_DIR', 'profiles')
        os.makedirs(profiles_dir, exist_ok=True)
        
        custom_profiles_path = os.path.join(profiles_dir, 'custom_profiles.json')
        custom_profiles = {}
        
        if os.path.exists(custom_profiles_path):
            with open(custom_profiles_path, 'r') as f:
                custom_profiles = json.load(f)
        
        # Add new profile
        custom_profiles[profile_name] = {
            'name': data['name'],
            'description': data['description'],
            'extensions': data['extensions'],
            'ignore_patterns': data.get('ignore_patterns', []),
            'token_budget': data.get('token_budget', 200000),
            'llm_model': data.get('llm_model', 'gpt-4')
        }
        
        # Save back to file
        with open(custom_profiles_path, 'w') as f:
            json.dump(custom_profiles, f, indent=2)
        
        return jsonify({
            'message': f'Profile "{profile_name}" created successfully',
            'profile': custom_profiles[profile_name]
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@profile_bp.route('/<profile_name>', methods=['DELETE'])
def delete_profile(profile_name):
    """Delete a custom profile"""
    if profile_name in DEFAULT_PROFILES:
        return jsonify({'error': 'Cannot delete default profile'}), 400
    
    try:
        custom_profiles_path = os.path.join(
            current_app.config.get('PROFILES_DIR', 'profiles'),
            'custom_profiles.json'
        )
        
        if not os.path.exists(custom_profiles_path):
            return jsonify({'error': 'Profile not found'}), 404
        
        with open(custom_profiles_path, 'r') as f:
            custom_profiles = json.load(f)
        
        if profile_name not in custom_profiles:
            return jsonify({'error': 'Profile not found'}), 404
        
        del custom_profiles[profile_name]
        
        with open(custom_profiles_path, 'w') as f:
            json.dump(custom_profiles, f, indent=2)
        
        return jsonify({'message': f'Profile "{profile_name}" deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@profile_bp.route('/apply', methods=['POST'])
def apply_profile():
    """Apply a profile to processing options"""
    try:
        data = request.get_json()
        profile_name = data.get('profile')
        
        if not profile_name:
            return jsonify({'error': 'Profile name required'}), 400
        
        # Get the profile
        profile = None
        
        if profile_name in DEFAULT_PROFILES:
            profile = DEFAULT_PROFILES[profile_name]
        else:
            custom_profiles_path = os.path.join(
                current_app.config.get('PROFILES_DIR', 'profiles'),
                'custom_profiles.json'
            )
            
            if os.path.exists(custom_profiles_path):
                with open(custom_profiles_path, 'r') as f:
                    custom_profiles = json.load(f)
                    if profile_name in custom_profiles:
                        profile = custom_profiles[profile_name]
        
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        # Build processing options based on profile
        options = {
            'file_types': profile.get('extensions', []),
            'ignore_patterns': profile.get('ignore_patterns', []),
            'token_budget': profile.get('token_budget', 200000),
            'llm_model': profile.get('llm_model', 'gpt-4'),
            'use_gitignore': True
        }
        
        # Merge with any additional options provided
        additional_options = data.get('options', {})
        options.update(additional_options)
        
        return jsonify({
            'profile': profile_name,
            'applied_options': options
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500