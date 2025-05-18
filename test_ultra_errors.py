#!/usr/bin/env python3
"""Test ultra mode to see actual error messages"""

import subprocess
import sys
import os

def test_ultra_mode():
    """Test ultra mode to see actual error messages"""
    cmd = [
        sys.executable,
        "-m", "repo2file.dump_ultra",
        ".",
        "test_output.txt",
        "--profile", "gemini"
    ]
    
    print("Running ultra mode test...")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd="/home/proxyie/MySoftware/BetterRepo2File")
    
    print("Return code:", result.returncode)
    print("\nStdout:")
    print(result.stdout)
    print("\nStderr:")
    print(result.stderr)
    
    # Check output file content
    output_path = "/home/proxyie/MySoftware/BetterRepo2File/test_output.txt"
    if os.path.exists(output_path):
        with open(output_path, 'r') as f:
            content = f.read()
        
        # Find error patterns
        import re
        errors = re.findall(r'\[Error reading file: ([^\]]+)\]', content)
        if errors:
            print(f"\nFound {len(errors)} file reading errors:")
            for error in errors[:5]:  # Show first 5
                print(f"  - {error}")
    else:
        print("\nOutput file not created")

if __name__ == "__main__":
    test_ultra_mode()