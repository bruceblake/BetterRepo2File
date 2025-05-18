#!/usr/bin/env python3
"""Test script to verify Gemini profile works correctly"""

import subprocess
import sys
import os
import tempfile
import shutil

# Create a test repository
test_dir = tempfile.mkdtemp()
output_file = os.path.join(test_dir, "output.txt")

# Create some test files
os.makedirs(os.path.join(test_dir, "src"))
with open(os.path.join(test_dir, "README.md"), "w") as f:
    f.write("# Test Project\nThis is a test project for Gemini 1.5 Pro.")

with open(os.path.join(test_dir, "src", "main.py"), "w") as f:
    f.write("""
def main():
    '''Main function for testing'''
    print("Hello, Gemini 1.5 Pro!")
    
def helper_function():
    '''A helper function'''
    return "This is a helper"

if __name__ == "__main__":
    main()
""")

print(f"Created test repository at: {test_dir}")

# Test with Gemini profile
cmd = [
    sys.executable,
    "repo2file/dump_ultra.py",
    test_dir,
    output_file,
    "--profile", "gemini",
    "--budget", "1000000"
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
        print("\nSUCCESS! Gemini profile works correctly.")
        
        # Check the output file
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                content = f.read()
                print(f"\nOutput file size: {len(content)} characters")
                print("\nFirst 500 characters of output:")
                print(content[:500])
    else:
        print("\nFAILED! Error running with Gemini profile.")
        
finally:
    # Cleanup
    shutil.rmtree(test_dir)
    print(f"\nCleaned up test directory: {test_dir}")