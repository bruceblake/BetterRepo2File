#!/usr/bin/env python
"""
Test ultra mode with gemini profile
"""
import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import the dump_ultra module
from repo2file.dump_ultra import ProcessingProfile, UltraRepo2File
from app.profiles import DEFAULT_PROFILES
from pathlib import Path

def test_with_profile():
    # Test args
    test_args = [
        'dump_ultra.py',
        '/tmp/test_repo',
        '/tmp/test_output.txt',
        '--profile', 'gemini',
        '--budget', '1000000'
    ]
    
    print(f"Testing with args: {test_args}")
    
    # Load gemini profile
    profile_name = 'gemini'
    if profile_name in DEFAULT_PROFILES:
        app_profile = DEFAULT_PROFILES[profile_name]
        print(f"Loaded profile: {profile_name}")
        print(f"Model: {app_profile.model}")
        print(f"Token budget: {app_profile.token_budget}")
        
        # Convert to dump_ultra profile
        profile = ProcessingProfile(
            name=app_profile.name,
            token_budget=app_profile.token_budget,
            model=app_profile.model,
            exclude_patterns=app_profile.exclude_patterns,
            generate_manifest=getattr(app_profile, 'generate_manifest', True),
            truncation_strategy=getattr(app_profile, 'truncation_strategy', 'semantic')
        )
        
        print(f"Created ProcessingProfile:")
        print(f"  Model: {profile.model}")
        print(f"  Token budget: {profile.token_budget}")
        print(f"  Generate manifest: {profile.generate_manifest}")
        print(f"  Truncation strategy: {profile.truncation_strategy}")
    else:
        print(f"Profile {profile_name} not found")

if __name__ == '__main__':
    test_with_profile()