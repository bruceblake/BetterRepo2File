"""
Configuration profiles for repo2file processing
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field

# Default profiles directory
PROFILES_DIR = Path.home() / '.repo2file' / 'profiles'
PROFILES_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class ProcessingProfile:
    """Configuration profile for processing"""
    name: str
    description: str = ""
    mode: str = "smart"  # standard, smart, token, ultra
    token_budget: int = 500000
    model: str = "gpt-4"
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    file_extensions: List[str] = field(default_factory=list)
    priority_patterns: Dict[str, float] = field(default_factory=dict)
    max_file_size: int = 1_000_000  # 1MB
    use_gitignore: bool = True
    truncation_strategy: str = "semantic"  # For ultra mode
    generate_manifest: bool = False  # For ultra mode
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'description': self.description,
            'mode': self.mode,
            'token_budget': self.token_budget,
            'model': self.model,
            'include_patterns': self.include_patterns,
            'exclude_patterns': self.exclude_patterns,
            'file_extensions': self.file_extensions,
            'priority_patterns': self.priority_patterns,
            'max_file_size': self.max_file_size,
            'use_gitignore': self.use_gitignore
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ProcessingProfile':
        """Create from dictionary"""
        return cls(**data)
    
    def save(self, profiles_dir: Path = PROFILES_DIR):
        """Save profile to disk"""
        profile_path = profiles_dir / f"{self.name}.json"
        with open(profile_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, name: str, profiles_dir: Path = PROFILES_DIR) -> Optional['ProcessingProfile']:
        """Load profile from disk"""
        profile_path = profiles_dir / f"{name}.json"
        if not profile_path.exists():
            return None
        
        with open(profile_path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    @classmethod
    def list_profiles(cls, profiles_dir: Path = PROFILES_DIR) -> List[str]:
        """List available profiles"""
        return [p.stem for p in profiles_dir.glob("*.json")]

# Default profiles
DEFAULT_PROFILES = {
    'frontend': ProcessingProfile(
        name='frontend',
        description='Frontend web development (React, Vue, Angular)',
        mode='smart',
        file_extensions=['.js', '.jsx', '.ts', '.tsx', '.vue', '.css', '.scss', '.html'],
        exclude_patterns=['node_modules/', 'dist/', 'build/', '*.min.js', '*.min.css'],
        priority_patterns={'**/components/**': 0.8, '**/pages/**': 0.7, '**/hooks/**': 0.6}
    ),
    
    'backend': ProcessingProfile(
        name='backend',
        description='Backend development (Python, Node.js, Java)',
        mode='smart',
        file_extensions=['.py', '.js', '.ts', '.java', '.go', '.rs'],
        exclude_patterns=['__pycache__/', 'venv/', 'node_modules/', 'target/'],
        priority_patterns={'**/models/**': 0.8, '**/controllers/**': 0.7, '**/services/**': 0.6}
    ),
    
    'datascience': ProcessingProfile(
        name='datascience',
        description='Data science and machine learning projects',
        mode='ultra',
        model='gpt-4',
        file_extensions=['.py', '.ipynb', '.r', '.jl'],
        exclude_patterns=['data/', 'datasets/', 'checkpoints/', '*.pkl', '*.h5'],
        priority_patterns={'**/*.ipynb': 0.9, '**/models/**': 0.8, '**/notebooks/**': 0.7}
    ),
    
    'documentation': ProcessingProfile(
        name='documentation',
        description='Documentation and technical writing',
        mode='standard',
        file_extensions=['.md', '.rst', '.txt', '.adoc'],
        priority_patterns={'README*': 1.0, 'CHANGELOG*': 0.8, 'docs/**': 0.7}
    ),
    
    'mobile': ProcessingProfile(
        name='mobile',
        description='Mobile app development (React Native, Flutter)',
        mode='smart',
        file_extensions=['.js', '.jsx', '.ts', '.tsx', '.dart', '.swift', '.kt'],
        exclude_patterns=['node_modules/', 'ios/Pods/', 'android/build/'],
        priority_patterns={'**/screens/**': 0.8, '**/components/**': 0.7}
    ),
    
    'microservices': ProcessingProfile(
        name='microservices',
        description='Microservices architecture',
        mode='ultra',
        token_budget=750000,
        exclude_patterns=['**/node_modules/', '**/target/', '**/build/'],
        priority_patterns={'**/api/**': 0.9, '**/services/**': 0.8, 'docker-compose*': 0.7}
    ),
    
    'gemini': ProcessingProfile(
        name='gemini',
        description='Optimized for Gemini 1.5 Pro with large context window',
        mode='ultra',
        model='gemini-1.5-pro',
        token_budget=1000000,  # 1M tokens for Gemini's large context
        file_extensions=[],  # Include all by default  
        exclude_patterns=['node_modules/', '__pycache__/', 'venv/', '.git/', 'dist/', 'build/'],
        priority_patterns={'**/README*': 1.0, '**/index.*': 0.9, '**/main.*': 0.8},
        truncation_strategy='middle_summarize',
        generate_manifest=True
    ),
}

class ProfileManager:
    """Manage processing profiles"""
    
    def __init__(self, profiles_dir: Path = PROFILES_DIR):
        self.profiles_dir = profiles_dir
        self.ensure_defaults()
    
    def ensure_defaults(self):
        """Ensure default profiles exist"""
        for profile in DEFAULT_PROFILES.values():
            profile_path = self.profiles_dir / f"{profile.name}.json"
            if not profile_path.exists():
                profile.save(self.profiles_dir)
    
    def get_profile(self, name: str) -> Optional[ProcessingProfile]:
        """Get a profile by name"""
        # Check custom profiles first
        profile = ProcessingProfile.load(name, self.profiles_dir)
        if profile:
            return profile
        
        # Check default profiles
        return DEFAULT_PROFILES.get(name)
    
    def list_profiles(self) -> List[Dict[str, str]]:
        """List all available profiles with descriptions"""
        profiles = []
        
        # List all JSON files in profiles directory
        for profile_path in self.profiles_dir.glob("*.json"):
            try:
                with open(profile_path, 'r') as f:
                    data = json.load(f)
                profiles.append({
                    'name': data.get('name', profile_path.stem),
                    'description': data.get('description', ''),
                    'mode': data.get('mode', 'smart')
                })
            except:
                pass
        
        return sorted(profiles, key=lambda p: p['name'])
    
    def create_profile(self, data: Dict) -> ProcessingProfile:
        """Create a new profile"""
        profile = ProcessingProfile.from_dict(data)
        profile.save(self.profiles_dir)
        return profile
    
    def update_profile(self, name: str, data: Dict) -> ProcessingProfile:
        """Update an existing profile"""
        profile = self.get_profile(name)
        if not profile:
            raise ValueError(f"Profile '{name}' not found")
        
        # Update fields
        for key, value in data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        profile.save(self.profiles_dir)
        return profile
    
    def delete_profile(self, name: str) -> bool:
        """Delete a profile"""
        # Don't delete default profiles
        if name in DEFAULT_PROFILES:
            raise ValueError(f"Cannot delete default profile '{name}'")
        
        profile_path = self.profiles_dir / f"{name}.json"
        if profile_path.exists():
            profile_path.unlink()
            return True
        return False

# Flask endpoints for profile management
from flask import Blueprint, request, jsonify

profiles_api = Blueprint('profiles', __name__, url_prefix='/api/profiles')
profile_manager = ProfileManager()

@profiles_api.route('/', methods=['GET'])
def list_profiles():
    """List all available profiles"""
    profiles = profile_manager.list_profiles()
    return jsonify(profiles)

@profiles_api.route('/<name>', methods=['GET'])
def get_profile(name):
    """Get a specific profile"""
    profile = profile_manager.get_profile(name)
    if not profile:
        return jsonify({'error': f'Profile "{name}" not found'}), 404
    return jsonify(profile.to_dict())

@profiles_api.route('/', methods=['POST'])
def create_profile():
    """Create a new profile"""
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400
    
    try:
        profile = profile_manager.create_profile(data)
        return jsonify(profile.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@profiles_api.route('/<name>', methods=['PUT'])
def update_profile(name):
    """Update an existing profile"""
    data = request.get_json()
    
    try:
        profile = profile_manager.update_profile(name, data)
        return jsonify(profile.to_dict())
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@profiles_api.route('/<name>', methods=['DELETE'])
def delete_profile(name):
    """Delete a profile"""
    try:
        if profile_manager.delete_profile(name):
            return jsonify({'success': True})
        else:
            return jsonify({'error': f'Profile "{name}" not found'}), 404
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500