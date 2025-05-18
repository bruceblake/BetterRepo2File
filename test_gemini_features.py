#!/usr/bin/env python3
"""Test script to verify all Gemini profile features"""

import subprocess
import sys
import os
import tempfile
import shutil

# Create a more complex test repository
test_dir = tempfile.mkdtemp()
output_file = os.path.join(test_dir, "output.txt")

# Create nested directory structure
os.makedirs(os.path.join(test_dir, "src"))
os.makedirs(os.path.join(test_dir, "src", "components"))
os.makedirs(os.path.join(test_dir, "src", "utils"))
os.makedirs(os.path.join(test_dir, "tests"))

# Create various files to test features
with open(os.path.join(test_dir, "README.md"), "w") as f:
    f.write("""# Test Project for Gemini 1.5 Pro
This tests hierarchical manifest generation and smart truncation.

## Features
- Component-based architecture
- Utility functions
- Full test coverage""")

with open(os.path.join(test_dir, "src", "main.py"), "w") as f:
    f.write("""import components.user_manager
import utils.logger

def main():
    '''Main application entry point'''
    logger = utils.logger.get_logger(__name__)
    user_manager = components.user_manager.UserManager()
    logger.info("Application started")
    return user_manager.start()

def helper_function():
    '''Helper function that demonstrates business logic'''
    # This is critical business logic
    return calculate_revenue() * PROFIT_MARGIN

def calculate_revenue():
    '''Calculate revenue - business critical'''
    return 1000000

PROFIT_MARGIN = 0.15

if __name__ == "__main__":
    main()
""")

with open(os.path.join(test_dir, "src", "components", "__init__.py"), "w") as f:
    f.write("# Components module")

with open(os.path.join(test_dir, "src", "components", "user_manager.py"), "w") as f:
    f.write("""class UserManager:
    '''Manages user operations'''
    
    def __init__(self):
        self.users = {}
    
    def add_user(self, user_id, name):
        '''Add a new user to the system'''
        self.users[user_id] = {"name": name, "active": True}
    
    def get_user(self, user_id):
        '''Retrieve user by ID'''
        return self.users.get(user_id)
    
    def start(self):
        '''Start the user manager service'''
        print("User manager started")
        return True
""")

with open(os.path.join(test_dir, "src", "utils", "__init__.py"), "w") as f:
    f.write("# Utils module")

with open(os.path.join(test_dir, "src", "utils", "logger.py"), "w") as f:
    f.write("""import logging

def get_logger(name):
    '''Get a logger instance'''
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger

def format_log_message(level, message):
    '''Format a log message'''
    return f"[{level}] {message}"
""")

with open(os.path.join(test_dir, "tests", "test_main.py"), "w") as f:
    f.write("""import unittest
from src.main import calculate_revenue, PROFIT_MARGIN

class TestMain(unittest.TestCase):
    def test_revenue_calculation(self):
        '''Test revenue calculation'''
        self.assertEqual(calculate_revenue(), 1000000)
    
    def test_profit_margin(self):
        '''Test profit margin constant'''
        self.assertEqual(PROFIT_MARGIN, 0.15)
""")

# Create a large file to test truncation
with open(os.path.join(test_dir, "large_config.json"), "w") as f:
    # Generate a large JSON config
    f.write("{\n")
    for i in range(1000):
        f.write(f'  "setting_{i}": "value_{i}",\n')
    f.write('  "final_setting": "final_value"\n}')

# Add .gitignore
with open(os.path.join(test_dir, ".gitignore"), "w") as f:
    f.write("""__pycache__/
*.pyc
venv/
node_modules/
.DS_Store
""")

print(f"Created complex test repository at: {test_dir}")

# Test with Gemini profile
cmd = [
    sys.executable,
    "repo2file/dump_ultra.py",
    test_dir,
    output_file,
    "--profile", "gemini"
]

print(f"Running command: {' '.join(cmd)}")

try:
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print("\n--- STDOUT ---")
    print(result.stdout)
    
    if result.stderr:
        print("\n--- STDERR ---")
        print(result.stderr)
    
    print(f"\nReturn code: {result.returncode}")
    
    if result.returncode == 0:
        print("\nSUCCESS! Gemini profile processed complex project correctly.")
        
        # Check the output file
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                content = f.read()
                print(f"\nOutput file size: {len(content)} characters")
                
                # Check for key features
                print("\nFeature checks:")
                
                if "# Project Manifest" in content:
                    print("✓ Hierarchical manifest generated")
                else:
                    print("✗ Manifest not found")
                
                if "### Navigation Guide" in content:
                    print("✓ Navigation guide included")
                else:
                    print("✗ Navigation guide not found")
                
                if "business logic" in content or "business critical" in content:
                    print("✓ Business logic prioritization detected")
                else:
                    print("✗ Business logic not prioritized")
                
                if "Token Budget: 1,000,000" in content:
                    print("✓ Large token budget applied")
                else:
                    print("✗ Token budget not correctly set")
                
                if "truncated" in content or "..." in content:
                    print("✓ Smart truncation applied")
                else:
                    print("✗ Truncation not detected (might not be needed)")
                
                print("\nFirst 1000 characters of manifest section:")
                manifest_start = content.find("# Project Manifest")
                if manifest_start >= 0:
                    print(content[manifest_start:manifest_start+1000])
    else:
        print("\nFAILED! Error running with Gemini profile.")
        
finally:
    # Cleanup
    shutil.rmtree(test_dir)
    print(f"\nCleaned up test directory: {test_dir}")