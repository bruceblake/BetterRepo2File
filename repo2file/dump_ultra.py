"""
Ultra-optimized repository consolidation with exact token counting,
semantic code analysis, and advanced features.
"""
import os
import sys
import json
import ast
import re
import time
import multiprocessing as mp
from typing import List, Set, Optional, Dict, Tuple, Any
from pathlib import Path
from dataclasses import dataclass, field
import fnmatch
import mimetypes
import pathspec
import tiktoken
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

# Import our custom modules
from token_manager import TokenManager, TokenBudget
from code_analyzer import CodeAnalyzer

# Configuration constants
DEFAULT_TOKEN_BUDGET = 500000
CACHE_DIR = Path.home() / '.repo2file_cache'
CACHE_EXPIRY_DAYS = 7

# Model configurations
MODEL_CONFIGS = {
    'gpt-4': {'encoding': 'cl100k_base', 'max_tokens': 128000},
    'gpt-3.5-turbo': {'encoding': 'cl100k_base', 'max_tokens': 16385},
    'claude-3': {'encoding': 'cl100k_base', 'max_tokens': 200000},
    'llama': {'encoding': 'cl100k_base', 'max_tokens': 32000},
    'gemini-1.5-pro': {'encoding': 'cl100k_base', 'max_tokens': 2000000},
}

# File type configurations
BINARY_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg', '.ico',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.exe', '.dll', '.so', '.dylib', '.app', '.deb', '.rpm',
    '.zip', '.tar', '.gz', '.bz2', '.xz', '.7z', '.rar',
    '.mp4', '.mp3', '.wav', '.avi', '.mov', '.mkv', '.flac',
    '.ttf', '.otf', '.woff', '.woff2', '.eot',
    '.pyc', '.pyo', '.class', '.o', '.obj', '.lib',
    '.db', '.sqlite', '.mdb', '.bin', '.dat',
    '.min.js', '.min.css',  # Minified files
}

AUTO_GENERATED_PATTERNS = [
    r'.*\.generated\.',
    r'.*\.auto\.',
    r'.*\.g\.',
    r'.*_pb2\.py$',  # Protocol buffers
    r'.*\.designer\.',  # Visual Studio designer files
    r'.*\.idea/',  # JetBrains IDEs
    r'.*\.vscode/',  # VS Code
    r'.*__pycache__/',  # Python cache
    r'.*node_modules/',  # Node modules
    r'.*\.next/',  # Next.js build
    r'.*\.nuxt/',  # Nuxt.js build
    r'.*build/',
    r'.*dist/',
    r'.*out/',
    r'.*target/',  # Java/Rust build
    r'.*\.egg-info/',  # Python packages
]

# Important files that should always be included if possible
CRITICAL_FILES = {
    'README.md', 'README.rst', 'README.txt', 'README',
    'setup.py', 'setup.cfg', 'pyproject.toml',
    'package.json', 'requirements.txt', 'Pipfile',
    'Cargo.toml', 'go.mod', 'build.gradle', 'pom.xml',
    'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
    '.env.example', 'config.example.json', 'settings.example.py',
    'Makefile', 'CMakeLists.txt', 'meson.build',
    '.gitignore', '.dockerignore',
}

# Files that should be summarized instead of full content
SUMMARIZE_FILES = {
    'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
    'poetry.lock', 'Pipfile.lock', 'Cargo.lock',
    'go.sum', 'composer.lock', 'Gemfile.lock',
    'pubspec.lock', 'mix.lock', '.terraform.lock.hcl',
}

