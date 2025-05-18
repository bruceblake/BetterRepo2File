"""
Git history analyzer for providing change impact insights
"""
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import subprocess
import json

try:
    from git import Repo
    GITPYTHON_AVAILABLE = True
except ImportError:
    GITPYTHON_AVAILABLE = False

class GitAnalyzer:
    """Analyzes git history to provide context about code changes"""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.repo = None
        
        if GITPYTHON_AVAILABLE:
            try:
                self.repo = Repo(repo_path)
                if self.repo.bare:
                    self.repo = None
            except:
                # Not a git repository or other error
                self.repo = None
    
    def is_git_repo(self) -> bool:
        """Check if the path is a git repository"""
        return self.repo is not None or os.path.exists(self.repo_path / '.git')
    
    def get_last_modified_info(self, file_path: str, line_number: Optional[int] = None) -> Dict:
        """Get last modification info for a file or specific line"""
        if not self.is_git_repo():
            return {}
        
        result = {
            'author': None,
            'date': None,
            'commit_hash': None,
            'commit_message': None
        }
        
        try:
            if GITPYTHON_AVAILABLE and self.repo:
                # Use GitPython for better performance
                if line_number:
                    # Use git blame for specific line
                    blame_info = self.repo.blame("HEAD", file_path)
                    for commit, lines in blame_info:
                        for line_info in lines:
                            if line_info[0] == line_number:
                                result['author'] = commit.author.name
                                result['date'] = commit.committed_datetime.isoformat()
                                result['commit_hash'] = commit.hexsha[:8]
                                result['commit_message'] = commit.summary
                                return result
                else:
                    # Get last commit that touched the file
                    commits = list(self.repo.iter_commits(paths=file_path, max_count=1))
                    if commits:
                        commit = commits[0]
                        result['author'] = commit.author.name
                        result['date'] = commit.committed_datetime.isoformat()
                        result['commit_hash'] = commit.hexsha[:8]
                        result['commit_message'] = commit.summary
            else:
                # Fallback to command line git
                cmd = ['git', '-C', str(self.repo_path), 'log', '-1', '--format=%an|%ai|%h|%s', file_path]
                output = subprocess.check_output(cmd, text=True).strip()
                
                if output:
                    parts = output.split('|', 3)
                    if len(parts) >= 4:
                        result['author'] = parts[0]
                        result['date'] = parts[1]
                        result['commit_hash'] = parts[2]
                        result['commit_message'] = parts[3]
        except Exception as e:
            # Silently fail if git operations fail
            pass
        
        return result
    
    def get_change_frequency(self, file_path: str, time_window_days: int = 90) -> int:
        """Get number of commits that touched a file in the given time window"""
        if not self.is_git_repo():
            return 0
        
        try:
            since_date = (datetime.now() - timedelta(days=time_window_days)).isoformat()
            
            if GITPYTHON_AVAILABLE and self.repo:
                commits = list(self.repo.iter_commits(
                    paths=file_path,
                    since=since_date
                ))
                return len(commits)
            else:
                # Fallback to command line git
                cmd = [
                    'git', '-C', str(self.repo_path), 'log',
                    '--since', since_date,
                    '--format=oneline',
                    file_path
                ]
                output = subprocess.check_output(cmd, text=True).strip()
                return len(output.splitlines()) if output else 0
        except:
            return 0
    
    def get_recent_contributors(self, file_path: str, limit: int = 3) -> List[str]:
        """Get list of recent contributors to a file"""
        if not self.is_git_repo():
            return []
        
        try:
            if GITPYTHON_AVAILABLE and self.repo:
                authors = []
                commits = self.repo.iter_commits(paths=file_path, max_count=10)
                
                for commit in commits:
                    author = commit.author.name
                    if author not in authors:
                        authors.append(author)
                    if len(authors) >= limit:
                        break
                
                return authors
            else:
                # Fallback to command line git
                cmd = [
                    'git', '-C', str(self.repo_path), 'log',
                    '--format=%an',
                    '-10',  # Look at last 10 commits
                    file_path
                ]
                output = subprocess.check_output(cmd, text=True).strip()
                
                if output:
                    authors = []
                    for author in output.splitlines():
                        if author not in authors:
                            authors.append(author)
                        if len(authors) >= limit:
                            break
                    return authors
                
                return []
        except:
            return []
    
    def get_recent_commits_for_area(self, query: str, max_commits: int = 5) -> List[Dict]:
        """Get recent commits related to a specific area/query"""
        if not self.is_git_repo():
            return []
        
        commits = []
        
        try:
            # Search commits by message
            if GITPYTHON_AVAILABLE and self.repo:
                for commit in self.repo.iter_commits(grep=query, max_count=max_commits):
                    commits.append({
                        'hash': commit.hexsha[:8],
                        'author': commit.author.name,
                        'date': commit.committed_datetime.isoformat(),
                        'message': commit.summary
                    })
            else:
                # Fallback to command line git
                cmd = [
                    'git', '-C', str(self.repo_path), 'log',
                    '--grep', query,
                    '--format=%h|%an|%ai|%s',
                    f'-{max_commits}'
                ]
                output = subprocess.check_output(cmd, text=True).strip()
                
                if output:
                    for line in output.splitlines():
                        parts = line.split('|', 3)
                        if len(parts) >= 4:
                            commits.append({
                                'hash': parts[0],
                                'author': parts[1],
                                'date': parts[2],
                                'message': parts[3]
                            })
        except:
            pass
        
        return commits
    
    def get_diff_summary(self, old_commit: Optional[str] = None, new_commit: str = "HEAD") -> Dict:
        """Get a summary of changes between two commits"""
        if not self.is_git_repo():
            return {}
        
        result = {
            "changed_files": [],
            "overall_summary_stats": "",
            "key_modified_functions": []
        }
        
        try:
            # If no old_commit specified, use HEAD~1 (parent of HEAD)
            if not old_commit:
                old_commit = "HEAD~1"
            
            if GITPYTHON_AVAILABLE and self.repo:
                # Get the diff between commits
                diff_index = self.repo.index.diff(old_commit, new_commit, create_patch=True)
                
                insertions = 0
                deletions = 0
                
                for diff_item in diff_index:
                    # Get file-level statistics
                    a_path = diff_item.a_path or diff_item.b_path
                    
                    # Count insertions and deletions
                    diff_text = diff_item.diff.decode('utf-8', errors='ignore')
                    file_insertions = len([line for line in diff_text.splitlines() if line.startswith('+') and not line.startswith('+++')])
                    file_deletions = len([line for line in diff_text.splitlines() if line.startswith('-') and not line.startswith('---')])
                    
                    insertions += file_insertions
                    deletions += file_deletions
                    
                    status = 'M'  # Modified
                    if diff_item.new_file:
                        status = 'A'  # Added
                    elif diff_item.deleted_file:
                        status = 'D'  # Deleted
                    elif diff_item.renamed_file:
                        status = 'R'  # Renamed
                    
                    result["changed_files"].append({
                        "file": a_path,
                        "status": status,
                        "insertions": file_insertions,
                        "deletions": file_deletions
                    })
                
                result["overall_summary_stats"] = f"+{insertions} lines, -{deletions} lines in {len(diff_index)} files"
                
                # Get key modified functions (simplified approach)
                for diff_item in diff_index:
                    if diff_item.a_path and diff_item.a_path.endswith(('.py', '.js', '.ts', '.java')):
                        # Try to extract function changes from diff
                        functions = self._extract_modified_functions(diff_item)
                        result["key_modified_functions"].extend(functions)
            
            else:
                # Fallback to command line git
                # Get list of changed files with stats
                cmd = ['git', '-C', str(self.repo_path), 'diff', '--stat', old_commit, new_commit]
                stat_output = subprocess.check_output(cmd, text=True).strip()
                
                # Parse the stat output
                files_changed = 0
                insertions = 0
                deletions = 0
                
                for line in stat_output.splitlines()[:-1]:  # Skip summary line
                    parts = line.strip().split('|')
                    if len(parts) == 2:
                        file_path = parts[0].strip()
                        stats = parts[1].strip()
                        
                        # Extract insertions and deletions
                        ins = stats.count('+')
                        dels = stats.count('-')
                        
                        result["changed_files"].append({
                            "file": file_path,
                            "status": "M",  # Default to modified
                            "insertions": ins,
                            "deletions": dels
                        })
                        
                        files_changed += 1
                        insertions += ins
                        deletions += dels
                
                # Extract summary from last line
                if stat_output:
                    last_line = stat_output.splitlines()[-1]
                    result["overall_summary_stats"] = last_line
                else:
                    result["overall_summary_stats"] = f"{files_changed} files changed"
                
                # Get diff for modified functions
                cmd = ['git', '-C', str(self.repo_path), 'diff', old_commit, new_commit]
                diff_output = subprocess.check_output(cmd, text=True).strip()
                
                # Simple extraction of modified functions
                current_file = None
                for line in diff_output.splitlines():
                    if line.startswith('diff --git'):
                        # Extract filename
                        parts = line.split()
                        if len(parts) >= 4:
                            current_file = parts[2].lstrip('a/')
                    elif line.startswith('@@') and current_file:
                        # Extract function context from hunk header
                        if ' ' in line:
                            context = line.split(' ', 4)[-1] if len(line.split(' ', 4)) > 4 else ''
                            if context and any(keyword in context for keyword in ['def ', 'function ', 'class ']):
                                result["key_modified_functions"].append({
                                    "file": current_file,
                                    "function": context.strip(),
                                    "change_type": "modified"
                                })
        
        except Exception as e:
            # Return what we have so far
            pass
        
        return result
    
    def _extract_modified_functions(self, diff_item):
        """Extract modified functions from a diff item"""
        functions = []
        
        try:
            diff_text = diff_item.diff.decode('utf-8', errors='ignore')
            current_function = None
            
            for line in diff_text.splitlines():
                # Look for function definitions in the diff context
                if line.startswith('@@'):
                    # Hunk header might contain function context
                    parts = line.split('@@')
                    if len(parts) >= 3:
                        context = parts[2].strip()
                        if context:
                            current_function = context
                elif (line.startswith('+') or line.startswith('-')) and not line.startswith('+++') and not line.startswith('---'):
                    # Look for function definitions in added/removed lines
                    content = line[1:].strip()
                    if any(content.startswith(keyword) for keyword in ['def ', 'function ', 'class ', 'public ', 'private ']):
                        func_name = self._extract_function_name(content)
                        if func_name:
                            change_type = 'added' if line.startswith('+') else 'deleted'
                            functions.append({
                                "file": diff_item.a_path or diff_item.b_path,
                                "function": func_name,
                                "change_type": change_type
                            })
                    elif current_function:
                        # If we're in a function context, mark it as modified
                        if current_function not in [f['function'] for f in functions]:
                            functions.append({
                                "file": diff_item.a_path or diff_item.b_path,
                                "function": current_function,
                                "change_type": "modified"
                            })
        except:
            pass
        
        return functions
    
    def _extract_function_name(self, line: str) -> Optional[str]:
        """Extract function name from a line of code"""
        # Simple extraction for common languages
        patterns = {
            'python': r'def\s+(\w+)\s*\(',
            'javascript': r'function\s+(\w+)\s*\(',
            'java': r'(?:public|private|protected)?\s*(?:static)?\s*\w+\s+(\w+)\s*\(',
            'class': r'class\s+(\w+)'
        }
        
        import re
        for pattern in patterns.values():
            match = re.search(pattern, line)
            if match:
                return match.group(1)
        
        return None
    
    def get_current_commit_hash(self) -> Optional[str]:
        """Get the current commit hash"""
        if not self.is_git_repo():
            return None
        
        try:
            if GITPYTHON_AVAILABLE and self.repo:
                return self.repo.head.commit.hexsha
            else:
                cmd = ['git', '-C', str(self.repo_path), 'rev-parse', 'HEAD']
                return subprocess.check_output(cmd, text=True).strip()
        except:
            return None
    
    def get_head_sha(self) -> Optional[str]:
        """Alias for get_current_commit_hash for consistency"""
        return self.get_current_commit_hash()