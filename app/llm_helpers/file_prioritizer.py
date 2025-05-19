"""Adaptive file prioritization based on LLM task requirements."""
import os
from dataclasses import dataclass
from enum import IntEnum
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path


class PriorityLevel(IntEnum):
    """Priority levels for file inclusion."""
    CRITICAL = 1    # Must include (configs, main files)
    HIGH = 2        # Should include (core logic)
    MEDIUM = 3      # Include if space allows (supporting files)
    LOW = 4         # Include only if plenty of space
    MINIMAL = 5     # Skip unless specifically requested


@dataclass
class FileInfo:
    """Information about a file for prioritization."""
    path: str
    size: int
    type: str
    extension: str
    priority: PriorityLevel
    relevance_score: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class FilePrioritizer:
    """Prioritizes files based on task requirements and token budget."""
    
    # File patterns and their priorities
    PRIORITY_PATTERNS = {
        PriorityLevel.CRITICAL: [
            'main.py', '__main__.py', 'app.py', 'server.py',
            'config.py', 'settings.py', '.env', 'requirements.txt',
            'package.json', 'Cargo.toml', 'go.mod', 'pom.xml',
            'README.md', 'CONTRIBUTING.md', 'docker-compose.yml'
        ],
        PriorityLevel.HIGH: [
            '*.py', '*.js', '*.ts', '*.jsx', '*.tsx',
            '*.java', '*.cpp', '*.c', '*.h', '*.go',
            '*.rs', '*.swift', '*.kt', '*.scala',
            'Dockerfile', '*.yaml', '*.yml'
        ],
        PriorityLevel.MEDIUM: [
            '*.css', '*.scss', '*.sass', '*.html',
            '*.json', '*.xml', '*.toml', '*.ini',
            '*.sh', '*.bash', '*.zsh', '*.ps1',
            'Makefile', 'CMakeLists.txt'
        ],
        PriorityLevel.LOW: [
            '*.md', '*.txt', '*.rst', '*.adoc',
            '*.csv', '*.tsv', '*.log'
        ],
        PriorityLevel.MINIMAL: [
            '*.min.js', '*.min.css', '*.map',
            '*.lock', '*.sum', '.git/*', 'node_modules/*',
            '__pycache__/*', '*.pyc', '*.pyo', '*.pyd'
        ]
    }
    
    # Task-specific priority adjustments
    TASK_PRIORITIES = {
        'code_review': {
            '*.py': -1, '*.js': -1, '*.ts': -1,  # Increase priority
            '*.test.*': -1, '*.spec.*': -1,      # Include test files
            '*.md': 1, '*.txt': 2                # Lower priority
        },
        'documentation': {
            '*.md': -2, '*.rst': -2, '*.adoc': -2,  # Much higher priority
            'README*': -3, 'CONTRIBUTING*': -3,     # Critical for docs
            '*.py': 1, '*.js': 1                    # Lower code priority
        },
        'debugging': {
            '*.log': -2, '.env': -2, 'config*': -2,  # Higher priority
            '*.test.*': -1, '*.spec.*': -1,          # Include tests
            'traceback*': -3, 'error*': -3           # Error files critical
        },
        'refactoring': {
            '*.py': -1, '*.js': -1, '*.ts': -1,      # Code files priority
            'test*': -1, '*_test.*': -1,             # Include tests
            '*.md': 2, '*.txt': 2                    # Lower documentation
        },
        'security_audit': {
            '.env*': -3, 'config*': -3, 'settings*': -3,  # Critical
            '*.key': -3, '*.pem': -3, '*.crt': -3,        # Security files
            'requirements*.txt': -2, 'package*.json': -2,  # Dependencies
            '*.lock': -1                                   # Lock files
        }
    }
    
    def __init__(self):
        """Initialize the file prioritizer."""
        self.task_type = 'general'
        self.focus_patterns: List[str] = []
        self.exclude_patterns: List[str] = []
    
    def configure_for_task(
        self,
        task_type: str,
        focus_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None
    ) -> None:
        """Configure prioritizer for a specific task type."""
        self.task_type = task_type
        self.focus_patterns = focus_patterns or []
        self.exclude_patterns = exclude_patterns or []
    
    def prioritize_files(
        self,
        file_list: List[str],
        token_budget: int,
        estimated_tokens_per_file: Optional[Dict[str, int]] = None
    ) -> Tuple[List[FileInfo], List[FileInfo]]:
        """
        Prioritize files based on task requirements and token budget.
        
        Returns:
            Tuple of (included_files, excluded_files)
        """
        # Create FileInfo objects with priorities
        file_infos = []
        for file_path in file_list:
            if self._should_exclude(file_path):
                continue
                
            file_info = self._create_file_info(file_path)
            file_info.priority = self._calculate_priority(file_path)
            file_info.relevance_score = self._calculate_relevance(file_path)
            file_infos.append(file_info)
        
        # Sort by priority and relevance
        file_infos.sort(key=lambda f: (f.priority, -f.relevance_score))
        
        # Select files within token budget
        included_files = []
        excluded_files = []
        total_tokens = 0
        
        for file_info in file_infos:
            if estimated_tokens_per_file:
                file_tokens = estimated_tokens_per_file.get(
                    file_info.path,
                    self._estimate_tokens(file_info)
                )
            else:
                file_tokens = self._estimate_tokens(file_info)
            
            if total_tokens + file_tokens <= token_budget:
                included_files.append(file_info)
                total_tokens += file_tokens
            else:
                excluded_files.append(file_info)
        
        return included_files, excluded_files
    
    def _create_file_info(self, file_path: str) -> FileInfo:
        """Create FileInfo object for a file."""
        path = Path(file_path)
        
        return FileInfo(
            path=file_path,
            size=self._get_file_size(file_path),
            type=self._determine_file_type(file_path),
            extension=path.suffix,
            priority=PriorityLevel.MEDIUM,  # Default
            metadata={
                'is_test': self._is_test_file(file_path),
                'is_config': self._is_config_file(file_path),
                'is_documentation': self._is_doc_file(file_path)
            }
        )
    
    def _calculate_priority(self, file_path: str) -> PriorityLevel:
        """Calculate file priority based on patterns and task type."""
        path = Path(file_path)
        filename = path.name
        
        # Check for exact matches first
        for priority_level, patterns in self.PRIORITY_PATTERNS.items():
            if filename in patterns:
                return self._adjust_for_task(priority_level, file_path)
        
        # Check pattern matches
        for priority_level, patterns in self.PRIORITY_PATTERNS.items():
            for pattern in patterns:
                if self._matches_pattern(file_path, pattern):
                    return self._adjust_for_task(priority_level, file_path)
        
        # Default priority
        return PriorityLevel.MEDIUM
    
    def _adjust_for_task(
        self,
        base_priority: PriorityLevel,
        file_path: str
    ) -> PriorityLevel:
        """Adjust priority based on task type."""
        if self.task_type not in self.TASK_PRIORITIES:
            return base_priority
        
        adjustments = self.TASK_PRIORITIES[self.task_type]
        path = Path(file_path)
        
        # Check for pattern-specific adjustments
        for pattern, adjustment in adjustments.items():
            if self._matches_pattern(file_path, pattern):
                new_priority = base_priority + adjustment
                # Ensure priority stays within bounds
                new_priority = max(
                    PriorityLevel.CRITICAL,
                    min(PriorityLevel.MINIMAL, new_priority)
                )
                return PriorityLevel(new_priority)
        
        return base_priority
    
    def _calculate_relevance(self, file_path: str) -> float:
        """Calculate relevance score for a file (0.0 to 1.0)."""
        score = 0.5  # Base score
        
        # Boost for focus patterns
        for pattern in self.focus_patterns:
            if pattern.lower() in file_path.lower():
                score += 0.2
        
        # Special relevance for task types
        metadata = self._create_file_info(file_path).metadata
        
        if self.task_type == 'debugging' and metadata.get('is_test'):
            score += 0.3
        elif self.task_type == 'documentation' and metadata.get('is_documentation'):
            score += 0.4
        elif self.task_type == 'security_audit' and metadata.get('is_config'):
            score += 0.3
        
        # Cap at 1.0
        return min(score, 1.0)
    
    def _should_exclude(self, file_path: str) -> bool:
        """Check if file should be excluded."""
        for pattern in self.exclude_patterns:
            if self._matches_pattern(file_path, pattern):
                return True
        
        # Also check minimal priority patterns
        for pattern in self.PRIORITY_PATTERNS[PriorityLevel.MINIMAL]:
            if self._matches_pattern(file_path, pattern):
                return True
        
        return False
    
    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if file path matches a pattern."""
        from fnmatch import fnmatch
        return fnmatch(file_path, pattern) or fnmatch(Path(file_path).name, pattern)
    
    def _get_file_size(self, file_path: str) -> int:
        """Get file size in bytes."""
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0
    
    def _estimate_tokens(self, file_info: FileInfo) -> int:
        """Estimate tokens for a file based on size and type."""
        # Rough estimation: 1 token per 4 bytes for code
        base_tokens = file_info.size // 4
        
        # Adjust based on file type
        if file_info.extension in ['.json', '.xml', '.yaml', '.yml']:
            # These tend to be more verbose
            return base_tokens * 1.5
        elif file_info.extension in ['.md', '.txt', '.rst']:
            # Natural language is more token-efficient
            return base_tokens * 0.8
        elif file_info.extension in ['.min.js', '.min.css']:
            # Minified files are denser
            return base_tokens * 2
        
        return base_tokens
    
    def _determine_file_type(self, file_path: str) -> str:
        """Determine general file type."""
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs']:
            return 'code'
        elif ext in ['.md', '.txt', '.rst', '.adoc']:
            return 'documentation'
        elif ext in ['.json', '.xml', '.yaml', '.yml', '.toml', '.ini']:
            return 'config'
        elif ext in ['.css', '.scss', '.sass', '.html']:
            return 'style'
        elif ext in ['.test.js', '.spec.ts', '_test.py', '_test.go']:
            return 'test'
        else:
            return 'other'
    
    def _is_test_file(self, file_path: str) -> bool:
        """Check if file is a test file."""
        path = Path(file_path)
        name = path.name.lower()
        return (
            'test' in name or
            'spec' in name or
            name.startswith('test_') or
            name.endswith('_test') or
            '/tests/' in file_path or
            '/test/' in file_path
        )
    
    def _is_config_file(self, file_path: str) -> bool:
        """Check if file is a configuration file."""
        path = Path(file_path)
        name = path.name.lower()
        ext = path.suffix.lower()
        
        return (
            'config' in name or
            'settings' in name or
            ext in ['.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.env']
        )
    
    def _is_doc_file(self, file_path: str) -> bool:
        """Check if file is documentation."""
        path = Path(file_path)
        ext = path.suffix.lower()
        name = path.name.upper()
        
        return (
            ext in ['.md', '.rst', '.txt', '.adoc'] or
            name in ['README', 'CHANGELOG', 'LICENSE', 'CONTRIBUTING']
        )