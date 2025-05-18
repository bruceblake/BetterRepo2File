"""
Test runner module for executing and analyzing project tests
"""
import subprocess
import time
import json
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Optional


def check_docker_available() -> bool:
    """Check if Docker is available on the system"""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def build_test_docker_image(repo_path: Path) -> bool:
    """Build the test runner Docker image"""
    try:
        dockerfile_path = Path(__file__).parent.parent / 'Dockerfile'
        
        # Build the test-runner stage
        cmd = [
            'docker', 'build',
            '-f', str(dockerfile_path),
            '--target', 'test-runner',
            '-t', 'betterrepo2file-test-runner:latest',
            '.'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=repo_path.parent.parent)
        return result.returncode == 0
    except Exception as e:
        print(f"Failed to build Docker image: {e}")
        return False


def run_tests_in_docker(repo_path: Path, test_framework: str = 'auto') -> Dict:
    """Run tests inside a Docker container"""
    try:
        # Create a temporary directory for test results
        with tempfile.TemporaryDirectory() as temp_dir:
            results_dir = Path(temp_dir) / 'results'
            results_dir.mkdir()
            
            # Docker run command
            cmd = [
                'docker', 'run',
                '--rm',
                '-v', f'{repo_path}:/test:ro',  # Mount repo as read-only
                '-v', f'{results_dir}:/test_results',  # Mount results directory
                '-e', f'TEST_FRAMEWORK={test_framework}',
                '-e', 'REPO_PATH=/test',
                'betterrepo2file-test-runner:latest'
            ]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)  # 10 minute timeout
            elapsed_time = time.time() - start_time
            
            # Parse results based on framework
            test_results = parse_docker_test_results(results_dir, test_framework)
            
            return {
                'passed': result.returncode == 0,
                'exit_code': result.returncode,
                'elapsed_time': elapsed_time,
                'command': ' '.join(cmd),
                'framework': test_framework,
                'docker': True,
                'results': test_results,
                'full_output': result.stdout + result.stderr
            }
            
    except subprocess.TimeoutExpired:
        return {
            'passed': False,
            'error': 'Docker test execution timeout (10 minutes)',
            'framework': test_framework,
            'docker': True
        }
    except Exception as e:
        return {
            'passed': False,
            'error': str(e),
            'framework': test_framework,
            'docker': True
        }


def parse_docker_test_results(results_dir: Path, framework: str) -> Dict:
    """Parse test results from Docker container output files"""
    results = {
        'tests_run': 0,
        'tests_passed': 0,
        'tests_failed': 0,
        'test_errors': 0,
        'details': []
    }
    
    try:
        if framework in ['pytest', 'auto']:
            # Try to parse pytest JSON report
            pytest_report = results_dir / 'pytest_report.json'
            if pytest_report.exists():
                with open(pytest_report, 'r') as f:
                    data = json.load(f)
                    summary = data.get('summary', {})
                    results['tests_run'] = summary.get('total', 0)
                    results['tests_passed'] = summary.get('passed', 0)
                    results['tests_failed'] = summary.get('failed', 0)
                    results['test_errors'] = summary.get('error', 0)
                    
                    # Add test details
                    for test in data.get('tests', []):
                        results['details'].append({
                            'name': test.get('nodeid'),
                            'outcome': test.get('outcome'),
                            'duration': test.get('duration', 0)
                        })
        
        # Similar parsing for other frameworks...
        elif framework == 'jest':
            jest_report = results_dir / 'jest_report.json'
            if jest_report.exists():
                with open(jest_report, 'r') as f:
                    data = json.load(f)
                    results['tests_run'] = data.get('numTotalTests', 0)
                    results['tests_passed'] = data.get('numPassedTests', 0)
                    results['tests_failed'] = data.get('numFailedTests', 0)
        
        # Add more framework-specific parsing as needed
        
    except Exception as e:
        print(f"Error parsing test results: {e}")
    
    return results


def run_project_tests(repo_path: Path, test_command: str = None, use_docker: bool = None) -> Dict:
    """
    Run project tests using the specified command or Docker
    
    Args:
        repo_path: Path to the repository
        test_command: Command to run tests (e.g., "pytest", "npm test")
        use_docker: Whether to use Docker for test execution (None = auto-detect)
    
    Returns:
        Dict containing test results
    """
    # Auto-detect Docker availability if not specified
    if use_docker is None:
        use_docker = check_docker_available() and (repo_path.parent.parent / 'Dockerfile').exists()
    
    # If Docker is available and requested, build image and run tests
    if use_docker:
        # Build the Docker image if it doesn't exist
        if not subprocess.run(['docker', 'images', '-q', 'betterrepo2file-test-runner:latest'], 
                             capture_output=True, text=True).stdout.strip():
            if not build_test_docker_image(repo_path):
                # Fall back to local execution if Docker build fails
                use_docker = False
        
        if use_docker:
            framework = 'auto'
            if test_command:
                # Try to determine framework from command
                if 'pytest' in test_command:
                    framework = 'pytest'
                elif 'npm test' in test_command:
                    framework = 'npm'
                elif 'jest' in test_command:
                    framework = 'jest'
                elif 'go test' in test_command:
                    framework = 'go'
                # Add more framework detection as needed
            
            return run_tests_in_docker(repo_path, framework)
    
    # Fall back to local execution
    if not test_command:
        return {
            'passed': False,
            'error': 'No test command specified and Docker not available',
            'docker': False
        }
    
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
            'docker': False,
            'full_output': output[:5000]  # Limit output size
        }
        
    except subprocess.TimeoutExpired:
        return {
            'passed': False,
            'error': 'Test execution timeout (5 minutes)',
            'command': test_command,
            'docker': False
        }
    except Exception as e:
        return {
            'passed': False,
            'error': str(e),
            'command': test_command,
            'docker': False
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