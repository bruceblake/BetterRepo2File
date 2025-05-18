#!/usr/bin/env python3
"""Test the iteration mode functionality"""

import subprocess
import sys
import os
from pathlib import Path

def test_iteration_mode():
    """Test the iteration mode"""
    # First, create a sample previous output file
    previous_output_content = """
# BetterRepo2File Output

My Vibe / Primary Goal: Create a modern web application with great performance

==================================================
SECTION 1: FOR AI PLANNING AGENT (e.g., Gemini 1.5 Pro in AI Studio)
Copy and paste this section into your Planning AI.
==================================================

Project Structure Summary:
- /app
  - app.py (Flask application)
  - /static
  - /templates

Key Technologies:
- Python Flask
- JavaScript
- CSS

[[FILE_START: app/app.py]]
from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return "Hello World"
[[FILE_END]]

==================================================
SECTION 2: FOR AI CODER (e.g., Claude Code in Claude)
==================================================

Project implementation details...
"""
    
    # Write the previous output file
    test_dir = Path("./test_iteration")
    test_dir.mkdir(exist_ok=True)
    
    previous_output_path = test_dir / "previous_output.txt"
    with open(previous_output_path, 'w') as f:
        f.write(previous_output_content)
    
    # Create a user feedback file
    user_feedback_path = test_dir / "feedback.txt"
    with open(user_feedback_path, 'w') as f:
        f.write("Please improve performance and add caching")
    
    # Run the iteration mode
    cmd = [
        sys.executable,
        "-m", "repo2file.dump_ultra",
        "iterate",
        "--current-repo-path", ".",
        "--previous-repo2file-output", str(previous_output_path),
        "--user-feedback-file", str(user_feedback_path),
        "--output", str(test_dir / "iteration-brief.md")
    ]
    
    print("Running command:", ' '.join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print("\nStdout:")
    print(result.stdout)
    print("\nStderr:")
    print(result.stderr)
    print(f"\nReturn code: {result.returncode}")
    
    # Check if output files were created
    output_path = test_dir / "iteration-brief.md"
    if output_path.exists():
        print(f"\nIteration brief created: {output_path}")
        with open(output_path, 'r') as f:
            print("Content preview:")
            print(f.read()[:500] + "...\n")
    else:
        print("\nError: Iteration brief was not created")

if __name__ == "__main__":
    test_iteration_mode()