class ManifestGenerator:
    """Generate hierarchical manifest for large contexts"""
    
    def __init__(self, token_manager: TokenManager, code_analyzer: CodeAnalyzer):
        self.token_manager = token_manager
        self.code_analyzer = code_analyzer
    
    def generate_manifest(self, files: List['FileInfo'], codebase_analysis: Dict, 
                         max_tokens: int = 5000) -> Tuple[str, Dict[str, int]]:
        """Generate a hierarchical manifest with navigation aids
        
        Returns:
            manifest_text: Markdown formatted manifest
            offset_map: Map of file paths to their token offset in the final output
        """
        manifest_lines = ["# Project Manifest", "", "## Table of Contents", ""]
        offset_map = {}
        
        # Group files by directory/module
        file_groups = self._group_files_by_directory(files)
        
        # Add overview section
        manifest_lines.extend([
            "### Project Overview",
            f"- **Type**: {codebase_analysis.get('project_type', 'Unknown')}",
            f"- **Primary Language**: {codebase_analysis.get('primary_language', 'Mixed')}",
            f"- **Key Frameworks**: {', '.join(codebase_analysis.get('frameworks', set()))}",
            f"- **Total Files**: {len(files)}",
            "",
            "### Navigation Guide",
            "",
            "Each section below contains:",
            "- Module/directory purpose (when detectable)",
            "- Key files with their main exports/classes",
            "- Estimated token location in the output",
            "",
            "---",
            ""
        ])
        
        # Process each module/directory
        for dir_path, dir_files in sorted(file_groups.items()):
            if not dir_files:
                continue
                
            # Add directory section
            dir_name = dir_path or "Root"
            manifest_lines.append(f"### {dir_name}")
            
            # Try to determine directory purpose
            purpose = self._determine_directory_purpose(dir_path, dir_files)
            if purpose:
                manifest_lines.append(f"*{purpose}*")
            
            manifest_lines.append("")
            
            # Sort files by importance
            dir_files.sort(key=lambda f: -f.importance_score)
            
            # Add key files
            for file in dir_files[:10]:  # Limit to top 10 files per directory
                rel_path = file.rel_path
                
                # Get file summary
                summary = self._get_file_summary(file)
                if summary:
                    manifest_lines.append(f"- **{rel_path}** - {summary}")
                else:
                    manifest_lines.append(f"- **{rel_path}**")
                
                # Add key exports/classes if available
                if file.semantic_data and 'ast_info' in file.semantic_data:
                    entities = []
                    for entity in file.semantic_data['ast_info'].get('entities', [])[:5]:
                        if entity['type'] in ['class', 'function', 'export']:
                            entities.append(f"`{entity['name']}`")
                    
                    if entities:
                        manifest_lines.append(f"  - Key items: {', '.join(entities)}")
                
                manifest_lines.append("")
            
            manifest_lines.append("")
        
        # Add token budget information
        manifest_lines.extend([
            "---",
            "",
            "## Processing Summary",
            "",
            f"- **Token Budget**: {self.token_manager.budget.total:,}",
            f"- **Tokens Used**: {self.token_manager.budget.used:,}",
            f"- **Utilization**: {self.token_manager.budget.used/self.token_manager.budget.total*100:.1f}%",
            "",
            "### File Selection Strategy",
            "",
            "Files were prioritized based on:",
            "1. Semantic importance (main files, configs, APIs)",
            "2. Code complexity and entity count",
            "3. File type and extension",
            "4. Size optimization for token budget",
            ""
        ])
        
        manifest_text = '\n'.join(manifest_lines)
        return manifest_text, offset_map
    
    def _group_files_by_directory(self, files: List['FileInfo']) -> Dict[str, List['FileInfo']]:
        """Group files by their parent directory"""
        groups = {}
        for file in files:
            parts = file.rel_path.split('/')
            dir_path = '/'.join(parts[:-1]) if len(parts) > 1 else ''
            
            if dir_path not in groups:
                groups[dir_path] = []
            groups[dir_path].append(file)
        
        return groups
    
    def _determine_directory_purpose(self, dir_path: str, files: List['FileInfo']) -> Optional[str]:
        """Try to determine the purpose of a directory based on its contents"""
        if not dir_path:
            return "Project root directory"
        
        dir_name = dir_path.split('/')[-1].lower()
        file_names = [f.path.name.lower() for f in files]
        
        # Common directory patterns
        patterns = {
            'components': 'UI Components',
            'pages': 'Application Pages/Routes',
            'views': 'View Templates',
            'models': 'Data Models',
            'controllers': 'Request Controllers',
            'services': 'Business Logic Services',
            'utils': 'Utility Functions',
            'helpers': 'Helper Functions',
            'config': 'Configuration Files',
            'api': 'API Endpoints',
            'routes': 'Route Definitions',
            'middleware': 'Middleware Functions',
            'tests': 'Test Files',
            'test': 'Test Files',
            'spec': 'Test Specifications',
            'docs': 'Documentation',
            'scripts': 'Build/Utility Scripts',
            'styles': 'Stylesheets',
            'css': 'Stylesheets',
            'assets': 'Static Assets',
            'static': 'Static Files',
            'public': 'Public Assets',
            'lib': 'Library Code',
            'vendor': 'Third-party Code',
            'migrations': 'Database Migrations',
            'fixtures': 'Test Data Fixtures',
        }
        
        # Check directory name
        for pattern, purpose in patterns.items():
            if pattern in dir_name:
                return purpose
        
        # Check file contents
        if any('test' in name or 'spec' in name for name in file_names):
            return 'Test Files'
        
        if any(name.endswith('.css') or name.endswith('.scss') for name in file_names):
            return 'Stylesheets'
        
        return None
    
    def _get_file_summary(self, file: 'FileInfo') -> Optional[str]:
        """Generate a brief summary of the file's purpose"""
        filename = file.path.name.lower()
        
        # Special files
        special_files = {
            'readme.md': 'Project documentation',
            'package.json': 'Node.js project configuration',
            'requirements.txt': 'Python dependencies',
            'setup.py': 'Python package setup',
            'dockerfile': 'Docker container configuration',
            'docker-compose.yml': 'Docker services configuration',
            '.gitignore': 'Git ignore patterns',
            'tsconfig.json': 'TypeScript configuration',
            'webpack.config.js': 'Webpack bundler configuration',
            'rollup.config.js': 'Rollup bundler configuration',
            'vite.config.js': 'Vite bundler configuration',
            '.eslintrc': 'ESLint configuration',
            '.prettierrc': 'Prettier configuration',
            'jest.config.js': 'Jest test configuration',
            'karma.conf.js': 'Karma test configuration',
            'babel.config.js': 'Babel transpiler configuration',
        }
        
        if filename in special_files:
            return special_files[filename]
        
        # Check file extension and content
        if file.semantic_data and 'ast_info' in file.semantic_data:
            ast_info = file.semantic_data['ast_info']
            entity_types = [e['type'] for e in ast_info.get('entities', [])]
            if 'class' in entity_types:
                main_class = next((e['name'] for e in ast_info['entities'] if e['type'] == 'class'), None)
                if main_class:
                    return f"Contains {main_class} class"
            
            if len(entity_types) > 3:
                unique_types = set(entity_types)
                return f"Contains {len(entity_types)} {'/'.join(unique_types)}"
        
        # File type based summary
        ext = file.path.suffix.lower()
        if ext == '.py':
            if 'main' in filename:
                return 'Main entry point'
            elif 'init' in filename:
                return 'Package initializer'
        elif ext in ['.js', '.ts']:
            if 'index' in filename:
                return 'Module entry point'
            elif 'main' in filename:
                return 'Main entry point'
        
        return None

@dataclass
class FileInfo:
    path: Path
    rel_path: str
    size: int
    is_binary: bool
    is_generated: bool
    is_critical: bool
    should_summarize: bool
    language: Optional[str] = None
    importance_score: float = 0.5
    content_hash: Optional[str] = None
    token_count: Optional[int] = None
    semantic_data: Optional[Dict] = None

@dataclass
class ProcessingProfile:
    """Configuration profile for processing"""
    name: str
    token_budget: int
    model: str
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    priority_boost: Dict[str, float] = field(default_factory=dict)
    max_file_size: int = 1_000_000  # 1MB
    min_importance_score: float = 0.0
    generate_manifest: bool = True  # Generate hierarchical manifest for large contexts
    truncation_strategy: str = 'semantic'  # semantic, basic, middle_summarize, business_logic
    
    def save(self, path: Path):
        with open(path, 'w') as f:
            json.dump(self.__dict__, f, indent=2)
    
    @classmethod
    def load(cls, path: Path) -> 'ProcessingProfile':
        with open(path, 'r') as f:
            data = json.load(f)
        return cls(**data)

