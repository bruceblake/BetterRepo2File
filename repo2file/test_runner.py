"""
Test runner module for executing and analyzing project tests
"""
import subprocess
import time
from pathlib import Path
from typing import Dict, Optional


def run_project_tests(repo_path: Path, test_command: str) -> Dict:
    """
    Run project tests using the specified command
    
    Args:
        repo_path: Path to the repository
        test_command: Command to run tests (e.g., "pytest", "npm test")
    
    Returns:
        Dict containing test results
    """
    try:
        # Change to repository directory and run test command
        cmd_parts = test_command.split()
        start_time = time.time()
        
        result = subprocess.run(
            cmd_parts,
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        elapsed_time = time.time() - start_time
        
        # Basic pass/fail detection
        passed = result.returncode == 0
        
        # Try to parse test output for more detailed results
        output = result.stdout + result.stderr
        test_summary = parse_test_output(output, test_command)
        
        return {
            'passed': passed,
            'exit_code': result.returncode,
            'elapsed_time': elapsed_time,
            'command': test_command,
            'summary': test_summary,
            'full_output': output[:5000]  # Limit output size
        }
        
    except subprocess.TimeoutExpired:
        return {
            'passed': False,
            'error': 'Test execution timeout (5 minutes)',
            'command': test_command
        }
    except Exception as e:
        return {
            'passed': False,
            'error': str(e),
            'command': test_command
        }


def parse_test_output(output: str, command: str) -> str:
    """
    Parse test output to extract summary based on test framework
    
    Args:
        output: Test command output
        command: Test command used
    
    Returns:
        Summary string
    """
    lines = output.splitlines()
    
    # Pytest patterns
    if 'pytest' in command or 'py.test' in command:
        for line in reversed(lines):
            if 'passed' in line and ('failed' in line or 'error' in line):
                return line.strip()
            if line.startswith('==='):
                return line.strip()
    
    # Jest/JavaScript test patterns
    if any(cmd in command for cmd in ['jest', 'npm test', 'yarn test']):
        for line in reversed(lines):
            if 'Tests:' in line and ('passed' in line or 'failed' in line):
                return line.strip()
            if 'Test Suites:' in line:
                return line.strip()
    
    # Mocha patterns
    if 'mocha' in command:
        for line in reversed(lines):
            if 'passing' in line and 'failing' in line:
                return line.strip()
    
    # Go test patterns
    if 'go test' in command:
        for line in reversed(lines):
            if line.startswith('PASS') or line.startswith('FAIL'):
                return line.strip()
    
    # Maven/Java patterns
    if any(cmd in command for cmd in ['mvn test', 'gradle test']):
        for line in reversed(lines):
            if 'Tests run:' in line and 'Failures:' in line:
                return line.strip()
            if line.startswith('[INFO] Tests run:'):
                return line.strip()
    
    # Generic patterns
    for line in reversed(lines):
        line_lower = line.lower()
        if any(word in line_lower for word in ['passed', 'failed', 'success', 'failure', 'error']):
            if any(char in line for char in [':', '=', '-']):
                return line.strip()
    
    # If no pattern matched, return a generic summary
    for line in reversed(lines[-10:]):  # Check last 10 lines
        if line.strip():
            return line.strip()
    
    return "Test completed (no summary found)"