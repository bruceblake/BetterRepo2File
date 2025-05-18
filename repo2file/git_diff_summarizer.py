"""
Git diff analyzer and summarizer for the development loop
"""
import subprocess
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import time

@dataclass
class DiffSummary:
    """Summary of a git diff"""
    files_changed: List[str]
    additions: int
    deletions: int
    functions_modified: List[str]
    commit_sha: str
    commit_message: str
    author: str
    timestamp: str
    test_results: Optional[Dict] = None
    colored_diff: Optional[str] = None
    detailed_changes: Optional[List[Dict]] = None

class GitDiffSummarizer:
    """Analyzes git diffs and generates summaries"""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.last_commit_sha = None
        
    def get_current_commit(self) -> str:
        """Get the current HEAD commit SHA"""
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    
    def has_new_commits(self) -> bool:
        """Check if there are new commits since last check"""
        current_sha = self.get_current_commit()
        has_new = current_sha != self.last_commit_sha
        if has_new:
            self.last_commit_sha = current_sha
        return has_new
    
    def get_diff_summary(self, old_sha: Optional[str] = None, new_sha: str = 'HEAD', color: bool = True) -> DiffSummary:
        """Get summary of changes between commits"""
        # Get commit info
        commit_info = self._get_commit_info(new_sha)
        
        # Get diff stats
        if old_sha:
            diff_range = f"{old_sha}..{new_sha}"
        else:
            diff_range = f"{new_sha}^..{new_sha}"
        
        # Get colored full diff for display
        if color:
            color_diff_result = subprocess.run(
                ['git', 'diff', '--color=always', diff_range],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            colored_diff = color_diff_result.stdout
        else:
            colored_diff = None
        
        # Get detailed diff with stats per file
        detailed_cmd = ['git', 'diff', '--numstat', diff_range]
        detailed_result = subprocess.run(
            detailed_cmd,
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        detailed_changes = []
        files_changed = []
        additions = 0
        deletions = 0
        
        # Parse detailed changes
        for line in detailed_result.stdout.splitlines():
            if '\t' in line:
                parts = line.split('\t')
                if len(parts) >= 3:
                    add_count = int(parts[0]) if parts[0] != '-' else 0
                    del_count = int(parts[1]) if parts[1] != '-' else 0
                    filename = parts[2]
                    
                    detailed_changes.append({
                        'file': filename,
                        'additions': add_count,
                        'deletions': del_count,
                        'status': self._get_file_status(diff_range, filename)
                    })
                    
                    files_changed.append(filename)
                    additions += add_count
                    deletions += del_count
        
        # Get function changes
        functions_modified = self._get_modified_functions(diff_range)
        
        # Get test results if available
        test_results = self._run_tests()
        
        return DiffSummary(
            files_changed=files_changed,
            additions=additions,
            deletions=deletions,
            functions_modified=functions_modified,
            commit_sha=commit_info['sha'],
            commit_message=commit_info['message'],
            author=commit_info['author'],
            timestamp=commit_info['timestamp'],
            test_results=test_results,
            colored_diff=colored_diff,
            detailed_changes=detailed_changes
        )
    
    def _get_commit_info(self, sha: str) -> Dict:
        """Get commit metadata"""
        format_string = '%H%n%s%n%an%n%aI'
        result = subprocess.run(
            ['git', 'show', '-s', f'--format={format_string}', sha],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        lines = result.stdout.strip().split('\n')
        return {
            'sha': lines[0][:8],  # Short SHA
            'message': lines[1],
            'author': lines[2],
            'timestamp': lines[3]
        }
    
    def _get_file_status(self, diff_range: str, filename: str) -> str:
        """Get the status of a file (M: modified, A: added, D: deleted)"""
        result = subprocess.run(
            ['git', 'diff', '--name-status', diff_range],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        for line in result.stdout.splitlines():
            if filename in line:
                status = line.split('\t')[0]
                return status
        return 'M'  # Default to modified
    
    def _get_modified_functions(self, diff_range: str) -> List[str]:
        """Extract function names from the diff"""
        result = subprocess.run(
            ['git', 'diff', diff_range, '--function-context'],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        
        functions = set()
        # Look for function definitions in various languages
        patterns = [
            r'^\+\s*def\s+(\w+)',  # Python
            r'^\+\s*function\s+(\w+)',  # JavaScript
            r'^\+\s*const\s+(\w+)\s*=\s*\(',  # JS arrow functions
            r'^\+\s*public\s+\w+\s+(\w+)\s*\(',  # Java/C#
            r'^\+\s*func\s+(\w+)',  # Go
        ]
        
        for line in result.stdout.splitlines():
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    functions.add(match.group(1))
        
        return list(functions)
    
    def _run_tests(self) -> Optional[Dict]:
        """Run tests and get results"""
        # Try different test runners
        test_commands = [
            ['pytest', '--json-report', '--json-report-file=test-report.json'],
            ['npm', 'test', '--', '--json'],
            ['go', 'test', '-json', './...'],
            ['mvn', 'test'],
        ]
        
        for cmd in test_commands:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 127:  # Command exists
                # Parse test results
                if 'pytest' in cmd[0]:
                    return self._parse_pytest_results()
                elif 'npm' in cmd[0]:
                    return self._parse_jest_results(result.stdout)
                else:
                    # Basic pass/fail
                    return {
                        'passed': result.returncode == 0,
                        'total': None,
                        'failed': None,
                        'framework': cmd[0]
                    }
        
        return None
    
    def _parse_pytest_results(self) -> Dict:
        """Parse pytest JSON report"""
        report_path = self.repo_path / 'test-report.json'
        if report_path.exists():
            with open(report_path, 'r') as f:
                data = json.load(f)
                return {
                    'passed': data['summary']['passed'],
                    'failed': data['summary']['failed'],
                    'total': data['summary']['total'],
                    'framework': 'pytest'
                }
        return None
    
    def _parse_jest_results(self, output: str) -> Dict:
        """Parse Jest test output"""
        # Simple regex parsing for Jest output
        match = re.search(r'Tests:\s+(\d+) passed.*?(\d+) total', output)
        if match:
            passed = int(match.group(1))
            total = int(match.group(2))
            return {
                'passed': passed,
                'failed': total - passed,
                'total': total,
                'framework': 'jest'
            }
        return None

class CommitWatcher:
    """Watches for new commits in a repository"""
    
    def __init__(self, repo_path: Path, callback):
        self.repo_path = repo_path
        self.callback = callback
        self.summarizer = GitDiffSummarizer(repo_path)
        self.running = False
        
    def start(self, poll_interval: int = 10):
        """Start watching for commits"""
        self.running = True
        self.summarizer.last_commit_sha = self.summarizer.get_current_commit()
        
        while self.running:
            if self.summarizer.has_new_commits():
                # Get diff summary
                summary = self.summarizer.get_diff_summary()
                # Call the callback with the summary
                self.callback(summary)
            
            time.sleep(poll_interval)
    
    def stop(self):
        """Stop watching"""
        self.running = False