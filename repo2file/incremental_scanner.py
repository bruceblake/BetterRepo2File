"""
Incremental Scanner for BetterRepo2File
Implements F02: Incremental-Scan Mode
"""
import subprocess
import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Set
import logging

logger = logging.getLogger(__name__)

class IncrementalScanner:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        self.cache_dir = self.repo_path / '.betterrepo2file_cache'
        self.last_scan_file = self.cache_dir / 'last_scan_sha.txt'
        self.ast_cache_file = self.cache_dir / 'ast_cache.json'
        self.embeddings_cache_file = self.cache_dir / 'embeddings_cache.json'
        
    def ensure_cache_dir(self):
        """Create cache directory if it doesn't exist"""
        self.cache_dir.mkdir(exist_ok=True)
        
    def get_last_scan_sha(self) -> Optional[str]:
        """Get the commit SHA from the last scan"""
        if self.last_scan_file.exists():
            return self.last_scan_file.read_text().strip()
        return None
    
    def set_last_scan_sha(self, commit_sha: str):
        """Save the current commit SHA as the last scan point"""
        self.ensure_cache_dir()
        self.last_scan_file.write_text(commit_sha)
    
    def get_current_commit_sha(self) -> Optional[str]:
        """Get the current HEAD commit SHA"""
        try:
            result = subprocess.run(
                ['git', '-C', str(self.repo_path), 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting current commit SHA: {e}")
            return None
    
    def get_changed_files(self) -> Optional[Dict[str, List[str]]]:
        """Get files that have changed since the last scan"""
        last_sha = self.get_last_scan_sha()
        current_sha = self.get_current_commit_sha()
        
        if not current_sha:
            logger.warning("Could not determine current commit SHA. Performing full scan.")
            return None
        
        if last_sha is None:
            logger.info("No last scan SHA found. Performing full scan.")
            return None
        
        if last_sha == current_sha:
            # Check for uncommitted changes
            try:
                result = subprocess.run(
                    ['git', '-C', str(self.repo_path), 'status', '--porcelain'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                if result.stdout.strip():
                    # Parse uncommitted changes
                    uncommitted = self._parse_git_status(result.stdout)
                    return uncommitted
                else:
                    logger.info("No changes since last scan.")
                    return {"changed": [], "deleted": []}
            except subprocess.CalledProcessError as e:
                logger.error(f"Error checking git status: {e}")
                return None
        
        try:
            # Get committed changes
            result = subprocess.run(
                ['git', '-C', str(self.repo_path), 'diff', '--name-status', last_sha, current_sha],
                capture_output=True,
                text=True,
                check=True
            )
            
            changed_files = []
            deleted_files = []
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                    
                parts = line.split('\t')
                status = parts[0]
                file_path = parts[-1]
                
                # Filter by relevant file types
                if not self._is_relevant_file(file_path):
                    continue
                
                if status.startswith('D'):
                    deleted_files.append(file_path)
                else:  # M, A, R (renamed), C (copied)
                    changed_files.append(file_path)
            
            # Also get uncommitted changes
            uncommitted = self._get_uncommitted_changes()
            changed_files.extend(uncommitted.get('changed', []))
            deleted_files.extend(uncommitted.get('deleted', []))
            
            # Remove duplicates
            changed_files = list(set(changed_files))
            deleted_files = list(set(deleted_files))
            
            logger.info(f"Found {len(changed_files)} changed files and {len(deleted_files)} deleted files")
            return {"changed": changed_files, "deleted": deleted_files}
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error running git diff: {e}")
            return None
    
    def _parse_git_status(self, status_output: str) -> Dict[str, List[str]]:
        """Parse git status --porcelain output"""
        changed = []
        deleted = []
        
        for line in status_output.strip().split('\n'):
            if not line:
                continue
                
            status = line[:2]
            file_path = line[3:]
            
            if not self._is_relevant_file(file_path):
                continue
            
            if 'D' in status:
                deleted.append(file_path)
            else:
                changed.append(file_path)
        
        return {"changed": changed, "deleted": deleted}
    
    def _get_uncommitted_changes(self) -> Dict[str, List[str]]:
        """Get uncommitted changes from working directory"""
        try:
            result = subprocess.run(
                ['git', '-C', str(self.repo_path), 'ls-files', '--modified', '--others', '--exclude-standard'],
                capture_output=True,
                text=True,
                check=True
            )
            
            changed_files = []
            for file_path in result.stdout.strip().split('\n'):
                if file_path and self._is_relevant_file(file_path):
                    changed_files.append(file_path)
            
            return {"changed": changed_files, "deleted": []}
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting uncommitted changes: {e}")
            return {"changed": [], "deleted": []}
    
    def _is_relevant_file(self, file_path: str) -> bool:
        """Check if file should be included in scan"""
        # Skip common non-code files
        excluded_patterns = {
            '.git/', '__pycache__/', 'node_modules/', '.pytest_cache/',
            '.next/', 'dist/', 'build/', 'coverage/', '.nyc_output/'
        }
        
        for pattern in excluded_patterns:
            if pattern in file_path:
                return False
        
        # Include only code files
        code_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.hpp',
            '.c', '.h', '.cs', '.rb', '.go', '.rs', '.swift', '.kt',
            '.scala', '.php', '.vue', '.dart', '.r', '.m', '.mm'
        }
        
        return any(file_path.endswith(ext) for ext in code_extensions)
    
    def load_ast_cache(self) -> Dict:
        """Load cached ASTs from disk"""
        if self.ast_cache_file.exists():
            try:
                with open(self.ast_cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading AST cache: {e}")
        return {}
    
    def save_ast_cache(self, ast_cache: Dict):
        """Save AST cache to disk"""
        self.ensure_cache_dir()
        try:
            with open(self.ast_cache_file, 'w') as f:
                json.dump(ast_cache, f)
        except Exception as e:
            logger.error(f"Error saving AST cache: {e}")
    
    def scan(self, force_full: bool = False) -> List['FileInfo']:
        """Perform incremental or full scan based on changes"""
        # Import FileInfo from dump_ultra if available
        try:
            from .dump_ultra import FileInfo
        except ImportError:
            # Fallback to simple implementation
            from dataclasses import dataclass
            @dataclass
            class FileInfo:
                path: Path
                rel_path: str
                size: int
                is_binary: bool = False
                language: str = None
                importance_score: float = 1.0
                token_count: int = 0
                is_critical: bool = False
                is_generated: bool = False
                semantic_data: Dict = None
        
        if force_full:
            logger.info("Forcing full scan")
            scan_result = self._full_scan()
        else:
            changes = self.get_changed_files()
            
            if changes is None:
                # Something went wrong or first scan
                scan_result = self._full_scan()
            elif not changes['changed'] and not changes['deleted']:
                # No changes, return cached data
                logger.info("No changes detected, using cached data")
                scan_result = {
                    'ast_cache': self.load_ast_cache(),
                    'scan_type': 'cached',
                    'files_scanned': []
                }
            else:
                # Perform incremental scan
                scan_result = self._incremental_scan(changes)
        
        # Convert to FileInfo objects
        file_infos = []
        ast_cache = scan_result.get('ast_cache', {})
        
        for file_path, ast_data in ast_cache.items():
            full_path = self.repo_path / file_path
            if full_path.exists():
                file_info = FileInfo(
                    path=full_path,
                    rel_path=file_path,
                    size=full_path.stat().st_size,
                    is_binary=self._is_binary_file(full_path),
                    language=self._detect_language(file_path),
                    importance_score=1.0,
                    semantic_data=ast_data
                )
                file_infos.append(file_info)
        
        logger.info(f"Returning {len(file_infos)} FileInfo objects")
        return file_infos
    
    def _full_scan(self) -> Dict:
        """Perform a full scan of all relevant files"""
        logger.info("Performing full scan")
        
        all_files = []
        for root, dirs, files in os.walk(self.repo_path):
            # Skip hidden and build directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'dist', 'build']]
            
            for file in files:
                file_path = os.path.relpath(os.path.join(root, file), self.repo_path)
                if self._is_relevant_file(file_path):
                    all_files.append(file_path)
        
        logger.info(f"Found {len(all_files)} files to scan")
        
        # Generate ASTs for all files (placeholder - would be actual AST generation)
        ast_cache = {}
        for file_path in all_files:
            # This is where you'd generate actual ASTs
            ast_cache[file_path] = self._generate_ast_placeholder(file_path)
        
        # Save cache and update last scan SHA
        self.save_ast_cache(ast_cache)
        current_sha = self.get_current_commit_sha()
        if current_sha:
            self.set_last_scan_sha(current_sha)
        
        return {
            'ast_cache': ast_cache,
            'scan_type': 'full',
            'files_scanned': all_files
        }
    
    def _incremental_scan(self, changes: Dict) -> Dict:
        """Perform incremental scan on changed files only"""
        logger.info(f"Performing incremental scan on {len(changes['changed'])} changed files")
        
        # Load existing cache
        ast_cache = self.load_ast_cache()
        
        # Remove deleted files from cache
        for deleted_file in changes['deleted']:
            if deleted_file in ast_cache:
                del ast_cache[deleted_file]
                logger.debug(f"Removed {deleted_file} from cache")
        
        # Update ASTs for changed files
        for changed_file in changes['changed']:
            ast_cache[changed_file] = self._generate_ast_placeholder(changed_file)
            logger.debug(f"Updated AST for {changed_file}")
        
        # Save updated cache and update last scan SHA
        self.save_ast_cache(ast_cache)
        current_sha = self.get_current_commit_sha()
        if current_sha:
            self.set_last_scan_sha(current_sha)
        
        return {
            'ast_cache': ast_cache,
            'scan_type': 'incremental',
            'files_scanned': changes['changed']
        }
    
    def _generate_ast_placeholder(self, file_path: str) -> Dict:
        """Placeholder for actual AST generation"""
        # In real implementation, this would generate actual AST
        # For now, return a simple placeholder
        full_path = self.repo_path / file_path
        
        return {
            'file_path': file_path,
            'size': full_path.stat().st_size if full_path.exists() else 0,
            'hash': hashlib.md5(str(full_path).encode()).hexdigest(),
            # In real implementation: 'ast': actual_ast_data,
            # 'semantic_data': semantic_analysis_result,
            # 'embeddings': code_embeddings
        }
    
    def clear_cache(self):
        """Clear all cached data"""
        if self.cache_dir.exists():
            import shutil
            shutil.rmtree(self.cache_dir)
            logger.info("Cache cleared")