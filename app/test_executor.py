import subprocess
import json
import time
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re
try:
    from .logger import get_logger, log_step, log_metric, log_error
except ImportError:
    from logger import get_logger, log_step, log_metric, log_error

class TestExecutor:
    """Execute user's tests with detailed output and metrics"""
    
    def __init__(self, repo_path: str = '.'):
        self.repo_path = Path(repo_path)
        self.logger = get_logger()
        self.test_results = {}
    
    def detect_test_framework(self) -> Dict[str, any]:
        """Detect available test frameworks and test files"""
        frameworks = {
            'pytest': {
                'detected': False,
                'config_files': [],
                'test_files': [],
                'command': 'pytest'
            },
            'unittest': {
                'detected': False,
                'config_files': [],
                'test_files': [],
                'command': 'python -m unittest'
            },
            'jest': {
                'detected': False,
                'config_files': [],
                'test_files': [],
                'command': 'npm test'
            },
            'mocha': {
                'detected': False,
                'config_files': [],
                'test_files': [],
                'command': 'npm test'
            },
            'go': {
                'detected': False,
                'config_files': [],
                'test_files': [],
                'command': 'go test'
            },
            'cargo': {
                'detected': False,
                'config_files': [],
                'test_files': [],
                'command': 'cargo test'
            }
        }
        
        log_step("Detecting test frameworks", {"path": str(self.repo_path)})
        
        # Python tests
        pytest_files = list(self.repo_path.glob('**/test_*.py')) + \
                      list(self.repo_path.glob('**/*_test.py')) + \
                      list(self.repo_path.glob('**/tests/*.py'))
        
        if pytest_files:
            frameworks['pytest']['detected'] = True
            frameworks['pytest']['test_files'] = [str(f) for f in pytest_files]
            
            # Check for pytest config
            for config in ['pytest.ini', 'setup.cfg', 'tox.ini', 'pyproject.toml']:
                if (self.repo_path / config).exists():
                    frameworks['pytest']['config_files'].append(config)
        
        # JavaScript tests
        package_json = self.repo_path / 'package.json'
        if package_json.exists():
            with open(package_json) as f:
                pkg = json.load(f)
                
            scripts = pkg.get('scripts', {})
            deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
            
            if 'jest' in deps or 'test' in scripts and 'jest' in scripts.get('test', ''):
                frameworks['jest']['detected'] = True
                frameworks['jest']['config_files'].append('package.json')
                
                # Find Jest test files
                jest_files = list(self.repo_path.glob('**/*.test.js')) + \
                           list(self.repo_path.glob('**/*.spec.js')) + \
                           list(self.repo_path.glob('**/__tests__/*.js'))
                frameworks['jest']['test_files'] = [str(f) for f in jest_files]
            
            if 'mocha' in deps:
                frameworks['mocha']['detected'] = True
                frameworks['mocha']['config_files'].append('package.json')
        
        # Go tests
        go_files = list(self.repo_path.glob('**/*_test.go'))
        if go_files:
            frameworks['go']['detected'] = True
            frameworks['go']['test_files'] = [str(f) for f in go_files]
        
        # Rust tests
        cargo_toml = self.repo_path / 'Cargo.toml'
        if cargo_toml.exists():
            frameworks['cargo']['detected'] = True
            frameworks['cargo']['config_files'].append('Cargo.toml')
        
        detected = {k: v for k, v in frameworks.items() if v['detected']}
        log_metric("detected_frameworks", len(detected))
        return detected
    
    def run_tests(self, framework: str = None, verbose: bool = True) -> Dict:
        """Run tests with the specified framework or auto-detect"""
        start_time = time.time()
        
        # Detect frameworks if not specified
        if not framework:
            detected = self.detect_test_framework()
            if not detected:
                return {
                    'success': False,
                    'error': 'No test frameworks detected',
                    'frameworks': {}
                }
            
            # Use the first detected framework
            framework = list(detected.keys())[0]
            self.logger.info(f"Auto-selected framework: {framework}")
        
        log_step(f"Running {framework} tests")
        
        # Run tests based on framework
        if framework == 'pytest':
            result = self._run_pytest(verbose)
        elif framework == 'jest':
            result = self._run_jest(verbose)
        elif framework == 'go':
            result = self._run_go_tests(verbose)
        elif framework == 'cargo':
            result = self._run_cargo_tests(verbose)
        else:
            result = self._run_generic_tests(framework, verbose)
        
        # Add execution time
        result['execution_time'] = time.time() - start_time
        log_metric("test_execution_time", result['execution_time'])
        
        return result
    
    def _run_pytest(self, verbose: bool) -> Dict:
        """Run pytest with detailed output"""
        cmd = ['pytest']
        
        # Add options for detailed output
        if verbose:
            cmd.extend(['-v', '--tb=short'])
        
        # Add JSON report if available
        cmd.extend(['--json-report', '--json-report-file=pytest_report.json'])
        
        # Add coverage if available
        cmd.extend(['--cov', '--cov-report=html', '--cov-report=term'])
        
        result = self._execute_command(cmd, 'pytest')
        
        # Parse JSON report if available
        report_file = self.repo_path / 'pytest_report.json'
        if report_file.exists():
            with open(report_file) as f:
                result['detailed_report'] = json.load(f)
        
        return result
    
    def _run_jest(self, verbose: bool) -> Dict:
        """Run Jest tests with detailed output"""
        cmd = ['npm', 'test']
        
        # Add options for detailed output
        env = os.environ.copy()
        if verbose:
            env['CI'] = 'true'  # Prevents Jest from running in watch mode
            cmd.extend(['--', '--verbose', '--coverage'])
        
        result = self._execute_command(cmd, 'jest', env=env)
        
        # Parse coverage report if available
        coverage_file = self.repo_path / 'coverage' / 'coverage-summary.json'
        if coverage_file.exists():
            with open(coverage_file) as f:
                result['coverage'] = json.load(f)
        
        return result
    
    def _run_go_tests(self, verbose: bool) -> Dict:
        """Run Go tests with detailed output"""
        cmd = ['go', 'test']
        
        if verbose:
            cmd.extend(['-v', '-cover'])
        
        # Run for all packages
        cmd.append('./...')
        
        result = self._execute_command(cmd, 'go')
        
        # Parse Go test output
        result['parsed'] = self._parse_go_test_output(result.get('stdout', ''))
        
        return result
    
    def _run_cargo_tests(self, verbose: bool) -> Dict:
        """Run Rust tests with Cargo"""
        cmd = ['cargo', 'test']
        
        if verbose:
            cmd.append('--verbose')
        
        result = self._execute_command(cmd, 'cargo')
        
        # Parse Cargo test output
        result['parsed'] = self._parse_cargo_test_output(result.get('stdout', ''))
        
        return result
    
    def _run_generic_tests(self, framework: str, verbose: bool) -> Dict:
        """Run generic test command"""
        # Try to find test command in package.json or Makefile
        package_json = self.repo_path / 'package.json'
        if package_json.exists():
            with open(package_json) as f:
                pkg = json.load(f)
            
            if 'test' in pkg.get('scripts', {}):
                return self._execute_command(['npm', 'test'], framework)
        
        makefile = self.repo_path / 'Makefile'
        if makefile.exists():
            with open(makefile) as f:
                content = f.read()
            
            if 'test:' in content:
                return self._execute_command(['make', 'test'], framework)
        
        return {
            'success': False,
            'error': f'No test command found for {framework}'
        }
    
    def _execute_command(self, cmd: List[str], framework: str, env: dict = None, cwd: str = None) -> Dict:
        """Execute a test command and capture output"""
        self.logger.info(f"Executing: {' '.join(cmd)}")
        
        # Use provided cwd or default to repo_path
        working_dir = cwd if cwd else self.repo_path
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=working_dir,
                env=env or os.environ,
                universal_newlines=True,
                bufsize=1
            )
            
            stdout_lines = []
            stderr_lines = []
            
            # Stream output in real-time
            while True:
                stdout_line = process.stdout.readline()
                stderr_line = process.stderr.readline()
                
                if stdout_line:
                    stdout_lines.append(stdout_line.rstrip())
                    self.logger.debug(f"[{framework}] {stdout_line.rstrip()}")
                
                if stderr_line:
                    stderr_lines.append(stderr_line.rstrip())
                    self.logger.debug(f"[{framework} ERROR] {stderr_line.rstrip()}")
                
                if not stdout_line and not stderr_line and process.poll() is not None:
                    break
            
            return_code = process.poll()
            
            return {
                'success': return_code == 0,
                'return_code': return_code,
                'stdout': '\n'.join(stdout_lines),
                'stderr': '\n'.join(stderr_lines),
                'command': ' '.join(cmd),
                'framework': framework
            }
            
        except Exception as e:
            log_error(f"Failed to execute {framework} tests", e)
            return {
                'success': False,
                'error': str(e),
                'command': ' '.join(cmd),
                'framework': framework
            }
    
    def _parse_go_test_output(self, output: str) -> Dict:
        """Parse Go test output for detailed results"""
        lines = output.split('\n')
        tests = {}
        coverage = None
        
        for line in lines:
            # Parse test results
            if line.startswith('--- PASS:') or line.startswith('--- FAIL:'):
                parts = line.split()
                if len(parts) >= 3:
                    status = 'pass' if 'PASS' in parts[1] else 'fail'
                    test_name = parts[2]
                    duration = parts[3].strip('()') if len(parts) > 3 else None
                    tests[test_name] = {
                        'status': status,
                        'duration': duration
                    }
            
            # Parse coverage
            if 'coverage:' in line:
                match = re.search(r'coverage: (\d+\.\d+)%', line)
                if match:
                    coverage = float(match.group(1))
        
        return {
            'tests': tests,
            'coverage': coverage,
            'passed': sum(1 for t in tests.values() if t['status'] == 'pass'),
            'failed': sum(1 for t in tests.values() if t['status'] == 'fail')
        }
    
    def _parse_cargo_test_output(self, output: str) -> Dict:
        """Parse Cargo test output for detailed results"""
        lines = output.split('\n')
        tests = {}
        summary = {}
        
        for line in lines:
            # Parse test results
            if '... ok' in line or '... FAILED' in line:
                parts = line.split(' ... ')
                if len(parts) == 2:
                    test_name = parts[0].strip()
                    status = 'pass' if 'ok' in parts[1] else 'fail'
                    tests[test_name] = {'status': status}
            
            # Parse summary
            if 'test result:' in line:
                match = re.search(r'(\d+) passed.*(\d+) failed', line)
                if match:
                    summary['passed'] = int(match.group(1))
                    summary['failed'] = int(match.group(2))
        
        return {
            'tests': tests,
            'summary': summary
        }
    
    def run_docker_tests(self, image: str = None) -> Dict:
        """Run tests inside Docker container"""
        if not image:
            # Search for docker-compose files in repo and subdirectories
            import glob
            compose_patterns = [
                str(self.repo_path / 'docker-compose.yml'),
                str(self.repo_path / 'docker-compose.yaml'),
                str(self.repo_path / '**/docker-compose.yml'),
                str(self.repo_path / '**/docker-compose.yaml'),
                str(self.repo_path / 'docker-compose.*.yml'),
                str(self.repo_path / 'docker-compose.*.yaml')
            ]
            
            compose_file = None
            for pattern in compose_patterns:
                matches = glob.glob(pattern, recursive=True)
                if matches:
                    compose_file = matches[0]
                    self.logger.info(f"Found docker-compose file: {compose_file}")
                    break
            
            if compose_file:
                return self._run_docker_compose_tests(compose_file)
            else:
                return {'error': 'No Docker image specified and no docker-compose file found'}
        
        # Run with specified image
        # First check what test framework is available
        test_command = self._get_docker_test_command()
        
        cmd = [
            'docker', 'run', '--rm',
            '-v', f'{self.repo_path}:/app',
            '-w', '/app',
            image,
            'sh', '-c', test_command
        ]
        
        return self._execute_command(cmd, 'docker')
    
    def _get_docker_test_command(self) -> str:
        """Determine the appropriate test command to run in Docker"""
        # Check for various test frameworks/files
        if (self.repo_path / 'package.json').exists():
            return 'npm test'
        elif (self.repo_path / 'setup.py').exists() or (self.repo_path / 'pyproject.toml').exists():
            return 'pytest || python -m pytest || python -m unittest discover'
        elif (self.repo_path / 'go.mod').exists():
            return 'go test ./...'
        elif (self.repo_path / 'Cargo.toml').exists():
            return 'cargo test'
        elif (self.repo_path / 'Makefile').exists():
            return 'make test'
        else:
            # Try common test commands
            return 'make test || npm test || pytest || go test ./... || cargo test'
    
    def _run_docker_compose_tests(self, compose_file: str = None) -> Dict:
        """Run tests using docker-compose"""
        if compose_file:
            # Use the found compose file
            compose_dir = os.path.dirname(compose_file)
            compose_name = os.path.basename(compose_file)
            cmd = ['docker-compose', '-f', compose_name, '--profile', 'test', 'up', '--build', '--exit-code-from', 'test']
            return self._execute_command(cmd, 'docker-compose', cwd=compose_dir)
        else:
            # Fallback to default
            cmd = ['docker-compose', '--profile', 'test', 'up', '--build', '--exit-code-from', 'test']
            return self._execute_command(cmd, 'docker-compose')


# Global test executor instance
test_executor = TestExecutor()

# Convenience functions
def detect_test_framework() -> Dict:
    return test_executor.detect_test_framework()

def run_tests(framework: str = None, verbose: bool = True) -> Dict:
    return test_executor.run_tests(framework, verbose)

def run_docker_tests(image: str = None) -> Dict:
    return test_executor.run_docker_tests(image)