class Cache:
    """File and token count caching system"""
    def __init__(self, cache_dir: Path = CACHE_DIR, profile_key: str = None):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.profile_key = profile_key or 'default'
        self.token_cache_file = self.cache_dir / f'token_cache_{self.profile_key}.json'
        self.file_cache_file = self.cache_dir / f'file_cache_{self.profile_key}.json'
        self.load_caches()
    
    def load_caches(self):
        try:
            with open(self.token_cache_file, 'r') as f:
                self.token_cache = json.load(f)
        except:
            self.token_cache = {}
        
        try:
            with open(self.file_cache_file, 'r') as f:
                self.file_cache = json.load(f)
        except:
            self.file_cache = {}
    
    def save_caches(self):
        with open(self.token_cache_file, 'w') as f:
            json.dump(self.token_cache, f)
        with open(self.file_cache_file, 'w') as f:
            json.dump(self.file_cache, f)
    
    def get_file_hash(self, file_path: Path, profile_hash: str = None) -> str:
        """Get hash of file content and processing parameters"""
        stat = file_path.stat()
        # Include file metadata
        file_hash = f"{stat.st_size}:{stat.st_mtime_ns}"
        
        # Include processing profile in hash if provided
        if profile_hash:
            return hashlib.sha256(f"{file_hash}:{profile_hash}".encode()).hexdigest()
        
        return file_hash
    
    def get_token_count(self, content_hash: str) -> Optional[int]:
        """Get cached token count for content hash"""
        return self.token_cache.get(content_hash)
    
    def set_token_count(self, content_hash: str, count: int):
        """Cache token count for content hash"""
        self.token_cache[content_hash] = count
    
    def get_file_info(self, file_path: Path, profile_hash: str = None) -> Optional[Dict]:
        """Get cached file info with expiration check"""
        cache_key = str(file_path)
        if cache_key in self.file_cache:
            info = self.file_cache[cache_key]
            
            # Check cache expiration
            cached_time = info.get('cached_at', 0)
            if time.time() - cached_time > (CACHE_EXPIRY_DAYS * 24 * 3600):
                del self.file_cache[cache_key]
                return None
            
            # Check if cache is still valid
            current_hash = self.get_file_hash(file_path, profile_hash)
            if info.get('hash') == current_hash:
                return info
            else:
                # Cache invalid, remove it
                del self.file_cache[cache_key]
        return None
    
    def set_file_info(self, file_path: Path, info: Dict, profile_hash: str = None):
        """Cache file info with profile awareness"""
        cache_key = str(file_path)
        info['hash'] = self.get_file_hash(file_path, profile_hash)
        info['cached_at'] = time.time()
        self.file_cache[cache_key] = info
        
        # Periodically clean old cache entries
        if len(self.file_cache) % 100 == 0:
            self.clean_expired_cache()
    
    def clean_expired_cache(self):
        """Remove expired cache entries"""
        current_time = time.time()
        expiry_time = CACHE_EXPIRY_DAYS * 24 * 3600
        
        # Clean token cache
        self.token_cache = {
            k: v for k, v in self.token_cache.items()
            if isinstance(v, dict) and current_time - v.get('cached_at', 0) < expiry_time
        }
        
        # Clean file cache
        self.file_cache = {
            k: v for k, v in self.file_cache.items()
            if current_time - v.get('cached_at', 0) < expiry_time
        }
        
        self.save_caches()

class UltraFileScanner:
    """Advanced file scanner with caching and parallel processing"""
    def __init__(self, cache: Cache, token_manager: TokenManager, code_analyzer: CodeAnalyzer, profile: ProcessingProfile = None):
        self.cache = cache
        self.token_manager = token_manager
        self.code_analyzer = code_analyzer
        self.profile = profile
        self.executor = ThreadPoolExecutor(max_workers=mp.cpu_count())
        # Create a profile hash for cache invalidation
        self.profile_hash = self._get_profile_hash() if profile else None
    
    def _get_profile_hash(self) -> str:
        """Generate a hash of the processing profile for cache invalidation"""
        if not self.profile:
            return None
        profile_str = f"{self.profile.model}:{self.profile.token_budget}:{self.profile.truncation_strategy}:{self.profile.min_importance_score}"
        return hashlib.sha256(profile_str.encode()).hexdigest()
    
    def scan_file(self, file_path: Path, base_path: Path) -> Optional[FileInfo]:
        """Scan a single file with caching"""
        try:
            # Check cache first with profile awareness
            cached_info = self.cache.get_file_info(file_path, self.profile_hash)
            if cached_info:
                return self._dict_to_fileinfo(cached_info, file_path, base_path)
            
            # Analyze file
            rel_path = file_path.relative_to(base_path)
            stat = file_path.stat()
            
            info = FileInfo(
                path=file_path,
                rel_path=str(rel_path),
                size=stat.st_size,
                is_binary=self._is_binary(file_path),
                is_generated=self._is_generated(str(rel_path)),
                is_critical=file_path.name in CRITICAL_FILES,
                should_summarize=file_path.name in SUMMARIZE_FILES,
            )
            
            # Skip binary files for content analysis
            if not info.is_binary and info.size < 10_000_000:  # 10MB limit
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                content_hash = hashlib.md5(content.encode()).hexdigest()
                info.content_hash = content_hash
                
                # Get token count from cache or calculate
                token_count = self.cache.get_token_count(content_hash)
                if token_count is None:
                    token_count = self.token_manager.count_tokens(content)
                    self.cache.set_token_count(content_hash, token_count)
                info.token_count = token_count
                
                # Semantic analysis for code files
                if self._is_code_file(file_path):
                    info.semantic_data = self.code_analyzer.analyze_file(file_path, content)
                    info.language = info.semantic_data.get('language')
                    info.importance_score = self.code_analyzer.calculate_file_importance(
                        info.semantic_data, file_path
                    )
            
            # Cache the result with profile awareness
            self.cache.set_file_info(file_path, self._fileinfo_to_dict(info), self.profile_hash)
            return info
            
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
            return None
    
    def scan_directory(self, directory: Path, exclusion_spec: pathspec.PathSpec,
                      progress_callback=None) -> List[FileInfo]:
        """Scan directory in parallel"""
        all_files = []
        futures = []
        
        for root, dirs, files in os.walk(directory, topdown=True):
            # Filter directories
            rel_root = Path(root).relative_to(directory)
            dirs[:] = [d for d in dirs if not exclusion_spec.match_file(str(rel_root / d))]
            
            for file_name in files:
                file_path = Path(root) / file_name
                rel_path = file_path.relative_to(directory)
                
                if not exclusion_spec.match_file(str(rel_path)):
                    future = self.executor.submit(self.scan_file, file_path, directory)
                    futures.append(future)
        
        # Collect results
        for i, future in enumerate(as_completed(futures)):
            result = future.result()
            if result:
                all_files.append(result)
            
            if progress_callback and i % 100 == 0:
                progress_callback(i, len(futures))
        
        return all_files
    
    def _is_binary(self, file_path: Path) -> bool:
        """Enhanced binary file detection"""
        # Check extension
        if file_path.suffix.lower() in BINARY_EXTENSIONS:
            return True
        
        # Check MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type:
            if not mime_type.startswith('text/') and mime_type != 'application/json':
                return True
        
        # Sample file content
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(8192)
                if b'\0' in chunk:
                    return True
                
                # Check for high percentage of non-printable characters
                text_chars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
                nontext = len([b for b in chunk if b not in text_chars])
                return nontext / len(chunk) > 0.30
        except:
            return True
    
    def _is_generated(self, rel_path: str) -> bool:
        """Check if file is auto-generated"""
        for pattern in AUTO_GENERATED_PATTERNS:
            if re.match(pattern, rel_path):
                return True
        return False
    
    def _is_code_file(self, file_path: Path) -> bool:
        """Check if file is a code file"""
        code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
            '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala', '.m',
            '.cs', '.vb', '.lua', '.pl', '.sh', '.r', '.jl', '.dart', '.ex'
        }
        return file_path.suffix.lower() in code_extensions
    
    def _fileinfo_to_dict(self, info: FileInfo) -> Dict:
        """Convert FileInfo to dictionary for caching"""
        return {
            'rel_path': info.rel_path,
            'size': info.size,
            'is_binary': info.is_binary,
            'is_generated': info.is_generated,
            'is_critical': info.is_critical,
            'should_summarize': info.should_summarize,
            'language': info.language,
            'importance_score': info.importance_score,
            'content_hash': info.content_hash,
            'token_count': info.token_count,
            'semantic_data': info.semantic_data,
        }
    
    def _dict_to_fileinfo(self, data: Dict, file_path: Path, base_path: Path) -> FileInfo:
        """Convert dictionary to FileInfo"""
        return FileInfo(
            path=file_path,
            rel_path=data['rel_path'],
            size=data['size'],
            is_binary=data['is_binary'],
            is_generated=data['is_generated'],
            is_critical=data['is_critical'],
            should_summarize=data['should_summarize'],
            language=data.get('language'),
            importance_score=data.get('importance_score', 0.5),
            content_hash=data.get('content_hash'),
            token_count=data.get('token_count'),
            semantic_data=data.get('semantic_data'),
        )

