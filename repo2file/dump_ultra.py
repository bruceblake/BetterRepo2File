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
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    print("Warning: tiktoken not available. Using character-based token estimation.", file=sys.stderr)
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

# Import our custom modules
from .token_manager import TokenManager, TokenBudget
from .code_analyzer import CodeAnalyzer
from .git_analyzer import GitAnalyzer
from .llm_augmenter import LLMAugmenter
from .action_blocks import (
    ActionBlockGenerator, CallGraphNode, GitInsight, 
    TodoItem, PCANote, CodeQualityMetric
)

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
    
    def __init__(self, token_manager: TokenManager, code_analyzer: CodeAnalyzer, 
                 action_block_generator = None):
        self.token_manager = token_manager
        self.code_analyzer = code_analyzer
        self.action_block_generator = action_block_generator
    
    def generate_manifest(self, files: List['FileInfo'], codebase_analysis: Dict, 
                         max_tokens: int = 5000, file_offset_map: Dict[str, int] = None) -> Tuple[str, Dict[str, int]]:
        """Generate a hierarchical manifest with navigation aids
        
        Args:
            files: List of FileInfo objects
            codebase_analysis: Analysis results
            max_tokens: Maximum tokens for manifest
            file_offset_map: Map of file paths to their token offsets in the output
                           
        Returns:
            manifest_text: Markdown formatted manifest
            offset_map: Map of file paths to their token offset in the final output
        """
        manifest_lines = ["# Project Manifest", "", "## Table of Contents", ""]
        offset_map = file_offset_map if file_offset_map else {}
        
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
            
            # Sort files by importance (including query relevance if available)
            dir_files.sort(key=lambda f: -f.importance_score)
            
            # Add key files
            for file in dir_files[:10]:  # Limit to top 10 files per directory
                rel_path = file.rel_path
                
                # Get file summary
                summary = self._get_file_summary(file)
                
                # Add query relevance indicator if DQCG is active
                query_indicator = ""
                if hasattr(file, 'query_relevance_score') and file.query_relevance_score > 0.3:
                    query_indicator = " 🎯"  # Target emoji to indicate query relevance
                
                # Add token location if available
                token_location = ""
                if rel_path in offset_map:
                    token_location = f" (Token offset: {offset_map[rel_path]:,})"
                
                if summary:
                    manifest_lines.append(f"- **{rel_path}** - {summary}{query_indicator}{token_location}")
                else:
                    manifest_lines.append(f"- **{rel_path}**{query_indicator}{token_location}")
                
                # Add key exports/classes if available
                if file.semantic_data and 'entities' in file.semantic_data:
                    key_entities = []
                    for entity in file.semantic_data['entities'][:5]:
                        entity_type = entity['type'] if isinstance(entity, dict) else entity.type
                        entity_name = entity['name'] if isinstance(entity, dict) else entity.name
                        if entity_type in ['class', 'function', 'method']:
                            key_entities.append(f"`{entity_name}`")
                    
                    if key_entities:
                        manifest_lines.append(f"  - Key items: {', '.join(key_entities)}")
                    
                    # Add call graph information for important entities
                    for entity in file.semantic_data['entities'][:3]:  # Show top 3
                        entity_type = entity['type'] if isinstance(entity, dict) else entity.type
                        entity_name = entity['name'] if isinstance(entity, dict) else entity.name
                        entity_calls = entity.get('calls', []) if isinstance(entity, dict) else entity.calls
                        entity_called_by = entity.get('called_by', []) if isinstance(entity, dict) else entity.called_by
                        if entity_type in ['function', 'method'] and (entity_calls or entity_called_by):
                            manifest_lines.append(f"  - `{entity_name}`:")
                            if entity_calls:
                                # Only show calls that are also in our output context
                                relevant_calls = [call for call in entity_calls[:5]]  # Limit to 5
                                if relevant_calls:
                                    manifest_lines.append(f"    - Calls: {', '.join(relevant_calls)}")
                            if entity_called_by:
                                # Only show callers that are also in our output context
                                relevant_callers = [caller for caller in entity_called_by[:5]]  # Limit to 5
                                if relevant_callers:
                                    manifest_lines.append(f"    - Called by: {', '.join(relevant_callers)}")
                
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
        ])
        
        # Add query information if available
        if hasattr(self, 'processing_query') and self.processing_query:
            manifest_lines.extend([
                "### Query-Aware Context Generation",
                "",
                f"Files were prioritized for the query: \"{self.processing_query}\"",
                "🎯 indicates files with high query relevance",
                "",
            ])
        
        manifest_lines.extend([
            "### File Selection Strategy",
            "",
            "Files were prioritized based on:",
            "1. Semantic importance (main files, configs, APIs)",
            "2. Code complexity and entity count",
            "3. File type and extension",
            "4. Size optimization for token budget",
        ])
        
        # Add query prioritization if active
        if hasattr(self, 'processing_query') and self.processing_query:
            manifest_lines.append("5. Query relevance (DQCG active)")
        
        manifest_lines.append("")
        
        # Add AI Action Blocks section if configured
        if (self.action_block_generator and 
            self.action_block_generator.format in ['manifest', 'both']):
            action_blocks_section = self.action_block_generator.generate_manifest_section()
            if action_blocks_section:
                manifest_lines.extend([
                    "---",
                    "",
                    "## AI Action Blocks Summary",
                    "",
                    action_blocks_section
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
    query_relevance_score: float = 0.0

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
    intended_query: str = ''  # Optional intended LLM query for context-aware prioritization
    vibe_statement: str = ''  # User's high-level goal/vibe for Gemini Planner Primer  
    planner_output: str = ''  # AI planner's output to integrate into Claude Coder context
    enable_git_insights: bool = False  # Include git history insights in output
    enable_llm_summarization: bool = False  # Use LLM to summarize long/complex files
    enable_llm_proactive_augmentation: bool = False  # Use LLM for proactive code analysis
    llm_augmentation_model: str = 'gemini-1.5-flash'  # LLM model for augmentation
    llm_augmentation_api_key_env_var: str = 'GEMINI_API_KEY'  # Environment variable for API key
    max_tokens_per_summary: int = 150  # Max tokens for each summary
    max_tokens_per_augmentation_chunk: int = 400  # Max tokens for PCA per chunk
    # AI Action Block options
    enable_action_blocks: bool = True
    action_block_format: str = 'both'  # 'inline', 'manifest', or 'both'
    action_block_types: List[str] = field(default_factory=lambda: [
        'CALL_GRAPH_NODE', 'GIT_INSIGHT', 'TODO_ITEM', 
        'PCA_NOTE', 'CODE_QUALITY_METRIC'
    ])
    action_block_filters: Dict[str, Any] = field(default_factory=lambda: {
        'min_complexity': 10,
        'min_priority': 'medium',
        'include_private_methods': False
    })
    auto_create_ai_guardrails_file: bool = True  # Auto-create ai_guardrails.md if missing
    
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
                    # Add query relevance if query is provided
                    if hasattr(self.profile, 'intended_query') and self.profile.intended_query:
                        query_relevance = self.code_analyzer.calculate_query_relevance(
                            self.profile.intended_query, file_path, content, info.semantic_data
                        )
                        # Combine importance score with query relevance
                        # Query relevance can boost score by up to 50%
                        info.query_relevance_score = query_relevance
                        info.importance_score = min(1.0, info.importance_score + query_relevance * 0.5)
            
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
    
    def _serialize_semantic_data(self, semantic_data: Dict) -> Dict:
        """Convert semantic data to JSON-serializable format"""
        if not semantic_data:
            return None
        
        serialized = {}
        for key, value in semantic_data.items():
            if key == 'entities' and isinstance(value, list):
                # Convert CodeEntity objects to dictionaries
                serialized[key] = []
                for entity in value:
                    if hasattr(entity, '__dict__'):
                        entity_dict = entity.__dict__.copy()
                        # Convert set to list for JSON serialization
                        if 'dependencies' in entity_dict and isinstance(entity_dict['dependencies'], set):
                            entity_dict['dependencies'] = list(entity_dict['dependencies'])
                        serialized[key].append(entity_dict)
                    else:
                        serialized[key].append(entity)
            else:
                serialized[key] = value
        
        return serialized
    
    def _fileinfo_to_dict(self, info: FileInfo) -> Dict:
        """Convert FileInfo to dictionary for caching"""
        # Convert semantic_data to JSON-serializable format
        semantic_data = None
        if info.semantic_data:
            semantic_data = self._serialize_semantic_data(info.semantic_data)
        
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
            'semantic_data': semantic_data,
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
    def __init__(self, token_manager: TokenManager, code_analyzer: CodeAnalyzer, 
                 profile: ProcessingProfile = None, git_analyzer = None, llm_augmenter = None,
                 action_block_generator = None):
        self.token_manager = token_manager
        self.code_analyzer = code_analyzer
        self.profile = profile
        self.git_analyzer = git_analyzer
        self.llm_augmenter = llm_augmenter
        self.action_block_generator = action_block_generator
    
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
            
            # Extract TODOs and generate action blocks
            if self.action_block_generator:
                todos = self._extract_todos(content, str(file_info.rel_path))
                for todo in todos:
                    self.action_block_generator.add_block(todo)
                
                # Generate Call Graph action blocks from semantic data
                if file_info.semantic_data and 'entities' in file_info.semantic_data:
                    for entity in file_info.semantic_data['entities']:
                        if hasattr(entity, 'calls') and hasattr(entity, 'called_by'):
                            call_node = CallGraphNode(
                                file=str(file_info.rel_path),
                                entity=entity.name,
                                entity_type=entity.type,
                                calls=entity.calls or [],
                                called_by=entity.called_by or []
                            )
                            self.action_block_generator.add_block(call_node)
            
            # Add git insights if enabled
            output_content = []
            git_header = ""
            
            if self.profile and self.profile.enable_git_insights and self.git_analyzer:
                git_info = self.git_analyzer.get_last_modified_info(str(file_info.rel_path))
                if git_info and any(git_info.values()):
                    change_freq = self.git_analyzer.get_change_frequency(str(file_info.rel_path))
                    contributors = self.git_analyzer.get_recent_contributors(str(file_info.rel_path))
                    
                    git_header = f"""# Git Insights for {file_info.rel_path}
# Last Modified: {git_info.get('date', 'Unknown')} by {git_info.get('author', 'Unknown')}
# Commit: {git_info.get('commit_message', 'Unknown')} ({git_info.get('commit_hash', 'Unknown')})
# Change Frequency (90d): {change_freq} commits
# Recent Contributors: {', '.join(contributors) if contributors else 'Unknown'}
# {'=' * 50}
"""
                    output_content.append(git_header)
                    
                    # Generate Git insight action block
                    if self.action_block_generator:
                        git_block = GitInsight(
                            file=str(file_info.rel_path),
                            last_mod_date=git_info.get('date', 'Unknown'),
                            last_mod_author=git_info.get('author', 'Unknown'),
                            last_commit=git_info.get('commit_message', 'Unknown'),
                            commit_hash=git_info.get('commit_hash', 'Unknown')[:7],  # Short hash
                            change_frequency_90d=change_freq,
                            recent_contributors=contributors if contributors else []
                        )
                        self.action_block_generator.add_block(git_block)
            
            # If content fits within budget, return as is
            adjusted_budget = token_budget - self.token_manager.count_tokens(git_header)
            if file_info.token_count <= adjusted_budget:
                output_content.append(content)
                return '\n'.join(output_content), file_info.token_count + len(git_header.split())
            
            # Check if LLM summarization is enabled for long/complex files
            if (self.profile and self.profile.enable_llm_summarization and 
                self.llm_augmenter and self.llm_augmenter.is_available()):
                
                # Criteria for LLM summarization
                should_summarize = (
                    file_info.token_count > token_budget * 2 or  # File is much larger than budget
                    (file_info.semantic_data and 
                     file_info.semantic_data.get('metrics', {}).get('complexity_score', 0) > 0.3)
                )
                
                if should_summarize:
                    summary = self.llm_augmenter.summarize_code_chunk(
                        content,
                        task_context=f"Summarize this {file_info.language or 'code'} file for understanding its purpose and structure",
                        max_summary_tokens=self.profile.max_tokens_per_summary
                    )
                    
                    if summary:
                        summary_header = f"\n[LLM-Generated Summary]\n{summary}\n{'=' * 50}\n"
                        output_content.append(summary_header)
                        adjusted_budget -= self.token_manager.count_tokens(summary_header)
            
            # Smart truncation based on configured strategy
            strategy = self.profile.truncation_strategy if self.profile else 'semantic'
            
            # Apply truncation with remaining budget
            truncated_content, tokens = self._apply_truncation_strategy(
                content, file_info, adjusted_budget, strategy
            )
            output_content.append(truncated_content)
            
            # Add LLM augmentation notes if enabled
            if (self.profile and self.profile.enable_llm_proactive_augmentation and
                self.llm_augmenter and self.llm_augmenter.is_available()):
                
                augmentation_notes = self._generate_augmentation_notes(
                    truncated_content, file_info
                )
                if augmentation_notes:
                    output_content.append(augmentation_notes)
            
            # Add function/method anchors for easier navigation  
            if file_info.semantic_data and 'entities' in file_info.semantic_data:
                # Find where the actual content is in output_content
                for i, part in enumerate(output_content):
                    if part == truncated_content:
                        enriched_content = self._add_entity_anchors(truncated_content, file_info.semantic_data['entities'])
                        output_content[i] = enriched_content  # Replace the content with anchored version
                        break
            
            return '\n'.join(output_content), sum(self.token_manager.count_tokens(part) for part in output_content)
        except Exception as e:
            return f"[Error reading file: {e}]", 50
    
    def _add_entity_anchors(self, content: str, entities: List) -> str:
        """Add textual anchors for functions/methods/classes"""
        lines = content.splitlines()
        anchored_lines = []
        line_index = 0
        
        # Sort entities by line number
        sorted_entities = sorted(entities, key=lambda e: e.line_start if hasattr(e, 'line_start') else 0)
        
        for entity in sorted_entities:
            if not hasattr(entity, 'line_start'):
                continue
                
            # Add lines before the entity
            while line_index < entity.line_start - 1 and line_index < len(lines):
                anchored_lines.append(lines[line_index])
                line_index += 1
            
            # Add anchor for the entity
            if hasattr(entity, 'name') and entity.name:
                anchor_type = "FUNCTION" if entity.type == 'function' else "METHOD" if entity.type == 'method' else "CLASS"
                anchored_lines.append(f"[[{anchor_type}_START: {entity.name}]]")
            
            # Add the entity lines
            while line_index < entity.line_end and line_index < len(lines):
                anchored_lines.append(lines[line_index])
                line_index += 1
                
            # Add end anchor
            if hasattr(entity, 'name') and entity.name:
                anchored_lines.append(f"[[{anchor_type}_END: {entity.name}]]")
        
        # Add remaining lines
        while line_index < len(lines):
            anchored_lines.append(lines[line_index])
            line_index += 1
        
        return '\n'.join(anchored_lines)
    
    def _extract_todos(self, content: str, file_path: str) -> List[TodoItem]:
        """Extract TODO, FIXME, HACK, and NOTE comments from content"""
        todos = []
        lines = content.splitlines()
        
        # Pattern to match TODO-like comments
        pattern = r'(?:#|//|/\*|\*)\s*(TODO|FIXME|HACK|NOTE)[:\s]+(.*?)(?:\*/)?$'
        
        for i, line in enumerate(lines):
            match = re.search(pattern, line.strip(), re.IGNORECASE)
            if match:
                todo_type = match.group(1).upper()
                text = match.group(2).strip()
                
                # Determine priority based on type and content
                priority = 'medium'
                if todo_type in ['FIXME', 'HACK']:
                    priority = 'high'
                elif any(word in text.lower() for word in ['critical', 'urgent', 'security', 'vulnerability']):
                    priority = 'high'
                elif any(word in text.lower() for word in ['minor', 'cleanup', 'refactor']):
                    priority = 'low'
                
                todos.append(TodoItem(
                    file=file_path,
                    line=i + 1,
                    todo_type=todo_type,
                    text=text,
                    priority=priority
                ))
        
        return todos
    
    def _apply_truncation_strategy(self, content: str, file_info: FileInfo, 
                                  token_budget: int, strategy: str) -> Tuple[str, int]:
        """Apply the specified truncation strategy"""
        if strategy == 'business_logic' and file_info.semantic_data:
            return self._business_logic_truncate(content, file_info, token_budget)
        elif strategy == 'middle_summarize':
            return self._middle_summarize_truncate(content, file_info, token_budget)
        elif strategy == 'semantic' and file_info.semantic_data:
            return self._semantic_truncate(content, file_info, token_budget)
        else:
            return self._basic_truncate(content, token_budget)
    
    def _generate_augmentation_notes(self, content: str, file_info: FileInfo) -> str:
        """Generate AI augmentation notes for critical code sections"""
        if not self.llm_augmenter or not self.llm_augmenter.is_available():
            return ""
        
        notes = []
        
        # Identify critical sections for augmentation
        critical_sections = self._identify_critical_sections(content, file_info)
        
        for section in critical_sections[:3]:  # Limit to top 3 sections
            # Get section content
            lines = content.splitlines()
            section_content = '\n'.join(lines[section['start']:section['end']])
            
            # Generate different types of augmentation
            if section['reason'] == 'high_complexity':
                ambiguities = self.llm_augmenter.identify_potential_ambiguities(
                    section_content,
                    task_context=f"Analyzing complex {file_info.language or 'code'} code section"
                )
                if ambiguities:
                    notes.append(f"\n--- AI Augmentation Notes ---")
                    notes.append(f"Section: lines {section['start']+1}-{section['end']+1}")
                    notes.append("Potential Ambiguities:")
                    for amb in ambiguities:
                        notes.append(f"  - {amb}")
            
            elif section['reason'] == 'query_relevant':
                assumptions = self.llm_augmenter.infer_implicit_assumptions(
                    section_content,
                    task_context=f"Analyzing query-relevant code for: {self.profile.intended_query}"
                )
                if assumptions:
                    notes.append(f"\n--- AI Augmentation Notes ---")
                    notes.append(f"Section: lines {section['start']+1}-{section['end']+1}")
                    notes.append("Implicit Assumptions:")
                    for assum in assumptions:
                        notes.append(f"  - {assum}")
            
            elif section['reason'] == 'high_change_frequency':
                questions = self.llm_augmenter.suggest_clarifying_questions(
                    section_content,
                    task_context="For modifying frequently changed code"
                )
                if questions:
                    notes.append(f"\n--- AI Augmentation Notes ---")
                    notes.append(f"Section: lines {section['start']+1}-{section['end']+1}")
                    notes.append("Clarifying Questions for Modification:")
                    for question in questions:
                        notes.append(f"  - {question}")
        
        if notes:
            notes.append("--- End AI Augmentation ---\n")
            return '\n'.join(notes)
        
        return ""
    
    def _identify_critical_sections(self, content: str, file_info: FileInfo) -> List[Dict]:
        """Identify critical code sections for AI augmentation"""
        sections = []
        lines = content.splitlines()
        
        # Use semantic data if available
        if file_info.semantic_data and 'entities' in file_info.semantic_data:
            for entity in file_info.semantic_data['entities']:
                # High complexity entities
                if hasattr(entity, 'complexity_score') and entity.complexity_score > 10:
                    sections.append({
                        'start': entity.line_start - 1,
                        'end': entity.line_end,
                        'reason': 'high_complexity',
                        'score': entity.complexity_score
                    })
                
                # Query-relevant entities (if query is provided)
                if self.profile.intended_query and hasattr(entity, 'query_relevance_score'):
                    if entity.query_relevance_score > 0.5:
                        sections.append({
                            'start': entity.line_start - 1,
                            'end': entity.line_end,
                            'reason': 'query_relevant',
                            'score': entity.query_relevance_score
                        })
                
                # Entities with many call relationships
                if hasattr(entity, 'calls') and hasattr(entity, 'called_by'):
                    total_connections = len(entity.calls) + len(entity.called_by)
                    if total_connections > 5:
                        sections.append({
                            'start': entity.line_start - 1,
                            'end': entity.line_end,
                            'reason': 'high_connectivity',
                            'score': total_connections
                        })
        
        # If git data available, check for frequently changed sections
        if self.git_analyzer and hasattr(file_info, 'change_frequency') and file_info.change_frequency > 10:
            # For simplicity, flag the whole file as frequently changed
            sections.append({
                'start': 0,
                'end': min(50, len(lines)),  # First 50 lines
                'reason': 'high_change_frequency',
                'score': file_info.change_frequency
            })
        
        # Sort by score and return top sections
        sections.sort(key=lambda s: s['score'], reverse=True)
        return sections
    
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
            'frameworks': [],
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
                    for framework in frameworks:
                        if framework not in analysis['frameworks']:
                            analysis['frameworks'].append(framework)
        
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
        self.git_analyzer = None  # Will be initialized when processing a git repo
        self.llm_augmenter = None  # Will be initialized if configured
        
        # Track skipped files for reporting (requirement S-1)
        self.skipped_files = []  # List of (path, reason) tuples
        
        # Initialize LLM augmenter if enabled
        if profile.enable_llm_summarization or profile.enable_llm_proactive_augmentation:
            try:
                # Extract provider name from model (e.g., "gemini-1.5-flash" -> "gemini")
                provider = profile.llm_augmentation_model.split('-')[0].lower()
                self.llm_augmenter = LLMAugmenter(
                    provider=provider,
                    api_key_env_var=profile.llm_augmentation_api_key_env_var
                )
                if self.llm_augmenter.is_available():
                    print(f"LLM augmentation enabled with {provider}")
                else:
                    print(f"LLM augmentation configured but provider {provider} is not available")
            except Exception as e:
                print(f"Failed to initialize LLM augmenter: {e}")
        
        # Initialize action block generator
        self.action_block_generator = ActionBlockGenerator({
            'enable_action_blocks': profile.enable_action_blocks,
            'action_block_format': profile.action_block_format,
            'action_block_types': profile.action_block_types,
            'action_block_filters': profile.action_block_filters
        })
        
        self.scanner = UltraFileScanner(self.cache, self.token_manager, self.code_analyzer, self.profile)
        self.processor = ContentProcessor(self.token_manager, self.code_analyzer, self.profile, 
                                         self.git_analyzer, self.llm_augmenter, self.action_block_generator)
        self.codebase_analyzer = CodebaseAnalyzer(self.code_analyzer)
        self.manifest_generator = ManifestGenerator(self.token_manager, self.code_analyzer, self.action_block_generator)
    
    def process_repository(self, repo_path: Path, output_path: Path):
        """Process repository with all optimizations"""
        start_time = time.time()
        
        print(f"Starting ultra-optimized processing...")
        print(f"Model: {self.profile.model}")
        print(f"Token Budget: {self.profile.token_budget:,}")
        print(f"Repository: {repo_path}")
        print()
        
        # Initialize GitAnalyzer if enabled and it's a git repo
        if self.profile.enable_git_insights:
            self.git_analyzer = GitAnalyzer(repo_path)
            if self.git_analyzer.is_git_repo():
                print("Git repository detected - insights will be included")
                self.processor.git_analyzer = self.git_analyzer
            else:
                print("Not a git repository - git insights disabled")
                self.git_analyzer = None
        
        # Check and create AI guardrails file if needed
        self._check_and_create_ai_guardrails(repo_path)
        
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
        
        # Reserve a placeholder for the manifest (we'll generate it after processing files)
        manifest_placeholder_index = None
        if self.profile.generate_manifest and (self.profile.model == 'gemini-1.5-pro' or self.profile.token_budget > 500000):
            print("\nReserving space for hierarchical manifest...")
            output_parts.append("[MANIFEST_PLACEHOLDER]")
            manifest_placeholder_index = len(output_parts) - 1
        
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
        
        # Track token offsets for each file
        file_offset_map = {}
        current_token_offset = sum(self.token_manager.count_tokens(part) for part in output_parts)
        
        processed_count = 0
        for i, file_info in enumerate(files):
            if self.token_manager.budget.remaining < 1000:  # Reserve some tokens for footer
                print(f"Token budget exhausted at file {i}/{len(files)}")
                # Track remaining files as skipped due to token budget
                for remaining_file in files[i:]:
                    self.skipped_files.append((remaining_file.rel_path, "Token budget exhausted"))
                break
            
            # Get remaining budget for this file
            remaining_budget = min(
                self.token_manager.budget.remaining - 1000,
                self.profile.max_file_size
            )
            
            # Track offset for this file
            file_offset_map[str(file_info.rel_path)] = current_token_offset
            
            # Process file
            content, tokens_used = self.processor.process_file(file_info, remaining_budget)
            
            if tokens_used > 0:
                file_header = f"\n[[FILE_START: {file_info.rel_path}]]\n"
                file_header += f"File: {file_info.rel_path}\n"
                file_header += f"Language: {file_info.language or 'Unknown'}\n"
                file_header += f"Size: {file_info.size:,} bytes | Tokens: {tokens_used:,}\n"
                file_header += "-" * 40 + "\n"
                
                # Add inline action blocks if configured
                action_blocks_prefix = ""
                if (self.action_block_generator and 
                    self.action_block_generator.format in ['inline', 'both']):
                    inline_blocks = self.action_block_generator.generate_inline_blocks(str(file_info.rel_path))
                    if inline_blocks:
                        action_blocks_prefix = '\n'.join(inline_blocks) + '\n\n'
                
                file_output = file_header + action_blocks_prefix + content + "\n"
                file_tokens = self.token_manager.count_tokens(file_output)
                
                if self.token_manager.budget.remaining >= file_tokens:
                    output_parts.append(file_output)
                    self.token_manager.budget.allocate(file_info.rel_path, file_tokens, file_info.importance_score)
                    processed_count += 1
                    
                    # Update current offset for next file
                    current_token_offset += file_tokens
                    
                    if processed_count % 10 == 0:
                        print(f"Processed {processed_count} files...")
        
        # Generate manifest with accurate token offsets
        if manifest_placeholder_index is not None:
            print("\nGenerating hierarchical manifest with token locations...")
            manifest_text, _ = self.manifest_generator.generate_manifest(
                files, codebase_analysis, file_offset_map=file_offset_map)
            manifest_tokens = self.token_manager.count_tokens(manifest_text)
            
            if self.token_manager.budget.remaining >= manifest_tokens:
                self.token_manager.budget.reserve('manifest', manifest_tokens)
                output_parts[manifest_placeholder_index] = manifest_text
            else:
                output_parts[manifest_placeholder_index] = "[Manifest omitted due to token budget]"
        
        # Add footer
        footer = self._generate_footer(codebase_analysis, processed_count, len(files))
        footer_tokens = self.token_manager.count_tokens(footer)
        
        if self.token_manager.budget.remaining >= footer_tokens:
            output_parts.append(footer)
        
        # Write output
        final_output = '\n'.join(output_parts)
        output_path.write_text(final_output, encoding='utf-8')
        
        # Generate structured output if action blocks are enabled
        if self.action_block_generator and self.action_block_generator.enabled:
            structured_output = self.action_block_generator.generate_structured_output()
            
            # Convert sets to lists in codebase_analysis for JSON serialization
            serializable_analysis = codebase_analysis.copy()
            if 'frameworks' in serializable_analysis and isinstance(serializable_analysis['frameworks'], set):
                serializable_analysis['frameworks'] = list(serializable_analysis['frameworks'])
            
            structured_output['codebase_analysis'] = serializable_analysis
            structured_output['processing_stats'] = {
                'files_processed': processed_count,
                'total_files': len(files),
                'tokens_used': self.token_manager.budget.used,
                'token_budget': self.token_manager.budget.total,
                'processing_time_seconds': time.time() - start_time
            }
            
            # Write structured output alongside main output
            structured_path = output_path.parent / f"{output_path.stem}_analysis.json"
            with open(structured_path, 'w') as f:
                json.dump(structured_output, f, indent=2)
            print(f"Structured analysis written to: {structured_path}")
        
        # Save cache
        self.cache.save_caches()
        
        # Print summary
        elapsed_time = time.time() - start_time
        print(f"\nProcessing complete in {elapsed_time:.1f} seconds")
        print(f"Output written to: {output_path}")
        print(f"Files processed: {processed_count}/{len(files)}")
        print(f"Total tokens used: {self.token_manager.budget.used:,}/{self.token_manager.budget.total:,}")
        print(f"Token utilization: {self.token_manager.budget.used/self.token_manager.budget.total*100:.1f}%")
    
    def _check_and_create_ai_guardrails(self, repo_path: Path):
        """Check for ai_guardrails.md and create if missing and configured"""
        if not self.profile.auto_create_ai_guardrails_file:
            return
            
        # Check for the vibe_coder_gemini_claude profile
        if self.profile.name != 'vibe_coder_gemini_claude':
            return
            
        ai_guardrails_path = repo_path / 'ai_guardrails.md'
        
        if not ai_guardrails_path.exists():
            print("Creating ai_guardrails.md with default content...")
            default_content = """IMPORTANT FOR AI CODER:
1. Only modify code directly related to the current plan and instructions. Do not make unrelated changes or refactor code outside the immediate scope unless explicitly asked.
2. Preserve existing comments and docstrings unless updating them is part of the task or they become inaccurate due to your changes.
3. Ask for clarification if any instruction is ambiguous *before* making potentially incorrect changes.
4. Follow existing code style and conventions in the project.
5. If creating new files, place them in the most appropriate directory based on project structure.
6. Always provide test cases for new functionality when applicable.
7. Document any assumptions made during implementation.
8. Keep security best practices in mind - never hardcode secrets or credentials.
9. Make commits with clear, descriptive messages following the project's commit convention.
10. If modifying build configurations or dependencies, ensure compatibility with existing requirements.
"""
            ai_guardrails_path.write_text(default_content)
            print(f"Created ai_guardrails.md at {ai_guardrails_path}")
    
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
        filtered_files = []
        
        for file in files:
            # Check file size limit (requirement N-1)
            if file.size > self.profile.max_file_size:
                self.skipped_files.append((file.rel_path, f"File too large ({file.size:,} bytes)"))
                continue
            
            # Check if it's a binary file
            if file.is_binary:
                self.skipped_files.append((file.rel_path, "Binary file"))
                continue
            
            # Filter out files below minimum importance
            if file.importance_score < self.profile.min_importance_score:
                self.skipped_files.append((file.rel_path, f"Low importance score ({file.importance_score:.2f})"))
                continue
                
            filtered_files.append(file)
        
        # Apply custom priority boosts
        for file in filtered_files:
            for pattern, boost in self.profile.priority_boost.items():
                if fnmatch.fnmatch(file.rel_path, pattern):
                    file.importance_score += boost
        
        # Sort by importance (descending) and size (ascending)
        filtered_files.sort(key=lambda f: (-f.importance_score, f.size))
        
        return filtered_files
    
    def _generate_header(self, analysis: Dict, repo_path: Path) -> str:
        """Generate informative header with Vibe Coder sections"""
        header = []
        
        # Generate Gemini Planner Primer if vibe statement is provided
        if self.profile.vibe_statement:
            header.extend(self._generate_gemini_planner_primer(analysis, repo_path))
            header.extend(["", ""])  # Add some spacing
        
        # Generate Claude Coder Super-Context section if planner output is provided
        if self.profile.planner_output:
            header.extend(self._generate_claude_coder_context_header(repo_path))
            header.extend(["", ""])  # Add some spacing
        
        # Standard header if no vibe coder features are enabled
        if not self.profile.vibe_statement and not self.profile.planner_output:
            header.extend(["# Repository Analysis Report", "=" * 50, ""])
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
    
    def _generate_gemini_planner_primer(self, analysis: Dict, repo_path: Path) -> List[str]:
        """Generate Section 1: Gemini Planner Primer"""
        section = []
        section.extend([
            "=" * 50,
            "SECTION 1: FOR AI PLANNING AGENT (e.g., Gemini 1.5 Pro in AI Studio)",
            "Copy and paste this section into your Planning AI.",
            "=" * 50,
            "",
            "INITIAL FEATURE VIBE/GOAL:",
            self.profile.vibe_statement,
            "",
            "PROJECT SNAPSHOT & HIGH-LEVEL CONTEXT:",
            f"- Primary Language: {analysis['primary_language'] or 'Not determined'}",
            f"- Key Frameworks/Libraries: {', '.join(sorted(analysis['frameworks']))}",
            "- Core Modules/Areas:"
        ])
        
        # Add key directory structure
        for key_dir in analysis.get('key_directories', [])[:5]:
            section.append(f"  - {key_dir['path']}: {key_dir.get('purpose', 'Unknown purpose')}")
        
        # Add initial focus areas if LLM augmenter is available
        if self.profile.vibe_statement and self.llm_augmenter and self.llm_augmenter.is_available():
            try:
                focus_areas = self._identify_vibe_relevant_areas(analysis, self.profile.vibe_statement)
                if focus_areas:
                    section.extend([
                        "- Initial Focus Areas Suggested by Repo2File (based on your vibe statement & code structure):"
                    ])
                    for area in focus_areas[:3]:
                        section.append(f"  - {area}")
            except Exception as e:
                print(f"Error generating focus areas: {e}")
        
        # Add Git insights summary if available
        if self.git_analyzer and analysis.get('recent_activity'):
            section.extend([
                "",
                "AREAS OF RECENT ACTIVITY / POTENTIAL CHURN (Git Insights):",
                f"- Files with most changes (last 30d): {', '.join([f'{f[0]} ({f[1]} commits)' for f in analysis['recent_activity']['most_changed'][:3]])}",
                f"- Key files recently modified: {', '.join([f'{f[0]} ({f[1]}, {f[2]})' for f in analysis['recent_activity']['recent_files'][:3]])}"
            ])
        
        # Add TODO summary
        if self.action_block_generator and self.action_block_generator.enabled:
            todos = [b for b in self.action_block_generator.blocks if isinstance(b, TodoItem)]
            high_priority_todos = [t for t in todos if t.priority == 'high'][:5]
            if high_priority_todos:
                section.extend([
                    "",
                    "SUMMARY OF KNOWN TODOS / ACTION ITEMS (Top 5-10):"
                ])
                for todo in high_priority_todos:
                    section.append(f"- [{todo.todo_type} from {todo.file}]: {todo.text}")
        
        section.extend([
            "",
            "This initial context provides a strategic overview. More detailed code will be supplied to the coding agent based on your plan.",
            ""
        ])
        
        return section
    
    def _generate_claude_coder_context_header(self, repo_path: Path = None) -> List[str]:
        """Generate Section 2: Claude Coder Super-Context header"""
        section = []
        section.extend([
            "=" * 50,
            "SECTION 2: FOR AI CODING AGENT (e.g., Local Claude Code)",
            "This section contains the detailed codebase context and the plan from the AI Planning Agent.",
            "=" * 50,
            ""
        ])
        
        # Inject AI guardrails first if they exist
        if repo_path:
            ai_guardrails_path = repo_path / 'ai_guardrails.md'
            if ai_guardrails_path.exists():
                section.extend([
                    "--- CRITICAL AI CODER GUARDRAILS (Read First!) ---",
                    ai_guardrails_path.read_text().strip(),
                    "--- END GUARDRAILS ---",
                    ""
                ])
        
        section.extend([
            "REMINDER OF OVERALL GOAL:",
            "INITIAL FEATURE VIBE/GOAL:",
            self.profile.vibe_statement if self.profile.vibe_statement else "[No vibe statement provided]",
            "",
            "PLAN/INSTRUCTIONS FROM AI PLANNING AGENT (Gemini 1.5 Pro):",
            self.profile.planner_output,
            ""
        ])
        
        # Inject selected project rules if any
        if hasattr(self.profile, 'selected_rules') and self.profile.selected_rules and repo_path:
            section.extend([
                "--- IMPORTANT PROJECT RULES & GUIDELINES ---",
                ""
            ])
            
            # Read each selected rule file
            for rule_file in self.profile.selected_rules:
                rule_path = repo_path / 'instructions' / rule_file
                if rule_path.exists():
                    section.extend([
                        f"### {rule_file}",
                        rule_path.read_text(),
                        ""
                    ])
        
        section.extend([
            "--- DETAILED CODEBASE CONTEXT ---",
            ""
        ])
        return section
    
    def _identify_vibe_relevant_areas(self, analysis: Dict, vibe: str) -> List[str]:
        """Use LLM to identify areas most relevant to the vibe statement"""
        prompt = f"""
        Given the following project structure and vibe statement, identify 2-3 specific files or modules 
        that are most likely relevant to achieving the goal.
        
        Vibe/Goal: {vibe}
        
        Project Type: {analysis['project_type']}
        Primary Language: {analysis['primary_language']}
        Key Files: {', '.join(analysis['key_files'][:10])}
        
        Suggest specific files or modules with brief reasoning.
        """
        
        try:
            response = self.llm_augmenter.identify_potential_ambiguities(prompt, task_context="identifying focus areas")
            # Parse response to extract file suggestions
            suggestions = []
            for line in response.split('\n'):
                if line.strip() and ('/' in line or '.py' in line or '.js' in line):
                    suggestions.append(line.strip())
            return suggestions[:3]
        except Exception as e:
            print(f"Error identifying vibe-relevant areas: {e}")
            return []
    
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
            
        # Add skipped files report (requirement S-1)
        if self.skipped_files:
            footer.append("")
            footer.append("## Skipped / Truncated Files")
            footer.append(f"Total: {len(self.skipped_files)} files")
            footer.append("")
            
            # Group by reason for better readability
            skip_reasons = {}
            for path, reason in self.skipped_files:
                if reason not in skip_reasons:
                    skip_reasons[reason] = []
                skip_reasons[reason].append(path)
            
            for reason, paths in skip_reasons.items():
                footer.append(f"### {reason} ({len(paths)} files)")
                for path in paths[:10]:  # Limit to first 10 per reason
                    footer.append(f"  - {path}")
                if len(paths) > 10:
                    footer.append(f"  ... and {len(paths) - 10} more")
                footer.append("")
        
        footer.append("")
        footer.append("Generated by UltraRepo2File")
        
        return '\n'.join(footer)
    
    def extract_content_from_previous_output(self, previous_output_path: Path) -> Dict:
        """Extract content from previous repo2file output"""
        with open(previous_output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract vibes/goals
        vibe_pattern = r"My Vibe / Primary Goal:.+?(?=\n\n)"
        vibe_match = re.search(vibe_pattern, content, re.DOTALL)
        vibe_statement = vibe_match.group(0).replace("My Vibe / Primary Goal:", "").strip() if vibe_match else ""
        
        # Extract planner output
        planner_start = content.find("SECTION 1: FOR AI PLANNING AGENT")
        planner_end = content.find("SECTION 2: FOR AI CODER") if "SECTION 2: FOR AI CODER" in content else len(content)
        planner_output = content[planner_start:planner_end].strip() if planner_start != -1 else ""
        
        # Extract key files and their content
        file_blocks = {}
        file_pattern = r"\[\[FILE_START:(.*?)\]\](.+?)\[\[FILE_END\]\]"
        for match in re.finditer(file_pattern, content, re.DOTALL):
            file_path = match.group(1).strip()
            file_content = match.group(2).strip()
            file_blocks[file_path] = file_content
        
        return {
            "vibe_statement": vibe_statement,
            "planner_output": planner_output,
            "file_blocks": file_blocks,
            "raw_content": content
        }
    
    def generate_iteration_brief(self, repo_path: Path, session_data: Dict, user_feedback: str = "") -> str:
        """Generate iteration brief (Section C) for Gemini planner"""
        brief = []
        brief.append("=" * 50)
        brief.append("SECTION 3: ITERATION CONTEXT FOR AI PLANNING AGENT")
        brief.append("This section provides updated context after a coding iteration.")
        brief.append("=" * 50)
        brief.append("")
        
        # Original vibe/goals
        if session_data.get("feature_vibe"):
            brief.append("## RECAP OF ORIGINAL FEATURE VIBE/GOAL:")
            brief.append(session_data["feature_vibe"])
            brief.append("")
        
        # User feedback and notes
        if user_feedback:
            brief.append("## USER'S FEEDBACK & NOTES ON RECENT WORK:")
            brief.append(user_feedback)
            brief.append("")
        
        # Git diff summary
        latest_iteration = session_data.get('iterations', [])[-1] if session_data.get('iterations') else None
        if latest_iteration and latest_iteration.get('diff_summary'):
            diff_summary = latest_iteration['diff_summary']
            brief.append("## GIT DIFF SUMMARY SINCE LAST PLANNING:")
            brief.append(f"- Files changed: {len(diff_summary.get('changed_files', []))}")
            brief.append(f"- Overall changes: {diff_summary.get('overall_summary_stats', 'N/A')}")
            brief.append("")
            
            if diff_summary.get('changed_files'):
                brief.append("### Modified Files:")
                for file_info in diff_summary['changed_files'][:10]:  # Limit to top 10
                    file_path = file_info.get('file', '')
                    status = file_info.get('status', 'M')
                    insertions = file_info.get('insertions', 0)
                    deletions = file_info.get('deletions', 0)
                    brief.append(f"- {file_path} [{status}] +{insertions}/-{deletions}")
                if len(diff_summary['changed_files']) > 10:
                    brief.append(f"- ... and {len(diff_summary['changed_files']) - 10} more files")
                brief.append("")
            
            if diff_summary.get('key_modified_functions'):
                brief.append("### Key Modified Functions:")
                for func_info in diff_summary['key_modified_functions'][:10]:
                    if isinstance(func_info, dict):
                        file_name = func_info.get('file', 'unknown')
                        func_name = func_info.get('function', 'unknown')
                        change_type = func_info.get('change_type', 'modified')
                        brief.append(f"- {file_name}: {func_name} ({change_type})")
                    else:
                        brief.append(f"- {func_info}")
                if len(diff_summary['key_modified_functions']) > 10:
                    brief.append(f"- ... and {len(diff_summary['key_modified_functions']) - 10} more functions")
                brief.append("")
        
        # Test Results Diff
        if latest_iteration and latest_iteration.get('test_results'):
            test_results = latest_iteration['test_results']
            brief.append("## TEST RESULTS DIFF:")
            
            if test_results.get('passed') is not None:
                brief.append(f"- Status: {'✅ PASSED' if test_results['passed'] else '❌ FAILED'}")
            
            if test_results.get('summary'):
                brief.append(f"- Summary: {test_results['summary']}")
            
            if test_results.get('command'):
                brief.append(f"- Command: {test_results['command']}")
            
            if test_results.get('elapsed_time'):
                brief.append(f"- Duration: {test_results['elapsed_time']:.2f}s")
            
            if test_results.get('error'):
                brief.append(f"- Error: {test_results['error']}")
            
            brief.append("")
        
        # Previous planning context (truncated)
        if session_data.get("last_gemini_plan"):
            brief.append("## PREVIOUS PLANNING CONTEXT (Summary):")
            plan_lines = session_data["last_gemini_plan"].split('\n')
            # Extract first 20 lines or until we find a section header
            summary_lines = []
            for i, line in enumerate(plan_lines[:50]):
                summary_lines.append(line)
                if i > 20 and (line.startswith('#') or line.startswith('**')):
                    break
            brief.extend(summary_lines)
            brief.append("... (truncated)")
            brief.append("")
        
        # Focused code snapshot
        brief.append("## FOCUSED CURRENT CODE SNAPSHOT:")
        brief.append("")
        
        # Generate focused snapshot of changed files
        if latest_iteration and latest_iteration.get('diff_summary'):
            changed_files = [f['file'] for f in latest_iteration['diff_summary'].get('changed_files', [])]
            
            # Add files mentioned in user feedback
            if user_feedback:
                import re
                # Look for file paths in feedback
                potential_files = re.findall(r'[\w/]+\.\w+', user_feedback)
                changed_files.extend(potential_files)
            
            # Remove duplicates and filter to existing files
            unique_files = list(set(changed_files))
            existing_files = []
            for file_path in unique_files:
                full_path = repo_path / file_path
                if full_path.exists():
                    existing_files.append(full_path)
            
            # Generate mini manifest for these files
            if existing_files:
                brief.append("### Files included in this snapshot:")
                for file_path in existing_files[:10]:  # Limit to 10 files
                    rel_path = file_path.relative_to(repo_path)
                    brief.append(f"- {rel_path}")
                brief.append("")
                
                # Now generate actual content (limited by token budget)
                # This is where we'd run a focused version of the manifest generation
                brief.append("### File Contents:")
                brief.append("```")
                brief.append("[File content generation would go here - limited by iteration_code_snapshot_budget]")
                brief.append("```")
            else:
                brief.append("No changed files found for focused snapshot.")
        
        brief.append("")
        brief.append("## REQUEST FOR NEXT PLANNING ITERATION:")
        brief.append("Based on the above changes, test results, and my feedback, please provide:")
        brief.append("1. Assessment of what was successfully implemented")
        brief.append("2. What still needs to be done to complete the feature")
        brief.append("3. Any issues or bugs that need to be addressed")
        brief.append("4. Suggested next steps for the AI Coder")
        brief.append("")
        
        return '\n'.join(brief)

def main_iterate():
    """Main entry point for iteration mode"""
    try:
        print("Running in iteration mode...")
        
        # Parse iteration-specific arguments
        current_repo_path = None
        previous_output_path = None
        user_feedback_file = None
        output_path = Path("iteration-brief.md")
        
        i = 2  # Skip 'dump_ultra.py' and 'iterate'
        while i < len(sys.argv):
            arg = sys.argv[i]
            if arg == '--current-repo-path' and i + 1 < len(sys.argv):
                current_repo_path = Path(sys.argv[i + 1])
                i += 2
            elif arg == '--previous-repo2file-output' and i + 1 < len(sys.argv):
                previous_output_path = Path(sys.argv[i + 1])
                i += 2
            elif arg == '--user-feedback-file' and i + 1 < len(sys.argv):
                user_feedback_file = Path(sys.argv[i + 1])
                i += 2
            elif arg == '--output' and i + 1 < len(sys.argv):
                output_path = Path(sys.argv[i + 1])
                i += 2
            else:
                i += 1
        
        # Validate required arguments
        if not current_repo_path or not previous_output_path:
            print("Error: Both --current-repo-path and --previous-repo2file-output are required")
            sys.exit(1)
        
        if not current_repo_path.exists():
            print(f"Error: Repository path '{current_repo_path}' does not exist")
            sys.exit(1)
        
        if not previous_output_path.exists():
            print(f"Error: Previous output file '{previous_output_path}' does not exist")
            sys.exit(1)
        
        # Load user feedback if provided
        user_feedback = ""
        if user_feedback_file and user_feedback_file.exists():
            with open(user_feedback_file, 'r') as f:
                user_feedback = f.read()
        
        # Create processor with default profile
        profile = ProcessingProfile(
            name="iteration",
            token_budget=500000,
            model="claude-3",
            enable_git_insights=True
        )
        processor = UltraRepo2File(profile)
        
        # Initialize git analyzer
        processor.git_analyzer = GitAnalyzer(current_repo_path)
        
        # Extract content from previous output
        print("Extracting content from previous output...")
        previous_content = processor.extract_content_from_previous_output(previous_output_path)
        
        # Generate iteration brief
        print("Generating iteration brief...")
        iteration_brief = processor.generate_iteration_brief(
            current_repo_path,
            previous_content,
            user_feedback
        )
        
        # Write output
        with open(output_path, 'w') as f:
            f.write(iteration_brief)
        
        print(f"Iteration brief written to: {output_path}")
        
        # Also generate a new repo2file output with the updated context
        print("\nGenerating updated repo2file output...")
        new_output_path = output_path.with_stem(f"{output_path.stem}-repo2file")
        
        # Update profile with extracted information
        profile.vibe_statement = previous_content["vibe_statement"]
        profile.planner_output = previous_content["planner_output"]
        
        # Process repository with updated context
        processor.process_repository(current_repo_path, new_output_path)
        
        print(f"Updated repo2file output written to: {new_output_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

def main():
    """Main entry point"""
    try:
        print(f"Arguments: {sys.argv}")
        
        # Check for iterate mode
        if len(sys.argv) >= 2 and sys.argv[1] == 'iterate':
            return main_iterate()
        
        if len(sys.argv) < 3:
            print("Usage: python dump_ultra.py <repo_path> <output_file> [profile_file] [options]")
            print("       python dump_ultra.py iterate --current-repo-path <path> --previous-repo2file-output <path> [options]")
            print("\nOptions:")
            print("  --model MODEL      LLM model to optimize for (default: gpt-4)")
            print("  --budget TOKENS    Token budget (default: 500000)")
            print("  --profile NAME     Use named profile")
            print("  --exclude PATTERN  Add exclusion pattern")
            print("  --boost PATTERN    Boost priority for files matching pattern")
            print("  --manifest         Generate hierarchical manifest")
            print("  --truncation MODE  Truncation strategy (semantic, basic, middle_summarize, business_logic)")
            print("  --query TEXT       Intended LLM query for context-aware prioritization")
            print("  --vibe TEXT        High-level goal/vibe statement for Gemini planner")
            print("  --planner TEXT     AI planner output to integrate into coder context")
            print("  --git-insights     Enable git history insights")
            print("\nIteration Mode Options:")
            print("  --current-repo-path PATH      Current repository path")
            print("  --previous-repo2file-output PATH   Previous repo2file output to compare")
            print("  --user-feedback-file PATH     Optional file with user feedback")
            print("  --output PATH                 Output file for iteration brief (default: iteration-brief.md)")
            print("\nExamples:")
            print("  python dump_ultra.py ./myrepo output.txt")
            print("  python dump_ultra.py ./myrepo output.txt --model claude-3 --budget 200000")
            print("  python dump_ultra.py ./myrepo output.txt --exclude '*.log' --boost '*.py:0.5'")
            print("  python dump_ultra.py ./myrepo output.txt --vibe 'Improve checkout speed' --planner 'plan.txt'")
            print("  python dump_ultra.py iterate --current-repo-path ./myrepo --previous-repo2file-output output.txt")
            sys.exit(1)
        
        repo_path = Path(sys.argv[1])
        output_path = Path(sys.argv[2])
        
        # Parse arguments
        profile = ProcessingProfile(
            name="default",
            token_budget=DEFAULT_TOKEN_BUDGET,
            model="gpt-4"
        )
        
        # Process profile first
        i = 3
        while i < len(sys.argv):
            arg = sys.argv[i]
            if arg == '--profile' and i + 1 < len(sys.argv):
                profile_name = sys.argv[i + 1]
                print(f"Loading profile: {profile_name}")
                # Load from app/profiles.py
                sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from app.profiles import DEFAULT_PROFILES
                if profile_name in DEFAULT_PROFILES:
                    app_profile = DEFAULT_PROFILES[profile_name]
                    # Convert app profile to dump_ultra profile
                    print(f"Profile model: {app_profile.model}")
                    profile = ProcessingProfile(
                        name=app_profile.name,
                        token_budget=app_profile.token_budget,
                        model=app_profile.model,
                        exclude_patterns=app_profile.exclude_patterns,
                        generate_manifest=getattr(app_profile, 'generate_manifest', True),
                        truncation_strategy=getattr(app_profile, 'truncation_strategy', 'semantic'),
                        enable_git_insights=app_profile.name == 'gemini'  # Enable for Gemini profile
                    )
                    # Copy priority patterns if they exist
                    if hasattr(app_profile, 'priority_patterns'):
                        for pattern, score in app_profile.priority_patterns.items():
                            profile.priority_boost[pattern] = score
                else:
                    # Try loading as a file path for backwards compatibility
                    profile_path = Path(profile_name)
                    if profile_path.exists():
                        profile = ProcessingProfile.load(profile_path)
                i += 2
            else:
                i += 1
        
        # Then process other arguments (which may override profile settings)
        i = 3
        while i < len(sys.argv):
            arg = sys.argv[i]
            if arg == '--model' and i + 1 < len(sys.argv):
                model_arg = sys.argv[i + 1]
                print(f"Setting model from arg: '{model_arg}'")
                if model_arg:  # Only set if not empty
                    profile.model = model_arg
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
            elif arg == '--profile':
                # Skip - already processed in first pass
                i += 2
            elif arg == '--manifest':
                profile.generate_manifest = True
                i += 1
            elif arg == '--truncation' and i + 1 < len(sys.argv):
                profile.truncation_strategy = sys.argv[i + 1]
                i += 2
            elif arg == '--query' and i + 1 < len(sys.argv):
                profile.intended_query = sys.argv[i + 1]
                i += 2
            elif arg == '--vibe' and i + 1 < len(sys.argv):
                profile.vibe_statement = sys.argv[i + 1]
                i += 2
            elif arg == '--planner' and i + 1 < len(sys.argv):
                # Check if it's a file path or direct text
                planner_arg = sys.argv[i + 1]
                if os.path.exists(planner_arg):
                    with open(planner_arg, 'r') as f:
                        profile.planner_output = f.read()
                else:
                    profile.planner_output = planner_arg
                i += 2
            elif arg == '--git-insights':
                profile.enable_git_insights = True
                i += 1
            elif arg == '--rules' and i + 1 < len(sys.argv):
                # Accept comma-separated list of rule filenames
                rule_files = sys.argv[i + 1].split(',')
                profile.selected_rules = rule_files
                i += 2
            else:
                i += 1
        
        # Process repository
        processor = UltraRepo2File(profile)
        processor.process_repository(repo_path, output_path)
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()