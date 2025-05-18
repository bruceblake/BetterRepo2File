"""
Git repository analysis functionality for commit tracking and diff generation
"""
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Optional

class GitAnalyzer:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        
    def get_recent_commits(self, branch: str = "main", limit: int = 10) -> List[Dict]:
        """Get recent commits with their information"""
        try:
            cmd = [
                "git", "log", 
                f"--max-count={limit}",
                "--pretty=format:%H|%an|%ae|%at|%s",
                branch
            ]
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|', 4)
                    commits.append({
                        'sha': parts[0],
                        'author': parts[1],
                        'email': parts[2],
                        'timestamp': int(parts[3]),
                        'message': parts[4]
                    })
            
            return commits
            
        except subprocess.CalledProcessError as e:
            print(f"Error getting commits: {e}")
            return []
    
    def get_commit_diff(self, sha: str) -> Dict:
        """Get the diff for a specific commit"""
        try:
            # Get files changed
            cmd_files = ["git", "diff-tree", "--no-commit-id", "--name-status", "-r", sha]
            result_files = subprocess.run(
                cmd_files,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            files_changed = []
            for line in result_files.stdout.strip().split('\n'):
                if line:
                    status, filename = line.split('\t', 1)
                    files_changed.append({
                        'status': status,
                        'filename': filename
                    })
            
            # Get diff stats
            cmd_stats = ["git", "diff-tree", "--numstat", "-r", sha]
            result_stats = subprocess.run(
                cmd_stats,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            diff_stats = {
                'additions': 0,
                'deletions': 0,
                'files': {}
            }
            
            for line in result_stats.stdout.strip().split('\n')[1:]:  # Skip header
                if line:
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        additions = int(parts[0]) if parts[0] != '-' else 0
                        deletions = int(parts[1]) if parts[1] != '-' else 0
                        filename = parts[2]
                        
                        diff_stats['additions'] += additions
                        diff_stats['deletions'] += deletions
                        diff_stats['files'][filename] = {
                            'additions': additions,
                            'deletions': deletions
                        }
            
            # Get actual diff content
            cmd_diff = ["git", "show", "--format=", sha]
            result_diff = subprocess.run(
                cmd_diff,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            return {
                'sha': sha,
                'files_changed': files_changed,
                'stats': diff_stats,
                'diff_content': result_diff.stdout
            }
            
        except subprocess.CalledProcessError as e:
            print(f"Error getting diff for {sha}: {e}")
            return {}
    
    def get_commits_between(self, from_sha: str, to_sha: str = "HEAD") -> List[Dict]:
        """Get commits between two points"""
        try:
            cmd = [
                "git", "log",
                "--pretty=format:%H|%an|%at|%s",
                f"{from_sha}..{to_sha}"
            ]
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|', 3)
                    commits.append({
                        'sha': parts[0],
                        'author': parts[1],
                        'timestamp': int(parts[2]),
                        'message': parts[3]
                    })
            
            return commits
            
        except subprocess.CalledProcessError as e:
            print(f"Error getting commits between {from_sha} and {to_sha}: {e}")
            return []
    
    def get_combined_diff(self, from_sha: str, to_sha: str = "HEAD") -> Dict:
        """Get combined diff between two commits"""
        try:
            cmd = ["git", "diff", "--numstat", from_sha, to_sha]
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            stats = {
                'additions': 0,
                'deletions': 0,
                'files': []
            }
            
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        additions = int(parts[0]) if parts[0] != '-' else 0
                        deletions = int(parts[1]) if parts[1] != '-' else 0
                        
                        stats['additions'] += additions
                        stats['deletions'] += deletions
                        stats['files'].append({
                            'filename': parts[2],
                            'additions': additions,
                            'deletions': deletions
                        })
            
            return stats
            
        except subprocess.CalledProcessError as e:
            print(f"Error getting combined diff: {e}")
            return {}