class ContentProcessor:
    """Advanced content processing with semantic understanding"""
    def __init__(self, token_manager: TokenManager, code_analyzer: CodeAnalyzer, profile: ProcessingProfile = None):
        self.token_manager = token_manager
        self.code_analyzer = code_analyzer
        self.profile = profile
    
    def process_file(self, file_info: FileInfo, token_budget: int) -> Tuple[str, int]:
        """Process file content with intelligent truncation"""
        try:
            content = file_info.path.read_text(encoding='utf-8', errors='ignore')
            
            # Handle special file types
            if file_info.should_summarize:
                return self._summarize_lockfile(content, file_info.path.name), 100
            
            # Get exact token count
            if file_info.token_count is None:
                file_info.token_count = self.token_manager.count_tokens(content)
            
            # If content fits within budget, return as is
            if file_info.token_count <= token_budget:
                return content, file_info.token_count
            
            # Smart truncation based on configured strategy
            strategy = self.profile.truncation_strategy if self.profile else 'semantic'
            
            if strategy == 'business_logic' and file_info.semantic_data:
                return self._business_logic_truncate(content, file_info, token_budget)
            elif strategy == 'middle_summarize':
                return self._middle_summarize_truncate(content, file_info, token_budget)
            elif strategy == 'semantic' and file_info.semantic_data:
                return self._semantic_truncate(content, file_info, token_budget)
            else:
                return self._basic_truncate(content, token_budget)
            
        except Exception as e:
            return f"[Error reading file: {e}]", 50
    
    def _semantic_truncate(self, content: str, file_info: FileInfo, token_budget: int) -> Tuple[str, int]:
        """Truncate content using semantic understanding"""
        entities = file_info.semantic_data.get('entities', [])
        if not entities:
            return self._basic_truncate(content, token_budget)
        
        # Sort entities by importance
        entities.sort(key=lambda e: e.importance_score, reverse=True)
        
        lines = content.splitlines()
        included_lines = set()
        current_tokens = 0
        
        # Always include imports/headers (first 20 lines typically)
        header_lines = min(20, len(lines))
        for i in range(header_lines):
            included_lines.add(i)
        
        header_content = '\n'.join(lines[:header_lines])
        current_tokens = self.token_manager.count_tokens(header_content)
        
        # Include important entities
        for entity in entities:
            if current_tokens >= token_budget * 0.9:
                break
            
            # Include entity definition and some context
            start = max(0, entity.line_start - 3)
            end = min(len(lines), entity.line_end + 3)
            
            entity_lines = set(range(start, end))
            new_lines = entity_lines - included_lines
            
            if new_lines:
                new_content = '\n'.join(lines[i] for i in sorted(new_lines))
                new_tokens = self.token_manager.count_tokens(new_content)
                
                if current_tokens + new_tokens <= token_budget:
                    included_lines.update(new_lines)
                    current_tokens += new_tokens
        
        # Build final content
        result_lines = []
        last_line = -1
        
        for line_num in sorted(included_lines):
            if line_num > last_line + 1:
                result_lines.append(f"\n... [Lines {last_line + 1}-{line_num - 1} omitted] ...\n")
            result_lines.append(lines[line_num])
            last_line = line_num
        
        if last_line < len(lines) - 1:
            result_lines.append(f"\n... [Lines {last_line + 1}-{len(lines) - 1} omitted] ...\n")
        
        final_content = '\n'.join(result_lines)
        return final_content, current_tokens
    
    def _basic_truncate(self, content: str, token_budget: int) -> Tuple[str, int]:
        """Basic truncation with token awareness"""
        lines = content.splitlines()
        
        # Include first and last portions
        total_lines = len(lines)
        head_lines = min(100, total_lines // 3)
        tail_lines = min(100, total_lines // 3)
        
        # Start with header
        result = lines[:head_lines]
        current_tokens = self.token_manager.count_tokens('\n'.join(result))
        
        # Add tail if budget allows
        tail_content = lines[-tail_lines:]
        tail_tokens = self.token_manager.count_tokens('\n'.join(tail_content))
        
        if current_tokens + tail_tokens + 50 <= token_budget:  # 50 tokens for truncation message
            result.append(f"\n... [{total_lines - head_lines - tail_lines} lines omitted] ...\n")
            result.extend(tail_content)
            current_tokens += tail_tokens + 50
        else:
            result.append(f"\n... [{total_lines - head_lines} lines omitted] ...\n")
            current_tokens += 50
        
        return '\n'.join(result), current_tokens
    
    def _middle_summarize_truncate(self, content: str, file_info: FileInfo, token_budget: int) -> Tuple[str, int]:
        """Advanced truncation that keeps beginning/end intact and summarizes middle"""
        lines = content.splitlines()
        
        if file_info.language not in ['python', 'javascript', 'typescript', 'java']:
            return self._basic_truncate(content, token_budget)
        
        # Calculate proportions
        total_lines = len(lines)
        header_ratio = 0.3  # 30% for header/imports
        footer_ratio = 0.2  # 20% for exports/main logic
        
        header_lines = int(total_lines * header_ratio)
        footer_lines = int(total_lines * footer_ratio)
        
        # Build header
        result = lines[:header_lines]
        current_tokens = self.token_manager.count_tokens('\n'.join(result))
        
        # Add footer if budget allows
        footer_content = lines[-footer_lines:]
        footer_tokens = self.token_manager.count_tokens('\n'.join(footer_content))
        
        if current_tokens + footer_tokens + 100 <= token_budget:
            # Add middle summary
            middle_start = header_lines
            middle_end = total_lines - footer_lines
            middle_summary = self._generate_middle_summary(
                lines[middle_start:middle_end], 
                file_info,
                (token_budget - current_tokens - footer_tokens - 100) // 2
            )
            
            result.append(f"\n... [Middle section summary] ...\n")
            result.append(middle_summary)
            result.append(f"\n... [Continuing to end] ...\n")
            result.extend(footer_content)
            
            current_tokens = self.token_manager.count_tokens('\n'.join(result))
        
        return '\n'.join(result), current_tokens
    
    def _generate_middle_summary(self, lines: List[str], file_info: FileInfo, max_tokens: int) -> str:
        """Generate a summary of the middle section of a file"""
        summary_parts = []
        
        # Extract key information from the middle section
        class_count = 0
        function_count = 0
        key_functions = []
        key_classes = []
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Language-specific pattern matching
            if file_info.language == 'python':
                if line_stripped.startswith('class '):
                    class_count += 1
                    class_name = line_stripped.split()[1].split('(')[0].strip(':')
                    key_classes.append(class_name)
                elif line_stripped.startswith('def '):
                    function_count += 1
                    func_name = line_stripped.split()[1].split('(')[0]
                    if not func_name.startswith('_'):  # Public functions
                        key_functions.append(func_name)
            
            elif file_info.language in ['javascript', 'typescript']:
                if 'class ' in line_stripped:
                    class_count += 1
                    parts = line_stripped.split('class ')
                    if len(parts) > 1:
                        class_name = parts[1].split()[0].strip('{')
                        key_classes.append(class_name)
                elif 'function ' in line_stripped or '=>' in line_stripped:
                    function_count += 1
                    if 'function ' in line_stripped:
                        parts = line_stripped.split('function ')
                        if len(parts) > 1:
                            func_name = parts[1].split('(')[0]
                            key_functions.append(func_name)
        
        # Build summary
        summary_parts.append(f"Middle section contains:")
        if class_count > 0:
            summary_parts.append(f"- {class_count} classes: {', '.join(key_classes[:5])}")
            if len(key_classes) > 5:
                summary_parts.append(f"  (and {len(key_classes) - 5} more)")
        
        if function_count > 0:
            summary_parts.append(f"- {function_count} functions: {', '.join(key_functions[:5])}")
            if len(key_functions) > 5:
                summary_parts.append(f"  (and {len(key_functions) - 5} more)")
        
        # Check for patterns
        has_tests = any('test' in line.lower() or 'spec' in line.lower() for line in lines)
        has_error_handling = any('try' in line or 'catch' in line or 'except' in line for line in lines)
        
        if has_tests:
            summary_parts.append("- Contains test cases")
        if has_error_handling:
            summary_parts.append("- Includes error handling")
        
        return '\n'.join(summary_parts)
    
    def _business_logic_truncate(self, content: str, file_info: FileInfo, token_budget: int) -> Tuple[str, int]:
        """Prioritize business logic over boilerplate"""
        if not file_info.semantic_data:
            return self._basic_truncate(content, token_budget)
        
        entities = file_info.semantic_data.get('entities', [])
        lines = content.splitlines()
        
        # Categorize entities
        imports = []
        business_logic = []
        utilities = []
        tests = []
        
        for entity in entities:
            entity_name = entity.name.lower()
            
            if entity.type == 'import':
                imports.append(entity)
            elif 'test' in entity_name or 'spec' in entity_name:
                tests.append(entity)
            elif any(util in entity_name for util in ['util', 'helper', 'format', 'parse', 'convert']):
                utilities.append(entity)
            else:
                business_logic.append(entity)
        
        # Build result prioritizing business logic
        included_lines = set()
        current_tokens = 0
        
        # Always include imports
        for entity in imports[:20]:  # Limit imports
            included_lines.update(range(entity.line_start, entity.line_end + 1))
        
        # Include business logic entities
        for entity in sorted(business_logic, key=lambda e: e.importance_score, reverse=True):
            if current_tokens >= token_budget * 0.8:
                break
            
            start = max(0, entity.line_start - 2)
            end = min(len(lines), entity.line_end + 2)
            
            new_lines = set(range(start, end))
            test_content = '\n'.join(lines[i] for i in new_lines if i not in included_lines)
            test_tokens = self.token_manager.count_tokens(test_content)
            
            if current_tokens + test_tokens <= token_budget * 0.9:
                included_lines.update(new_lines)
                current_tokens += test_tokens
        
        # Fill remaining space with utilities if any
        for entity in sorted(utilities, key=lambda e: e.importance_score, reverse=True):
            if current_tokens >= token_budget * 0.95:
                break
            
            start = max(0, entity.line_start - 1)
            end = min(len(lines), entity.line_end + 1)
            
            new_lines = set(range(start, end))
            test_content = '\n'.join(lines[i] for i in new_lines if i not in included_lines)
            test_tokens = self.token_manager.count_tokens(test_content)
            
            if current_tokens + test_tokens <= token_budget:
                included_lines.update(new_lines)
                current_tokens += test_tokens
        
        # Build final content
        result_lines = []
        last_line = -1
        
        for line_num in sorted(included_lines):
            if line_num > last_line + 1:
                result_lines.append(f"\n... [Lines {last_line + 1}-{line_num - 1} omitted] ...\n")
            result_lines.append(lines[line_num])
            last_line = line_num
        
        if last_line < len(lines) - 1:
            result_lines.append(f"\n... [Lines {last_line + 1}-{len(lines) - 1} omitted] ...\n")
        
        return '\n'.join(result_lines), current_tokens
    
    def _summarize_lockfile(self, content: str, filename: str) -> str:
        """Create a summary of lock files"""
        lines = content.splitlines()
        summary = [f"[LOCK FILE SUMMARY: {filename}]"]
        
        # Count dependencies based on file type
        if filename == 'package-lock.json':
            dep_count = content.count('"resolved":')
            summary.append(f"NPM packages: ~{dep_count}")
        elif filename == 'yarn.lock':
            dep_count = len([l for l in lines if l and not l.startswith(' ') and not l.startswith('#')])
            summary.append(f"Yarn packages: ~{dep_count}")
        elif filename == 'poetry.lock':
            dep_count = content.count('[[package]]')
            summary.append(f"Poetry packages: ~{dep_count}")
        elif filename == 'Cargo.lock':
            dep_count = content.count('[[package]]')
            summary.append(f"Rust crates: ~{dep_count}")
        else:
            dep_count = len([l for l in lines if l.strip() and not l.startswith('#')])
            summary.append(f"Dependencies: ~{dep_count}")
        
        summary.append(f"File size: {len(content):,} bytes")
        summary.append(f"Lines: {len(lines):,}")
        summary.append("[Full content omitted - lock file with dependency versions]")
        
        return '\n'.join(summary)

class CodebaseAnalyzer:
    """Analyze entire codebase structure and relationships"""
    def __init__(self, code_analyzer: CodeAnalyzer):
        self.code_analyzer = code_analyzer
    
    def analyze_codebase(self, files: List[FileInfo]) -> Dict:
        """Perform comprehensive codebase analysis"""
        analysis = {
            'total_files': len(files),
            'total_size': sum(f.size for f in files),
            'languages': {},
            'file_types': {},
            'primary_language': None,
            'frameworks': set(),
            'project_type': None,
            'dependency_graph': {},
            'key_files': [],
            'statistics': {}
        }
        
        # Language analysis
        for file in files:
            if file.language:
                analysis['languages'][file.language] = analysis['languages'].get(file.language, 0) + 1
            
            suffix = Path(file.path).suffix
            if suffix:
                analysis['file_types'][suffix] = analysis['file_types'].get(suffix, 0) + 1
        
        # Determine primary language
        if analysis['languages']:
            analysis['primary_language'] = max(analysis['languages'].items(), key=lambda x: x[1])[0]
        
        # Framework detection
        framework_files = {
            'package.json': ['Node.js', 'npm'],
            'yarn.lock': ['Yarn'],
            'requirements.txt': ['Python'],
            'setup.py': ['Python'],
            'pyproject.toml': ['Python', 'Poetry'],
            'Cargo.toml': ['Rust'],
            'go.mod': ['Go'],
            'build.gradle': ['Java', 'Gradle'],
            'pom.xml': ['Java', 'Maven'],
            'composer.json': ['PHP', 'Composer'],
            'Gemfile': ['Ruby', 'Bundler'],
            'angular.json': ['Angular'],
            'vue.config.js': ['Vue.js'],
            'next.config.js': ['Next.js'],
            'gatsby-config.js': ['Gatsby'],
            'svelte.config.js': ['Svelte'],
        }
        
        for file in files:
            for marker, frameworks in framework_files.items():
                if file.path.name == marker:
                    analysis['frameworks'].update(frameworks)
        
        # Determine project type
        analysis['project_type'] = self._determine_project_type(analysis)
        
        # Find key files (high importance score)
        key_files = sorted(files, key=lambda f: f.importance_score, reverse=True)[:20]
        analysis['key_files'] = [f.rel_path for f in key_files]
        
        # Statistics
        analysis['statistics'] = {
            'binary_files': sum(1 for f in files if f.is_binary),
            'generated_files': sum(1 for f in files if f.is_generated),
            'critical_files': sum(1 for f in files if f.is_critical),
            'total_tokens': sum(f.token_count or 0 for f in files),
            'avg_file_size': analysis['total_size'] / len(files) if files else 0,
        }
        
        return analysis
    
    def _determine_project_type(self, analysis: Dict) -> str:
        """Determine project type from analysis"""
        frameworks = analysis['frameworks']
        primary_lang = analysis['primary_language']
        
        if any(f in frameworks for f in ['Angular', 'React', 'Vue.js', 'Svelte']):
            return 'Frontend Web Application'
        elif 'Node.js' in frameworks and any(f in frameworks for f in ['Express', 'Fastify', 'Koa']):
            return 'Backend Web Application'
        elif primary_lang == 'Python' and any(f in frameworks for f in ['Django', 'Flask', 'FastAPI']):
            return 'Python Web Application'
        elif any(f in frameworks for f in ['React Native', 'Flutter', 'Ionic']):
            return 'Mobile Application'
        elif primary_lang:
            return f'{primary_lang} Project'
        else:
            return 'Software Project'

class UltraRepo2File:
    """Main class for ultra-optimized repository processing"""
    def __init__(self, profile: ProcessingProfile):
        self.profile = profile
        # Create a profile-specific cache key
        profile_key = f"{profile.model}_{profile.token_budget}_{profile.truncation_strategy}"
        self.cache = Cache(profile_key=profile_key)
        self.token_manager = TokenManager(model=profile.model, budget=profile.token_budget)
        self.code_analyzer = CodeAnalyzer()
        self.scanner = UltraFileScanner(self.cache, self.token_manager, self.code_analyzer, self.profile)
        self.processor = ContentProcessor(self.token_manager, self.code_analyzer, self.profile)
        self.codebase_analyzer = CodebaseAnalyzer(self.code_analyzer)
        self.manifest_generator = ManifestGenerator(self.token_manager, self.code_analyzer)
    
    def process_repository(self, repo_path: Path, output_path: Path):
        """Process repository with all optimizations"""
        start_time = time.time()
        
        print(f"Starting ultra-optimized processing...")
        print(f"Model: {self.profile.model}")
        print(f"Token Budget: {self.profile.token_budget:,}")
        print(f"Repository: {repo_path}")
        print()
        
        # Load exclusion patterns
        exclusion_spec = self._load_exclusions(repo_path)
        
        # Scan files with progress
        print("Scanning files...")
        def progress_callback(current, total):
            if current % 100 == 0:
                print(f"Scanned {current}/{total} files...")
        
        files = self.scanner.scan_directory(repo_path, exclusion_spec, progress_callback)
        print(f"Found {len(files)} files to process")
        
        # Filter and sort files
        files = self._filter_and_sort_files(files)
        print(f"After filtering: {len(files)} files")
        
        # Analyze codebase
        print("\nAnalyzing codebase structure...")
        codebase_analysis = self.codebase_analyzer.analyze_codebase(files)
        
        # Process files within token budget
        print("\nProcessing files...")
        output_parts = []
        
        # Add header
        header = self._generate_header(codebase_analysis, repo_path)
        header_tokens = self.token_manager.count_tokens(header)
        self.token_manager.budget.reserve('header', header_tokens)
        output_parts.append(header)
        
        # Generate manifest for large contexts (for Gemini 1.5 Pro)
        if self.profile.generate_manifest and (self.profile.model == 'gemini-1.5-pro' or self.profile.token_budget > 500000):
            print("\nGenerating hierarchical manifest...")
            manifest_text, offset_map = self.manifest_generator.generate_manifest(files, codebase_analysis)
            manifest_tokens = self.token_manager.count_tokens(manifest_text)
            
            if self.token_manager.budget.remaining >= manifest_tokens:
                self.token_manager.budget.reserve('manifest', manifest_tokens)
                output_parts.append(manifest_text)
            else:
                output_parts.append("[Manifest omitted due to token budget]")
        
        # Add directory structure
        tree_structure = self._generate_tree_structure(repo_path, exclusion_spec)
        tree_tokens = self.token_manager.count_tokens(tree_structure)
        
        if self.token_manager.budget.remaining >= tree_tokens:
            self.token_manager.budget.reserve('tree', tree_tokens)
            output_parts.append(tree_structure)
        else:
            output_parts.append("[Directory structure omitted due to token budget]")
        
        # Process individual files
        output_parts.append("\nFile Contents:\n" + "="*50 + "\n")
        
        processed_count = 0
        for i, file_info in enumerate(files):
            if self.token_manager.budget.remaining < 1000:  # Reserve some tokens for footer
                print(f"Token budget exhausted at file {i}/{len(files)}")
                break
            
            # Get remaining budget for this file
            remaining_budget = min(
                self.token_manager.budget.remaining - 1000,
                self.profile.max_file_size
            )
            
            # Process file
            content, tokens_used = self.processor.process_file(file_info, remaining_budget)
            
            if tokens_used > 0:
                file_header = f"\nFile: {file_info.rel_path}\n"
                file_header += f"Language: {file_info.language or 'Unknown'}\n"
                file_header += f"Size: {file_info.size:,} bytes | Tokens: {tokens_used:,}\n"
                file_header += "-" * 40 + "\n"
                
                file_output = file_header + content + "\n"
                file_tokens = self.token_manager.count_tokens(file_output)
                
                if self.token_manager.budget.remaining >= file_tokens:
                    output_parts.append(file_output)
                    self.token_manager.budget.allocate(file_info.rel_path, file_tokens, file_info.importance_score)
                    processed_count += 1
                    
                    if processed_count % 10 == 0:
                        print(f"Processed {processed_count} files...")
        
        # Add footer
        footer = self._generate_footer(codebase_analysis, processed_count, len(files))
        footer_tokens = self.token_manager.count_tokens(footer)
        
        if self.token_manager.budget.remaining >= footer_tokens:
            output_parts.append(footer)
        
        # Write output
        final_output = '\n'.join(output_parts)
        output_path.write_text(final_output, encoding='utf-8')
        
        # Save cache
        self.cache.save_caches()
        
        # Print summary
        elapsed_time = time.time() - start_time
        print(f"\nProcessing complete in {elapsed_time:.1f} seconds")
        print(f"Output written to: {output_path}")
        print(f"Files processed: {processed_count}/{len(files)}")
        print(f"Total tokens used: {self.token_manager.budget.used:,}/{self.token_manager.budget.total:,}")
        print(f"Token utilization: {self.token_manager.budget.used/self.token_manager.budget.total*100:.1f}%")
    
    def _load_exclusions(self, repo_path: Path) -> pathspec.PathSpec:
        """Load exclusion patterns from .gitignore and custom patterns"""
        patterns = []
        
        # Load .gitignore
        gitignore_path = repo_path / '.gitignore'
        if gitignore_path.exists():
            patterns.extend(gitignore_path.read_text().splitlines())
        
        # Add custom patterns from profile
        patterns.extend(self.profile.exclude_patterns)
        
        return pathspec.PathSpec.from_lines('gitwildmatch', patterns)
    
    def _filter_and_sort_files(self, files: List[FileInfo]) -> List[FileInfo]:
        """Filter and sort files based on profile settings"""
        # Filter out files below minimum importance
        files = [f for f in files if f.importance_score >= self.profile.min_importance_score]
        
        # Apply custom priority boosts
        for file in files:
            for pattern, boost in self.profile.priority_boost.items():
                if fnmatch.fnmatch(file.rel_path, pattern):
                    file.importance_score += boost
        
        # Sort by importance (descending) and size (ascending)
        files.sort(key=lambda f: (-f.importance_score, f.size))
        
        return files
    
    def _generate_header(self, analysis: Dict, repo_path: Path) -> str:
        """Generate informative header"""
        header = ["# Repository Analysis Report", "=" * 50, ""]
        header.append(f"Repository: {repo_path.name}")
        header.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        header.append(f"Processing Model: {self.profile.model}")
        header.append(f"Token Budget: {self.profile.token_budget:,}")
        header.append("")
        header.append("## Project Overview")
        header.append(f"Type: {analysis['project_type']}")
        header.append(f"Primary Language: {analysis['primary_language'] or 'Not determined'}")
        header.append(f"Total Files: {analysis['total_files']:,}")
        header.append(f"Total Size: {analysis['total_size']:,} bytes")
        
        if analysis['frameworks']:
            header.append(f"Frameworks: {', '.join(sorted(analysis['frameworks']))}")
        
        header.append("")
        header.append("## Key Files")
        for i, key_file in enumerate(analysis['key_files'][:10], 1):
            header.append(f"{i}. {key_file}")
        
        header.append("")
        header.append("## Processing Notes")
        header.append("- Files are processed by importance score")
        header.append("- Content is intelligently truncated to fit token budget")
        header.append("- Binary and auto-generated files are excluded")
        header.append("- Lock files are summarized")
        header.append("")
        
        return '\n'.join(header)
    
    def _generate_tree_structure(self, repo_path: Path, exclusion_spec: pathspec.PathSpec) -> str:
        """Generate directory tree structure"""
        tree_lines = ["## Directory Structure", "```"]
        
        def build_tree(path: Path, prefix: str = "", is_last: bool = True):
            if len(tree_lines) > 100:  # Limit tree size
                return
            
            # Skip if excluded
            rel_path = path.relative_to(repo_path) if path != repo_path else Path('.')
            if exclusion_spec.match_file(str(rel_path)):
                return
            
            # Add current item
            if path == repo_path:
                tree_lines.append(repo_path.name + '/')
            else:
                tree_lines.append(prefix + ('└── ' if is_last else '├── ') + path.name + ('/' if path.is_dir() else ''))
            
            # Process children if directory
            if path.is_dir():
                children = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
                visible_children = [c for c in children if not exclusion_spec.match_file(str(c.relative_to(repo_path)))]
                
                for i, child in enumerate(visible_children[:20]):  # Limit children
                    is_last_child = i == len(visible_children) - 1
                    next_prefix = prefix + ('    ' if is_last else '│   ')
                    build_tree(child, next_prefix, is_last_child)
        
        build_tree(repo_path)
        tree_lines.append("```")
        return '\n'.join(tree_lines) + '\n'
    
    def _generate_footer(self, analysis: Dict, processed: int, total: int) -> str:
        """Generate summary footer"""
        footer = ["\n" + "=" * 50]
        footer.append("## Processing Summary")
        footer.append(f"Files Processed: {processed:,} / {total:,}")
        footer.append(f"Token Usage: {self.token_manager.budget.used:,} / {self.token_manager.budget.total:,}")
        footer.append(f"Utilization: {self.token_manager.budget.used/self.token_manager.budget.total*100:.1f}%")
        footer.append("")
        footer.append("## File Type Distribution")
        
        for ext, count in sorted(analysis['file_types'].items(), key=lambda x: x[1], reverse=True)[:10]:
            footer.append(f"{ext}: {count} files")
        
        footer.append("")
        footer.append("## Language Distribution")
        
        for lang, count in sorted(analysis['languages'].items(), key=lambda x: x[1], reverse=True):
            footer.append(f"{lang}: {count} files")
        
        footer.append("")
        footer.append("Generated by UltraRepo2File")
        
        return '\n'.join(footer)

def main():
    """Main entry point"""
    if len(sys.argv) < 3:
        print("Usage: python dump_ultra.py <repo_path> <output_file> [profile_file] [options]")
        print("\nOptions:")
        print("  --model MODEL      LLM model to optimize for (default: gpt-4)")
        print("  --budget TOKENS    Token budget (default: 500000)")
        print("  --profile NAME     Use named profile")
        print("  --exclude PATTERN  Add exclusion pattern")
        print("  --boost PATTERN    Boost priority for files matching pattern")
        print("  --manifest         Generate hierarchical manifest")
        print("  --truncation MODE  Truncation strategy (semantic, basic, middle_summarize, business_logic)")
        print("\nExamples:")
        print("  python dump_ultra.py ./myrepo output.txt")
        print("  python dump_ultra.py ./myrepo output.txt --model claude-3 --budget 200000")
        print("  python dump_ultra.py ./myrepo output.txt --exclude '*.log' --boost '*.py:0.5'")
        sys.exit(1)
    
    repo_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    
    # Parse arguments
    profile = ProcessingProfile(
        name="default",
        token_budget=DEFAULT_TOKEN_BUDGET,
        model="gpt-4"
    )
    
    i = 3
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--model' and i + 1 < len(sys.argv):
            profile.model = sys.argv[i + 1]
            i += 2
        elif arg == '--budget' and i + 1 < len(sys.argv):
            profile.token_budget = int(sys.argv[i + 1])
            i += 2
        elif arg == '--exclude' and i + 1 < len(sys.argv):
            profile.exclude_patterns.append(sys.argv[i + 1])
            i += 2
        elif arg == '--boost' and i + 1 < len(sys.argv):
            pattern, boost = sys.argv[i + 1].split(':')
            profile.priority_boost[pattern] = float(boost)
            i += 2
        elif arg == '--profile' and i + 1 < len(sys.argv):
            profile_path = Path(sys.argv[i + 1])
            if profile_path.exists():
                profile = ProcessingProfile.load(profile_path)
            i += 2
        elif arg == '--manifest':
            profile.generate_manifest = True
            i += 1
        elif arg == '--truncation' and i + 1 < len(sys.argv):
            profile.truncation_strategy = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    # Process repository
    processor = UltraRepo2File(profile)
    processor.process_repository(repo_path, output_path)

if __name__ == '__main__':
    main()