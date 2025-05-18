import os
import sys
from typing import List, Set, Optional, Dict, Tuple
import fnmatch
import re
import mimetypes
import pathspec

# Configuration constants
TOKEN_BUDGET = 500000  # Global token budget (500K tokens)
MAX_FILE_SIZE = 100 * 1024  # 100KB
MAX_LINES_PER_FILE = 500
CHARS_PER_TOKEN = 3  # Conservative estimate: ~3 characters per token

# File type classifications
BINARY_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.pdf', '.exe', '.dll', '.so', '.dylib', 
    '.zip', '.tar', '.gz', '.mp4', '.mp3', '.wav', '.avi', '.mov', '.bin', 
    '.pyc', '.class', '.ico', '.ttf', '.woff', '.woff2', '.eot', '.webp',
    '.svg', '.bmp', '.psd', '.ai', '.sketch', '.fig', '.xd', '.jar', '.war',
    '.apk', '.dmg', '.iso', '.rar', '.7z', '.bz2', '.xz', '.deb', '.rpm'
}

AUTO_GENERATED_PATTERNS = [
    r'.*\.min\.(js|css)$',  # Minified JS/CSS
    r'.*\.bundle\.js$',     # Bundled JS
    r'.*\.map$',            # Source maps
    r'.*\.lock$',           # Lock files (package-lock, etc)
    r'.*\.generated\.',     # Generated files
    r'.*\.auto\.',          # Auto-generated files
    r'.*\.d\.ts$',          # TypeScript declaration files
    r'.*-lock\.json$',      # npm/yarn lock files
    r'.*\.(log|logs)$',     # Log files
    r'build/.*',            # Build directories
    r'dist/.*',             # Distribution directories
    r'node_modules/.*',     # Node modules
    r'__pycache__/.*',      # Python cache
    r'.*\.cache/.*',        # Cache directories
]

TRIVIAL_FILES = {
    '.editorconfig', '.eslintignore', '.prettierignore', 'thumbs.db', 
    '.DS_Store', 'desktop.ini', 'LICENSE', 'LICENSE.md', 'LICENSE.txt', 
    'CONTRIBUTING.md', 'CODE_OF_CONDUCT.md', '.gitkeep', '.gitattributes',
    '.dockerignore', '.npmignore', '.yarnignore', '.env.example.local',
    'AUTHORS', 'CREDITS', 'NOTICE', 'PATENTS', 'VERSION'
}

# Files that should have their structure summarized, not full content
SUMMARIZE_FILES = {
    'package-lock.json', 'yarn.lock', 'poetry.lock', 'Pipfile.lock',
    'composer.lock', 'Gemfile.lock', 'Cargo.lock', 'go.sum', 'pnpm-lock.yaml',
    'requirements.lock', 'pdm.lock', 'uv.lock', '.terraform.lock.hcl'
}

# Important files that should be included even if large
IMPORTANT_FILES = {
    'README.md', 'README.rst', 'README.txt', 'README', 'setup.py', 'setup.cfg',
    'package.json', 'requirements.txt', 'Gemfile', 'Cargo.toml', 'go.mod',
    'Pipfile', 'pyproject.toml', 'composer.json', '.gitignore', 'Makefile',
    'Dockerfile', 'docker-compose.yml', '.env.example', 'webpack.config.js',
    'vite.config.js', 'rollup.config.js', 'tsconfig.json', 'jest.config.js',
    'babel.config.js', '.eslintrc.js', '.prettierrc', 'vitest.config.js'
}

def estimate_tokens(text: str) -> int:
    """
    Estimates the number of tokens in a string.
    Using conservative estimate of ~3 characters per token.
    For more accuracy, consider using tiktoken with specific model encoding.
    """
    if not text:
        return 0
    return len(text) // CHARS_PER_TOKEN

def load_exclusion_patterns(start_path: str, custom_exclusion_file: Optional[str]) -> pathspec.PathSpec:
    """
    Loads .gitignore patterns from the root .gitignore and an optional custom exclusion file.
    Returns a PathSpec object for matching.
    """
    patterns = []
    
    # Load from .gitignore at the root of start_path
    gitignore_path = os.path.join(start_path, ".gitignore")
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
            patterns.extend(line for line in lines if line.strip() and not line.strip().startswith('#'))
        print(f"Loaded {len(patterns)} patterns from: {gitignore_path}")

    # Load from custom exclusion file if provided
    if custom_exclusion_file and os.path.exists(custom_exclusion_file):
        with open(custom_exclusion_file, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
            custom_patterns = [line for line in lines if line.strip() and not line.strip().startswith('#')]
            patterns.extend(custom_patterns)
            print(f"Loaded {len(custom_patterns)} patterns from custom exclusion file: {custom_exclusion_file}")
    
    # Create pathspec from patterns
    if patterns:
        return pathspec.PathSpec.from_lines('gitwildmatch', patterns)
    else:
        # Return empty pathspec that matches nothing
        return pathspec.PathSpec.from_lines('gitwildmatch', [])

def is_binary_file(file_path: str) -> bool:
    """Check if a file is binary based on extension and content."""
    # Check extension
    _, ext = os.path.splitext(file_path.lower())
    if ext in BINARY_EXTENSIONS:
        return True
    
    # Check MIME type
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type and not mime_type.startswith('text/'):
        return True
    
    # Check content for binary characters
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            if b'\0' in chunk:  # Null byte is a good indicator of binary file
                return True
            # Check for high proportion of non-printable characters
            text_chars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
            non_text = len([b for b in chunk if b not in text_chars])
            if non_text / len(chunk) > 0.3:
                return True
    except:
        pass
    return False

def is_auto_generated(file_path: str) -> bool:
    """Check if a file is auto-generated."""
    # Check against patterns
    for pattern in AUTO_GENERATED_PATTERNS:
        if re.match(pattern, file_path):
            return True
    
    # Check first few lines for generation markers
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            first_lines = []
            for _ in range(5):
                line = f.readline()
                if not line:
                    break
                first_lines.append(line)
            
            for line in first_lines:
                if any(marker in line.lower() for marker in [
                    'auto-generated', 'automatically generated', 'do not edit', 
                    'generated by', 'this file is generated', 'autogenerated',
                    'machine generated', 'computer generated', '/* generated'
                ]):
                    return True
    except:
        pass
    return False

def is_trivial_file(file_name: str) -> bool:
    """Check if a file is trivial and can be skipped."""
    return file_name.lower() in {f.lower() for f in TRIVIAL_FILES}

def get_file_info(file_path: str) -> Dict[str, any]:
    """Get comprehensive file information."""
    try:
        stat = os.stat(file_path)
        file_name = os.path.basename(file_path)
        base_name = file_name.lower()
        
        return {
            'size': stat.st_size,
            'size_str': format_file_size(stat.st_size),
            'binary': is_binary_file(file_path),
            'auto_generated': is_auto_generated(file_path),
            'trivial': is_trivial_file(file_name),
            'should_summarize': base_name in {f.lower() for f in SUMMARIZE_FILES},
            'is_important': base_name in {f.lower() for f in IMPORTANT_FILES}
        }
    except:
        return {
            'size': 0, 'size_str': '0B', 'binary': False, 
            'auto_generated': False, 'trivial': False, 
            'should_summarize': False, 'is_important': False
        }

def format_file_size(size: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f}{unit}"
        size /= 1024.0
    return f"{size:.1f}TB"

def should_skip_file(file_rel_path: str, file_abs_path: str, file_info: Dict[str, any], git_spec: pathspec.PathSpec) -> Optional[str]:
    """
    Determines if a file should be skipped based on various criteria.
    Returns a reason string if skipped, None otherwise.
    """
    # Gitignore patterns
    if git_spec and git_spec.match_file(file_rel_path):
        return "Matched .gitignore pattern"

    # Binary files
    if file_info['binary']:
        return "Binary file"
    
    # Auto-generated files (unless important)
    if file_info['auto_generated'] and not file_info['is_important']:
        return "Auto-generated file"
        
    # Trivial files (unless important)
    if file_info['trivial'] and not file_info['is_important']:
        return "Trivial file"
        
    return None

def truncate_content(content: str, file_rel_path: str, is_important: bool = False, 
                    max_size: int = MAX_FILE_SIZE, max_lines: int = MAX_LINES_PER_FILE) -> Tuple[str, bool]:
    """
    Intelligently truncate file content.
    Returns (truncated_content, was_truncated_flag).
    """
    lines = content.splitlines()
    original_length = len(content)
    was_truncated = False

    # Important files get more lenient truncation
    if is_important:
        max_size *= 2
        max_lines *= 2

    if len(lines) <= max_lines and original_length <= max_size:
        return content, False

    was_truncated = True
    
    # For code files, preserve structure
    code_extensions = (
        '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.hpp',
        '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala', '.m', '.mm',
        '.cs', '.vb', '.lua', '.pl', '.sh', '.bash', '.zsh', '.fish', '.ps1'
    )
    
    if file_rel_path.endswith(code_extensions):
        # For code files, get more context
        head_count = min(75, len(lines) // 3, max_lines // 2)
        tail_count = min(75, len(lines) // 3, max_lines // 2)
        
        if len(lines) > head_count + tail_count:
            truncated_lines = []
            truncated_lines.extend(lines[:head_count])
            truncated_lines.append(f"\n... [TRUNCATED - File has {len(lines)} lines. Showing first {head_count} and last {tail_count} lines] ...\n")
            truncated_lines.extend(lines[-tail_count:])
            return '\n'.join(truncated_lines), True
        else:
            # Not enough lines for complex truncation
            return '\n'.join(lines[:max_lines]) + f"\n... [TRUNCATED - Showing {max_lines} of {len(lines)} lines] ...", True
    else:
        # For other files, simpler truncation
        if len(lines) > max_lines:
            truncated_lines = lines[:max_lines]
            truncated_lines.append(f"\n... [TRUNCATED - File has {len(lines)} lines, showing first {max_lines}] ...\n")
            return '\n'.join(truncated_lines), True
        elif original_length > max_size:
            # Truncate by character length
            adjusted_content = content[:max_size]
            last_newline = adjusted_content.rfind('\n')
            if last_newline != -1:
                adjusted_content = adjusted_content[:last_newline]
            return adjusted_content + f"\n... [TRUNCATED - File size {format_file_size(original_length)} > {format_file_size(max_size)}] ...\n", True
        
        return content, False

def summarize_lock_file(content: str, file_name: str) -> str:
    """Create a summary of lock files instead of full content."""
    lines = content.splitlines()
    summary = [f"[LOCK FILE SUMMARY: {file_name}]"]
    
    # Count dependencies
    dependency_count = 0
    
    lower_name = file_name.lower()
    if lower_name == 'package-lock.json':
        # Count unique packages in npm lock file
        for line in lines:
            if '"resolved":' in line:
                dependency_count += 1
    elif lower_name in ['yarn.lock', 'pnpm-lock.yaml']:
        # Count packages in yarn/pnpm lock files
        for line in lines:
            if line and not line.startswith(' ') and not line.startswith('#'):
                dependency_count += 1
    elif lower_name == 'pipfile.lock':
        # Count packages in Pipenv lock file
        in_packages = False
        for line in lines:
            if '"packages":' in line or '"dev-packages":' in line:
                in_packages = True
            elif in_packages and line.strip().startswith('"') and '":' in line:
                dependency_count += 1
    elif lower_name in ['gemfile.lock', 'poetry.lock', 'cargo.lock']:
        # Count packages in other lock files
        for line in lines:
            if line.strip() and not line.startswith(' ') and not line.startswith('#'):
                if lower_name == 'cargo.lock' and line.startswith('[[package]]'):
                    dependency_count += 1
                elif lower_name == 'poetry.lock' and line.startswith('[[package]]'):
                    dependency_count += 1
                elif lower_name == 'gemfile.lock' and line.strip() and not line.startswith('GEM') and not line.startswith('PLATFORMS'):
                    dependency_count += 1
    else:
        # Generic counting for other lock files
        dependency_count = len([l for l in lines if l.strip() and not l.startswith('#')])
    
    summary.append(f"Total dependencies: ~{dependency_count}")
    summary.append(f"File size: {format_file_size(len(content))}")
    summary.append(f"Line count: {len(lines)}")
    summary.append(f"[Full content omitted - this is a lock file with dependency versions]")
    
    return '\n'.join(summary)

def analyze_codebase(start_path: str, exclusion_spec: pathspec.PathSpec) -> Dict[str, any]:
    """Analyze the codebase to provide AI-relevant summary."""
    analysis = {
        'primary_language': None,
        'frameworks': [],
        'project_type': None,
        'config_files': [],
        'test_directories': [],
        'build_files': [],
        'docs_directories': [],
        'total_files': 0,
        'file_types': {}
    }
    
    # Framework/config file markers
    framework_markers = {
        'package.json': 'Node.js',
        'requirements.txt': 'Python',
        'setup.py': 'Python',
        'pyproject.toml': 'Python',
        'Gemfile': 'Ruby',
        'Cargo.toml': 'Rust',
        'go.mod': 'Go',
        'composer.json': 'PHP',
        'pom.xml': 'Java/Maven',
        'build.gradle': 'Java/Gradle',
        '.csproj': '.NET',
        'tsconfig.json': 'TypeScript',
        'angular.json': 'Angular',
        'vue.config.js': 'Vue.js',
        'next.config.js': 'Next.js',
        'gatsby-config.js': 'Gatsby',
        'svelte.config.js': 'Svelte',
        'nuxt.config.js': 'Nuxt.js',
        'remix.config.js': 'Remix',
        'vite.config.js': 'Vite',
        'webpack.config.js': 'webpack',
        'Makefile': 'Make',
        'CMakeLists.txt': 'CMake',
        'Dockerfile': 'Docker',
        'docker-compose.yml': 'Docker Compose',
        '.github/workflows': 'GitHub Actions',
        '.gitlab-ci.yml': 'GitLab CI',
        'Jenkinsfile': 'Jenkins',
        '.circleci/config.yml': 'CircleCI'
    }
    
    for root, dirs, files in os.walk(start_path, topdown=True):
        rel_root_path = os.path.relpath(root, start_path)
        
        # Filter dirs in place based on gitignore
        if exclusion_spec:
            dirs[:] = [d for d in dirs if not exclusion_spec.match_file(
                os.path.join(rel_root_path, d) if rel_root_path != '.' else d
            )]
            
        # Check for test/docs directories
        for dir_name in dirs:
            lower_dir = dir_name.lower()
            dir_path = os.path.join(rel_root_path, dir_name) if rel_root_path != '.' else dir_name
            
            if any(test_name in lower_dir for test_name in ['test', 'tests', 'spec', 'specs', '__tests__']):
                analysis['test_directories'].append(dir_path)
            if any(doc_name in lower_dir for doc_name in ['docs', 'documentation', 'doc']):
                analysis['docs_directories'].append(dir_path)
        
        for file_name in files:
            file_rel_path = os.path.join(rel_root_path, file_name) if rel_root_path != '.' else file_name
            
            if exclusion_spec and exclusion_spec.match_file(file_rel_path):
                continue
                
            analysis['total_files'] += 1
            
            # Track file extensions
            _, ext = os.path.splitext(file_name)
            if ext:
                analysis['file_types'][ext] = analysis['file_types'].get(ext, 0) + 1
            
            # Check for framework markers
            for marker, framework in framework_markers.items():
                if file_name == marker or file_name.endswith(marker) or marker in file_rel_path:
                    if framework not in analysis['frameworks']:
                        analysis['frameworks'].append(framework)
                    analysis['config_files'].append(file_rel_path)
            
            # Check for build files
            if file_name in ['Makefile', 'CMakeLists.txt', 'build.gradle', 'pom.xml', 'setup.py', 'build.xml', 'meson.build']:
                analysis['build_files'].append(file_rel_path)
    
    # Determine primary language
    lang_extensions = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.java': 'Java',
        '.cs': 'C#',
        '.cpp': 'C++',
        '.c': 'C',
        '.go': 'Go',
        '.rs': 'Rust',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.m': 'Objective-C',
        '.scala': 'Scala',
        '.dart': 'Dart',
        '.lua': 'Lua',
        '.r': 'R',
        '.jl': 'Julia',
        '.ex': 'Elixir',
        '.clj': 'Clojure'
    }
    
    max_count = 0
    for ext, lang in lang_extensions.items():
        count = analysis['file_types'].get(ext, 0)
        if count > max_count:
            max_count = count
            analysis['primary_language'] = lang
    
    # Determine project type
    if any(f in analysis['frameworks'] for f in ['React', 'Vue.js', 'Angular', 'Svelte', 'Next.js', 'Nuxt.js']):
        analysis['project_type'] = 'Frontend Web Application'
    elif any(f in analysis['frameworks'] for f in ['Node.js', 'Express', 'Fastify', 'Koa']):
        analysis['project_type'] = 'Node.js Backend Application'
    elif 'Python' in analysis['frameworks'] and any(f in analysis['config_files'] for f in ['manage.py', 'wsgi.py']):
        analysis['project_type'] = 'Python Web Application'
    elif any(f in analysis['frameworks'] for f in ['Docker', 'Kubernetes']):
        analysis['project_type'] = 'Containerized Application'
    elif analysis['test_directories']:
        if analysis['primary_language']:
            analysis['project_type'] = f'{analysis["primary_language"]} Library/Package'
        else:
            analysis['project_type'] = 'Library/Package with Tests'
    elif analysis['primary_language']:
        analysis['project_type'] = f'{analysis["primary_language"]} Project'
    else:
        analysis['project_type'] = 'General Software Project'
    
    # Limit lists to prevent excessive output
    analysis['test_directories'] = analysis['test_directories'][:5]
    analysis['docs_directories'] = analysis['docs_directories'][:5]
    analysis['build_files'] = analysis['build_files'][:5]
    analysis['config_files'] = analysis['config_files'][:10]
    
    return analysis

def print_directory_structure(start_path: str, exclusion_spec: pathspec.PathSpec, max_depth: int = 4) -> str:
    """Generate a tree-like directory structure."""
    def _generate_tree(current_dir_abs: str, prefix: str = '', depth: int = 0) -> List[str]:
        if depth > max_depth:
            return [f"{prefix}... [deeper levels truncated]"]
            
        entries = sorted(os.listdir(current_dir_abs), 
                        key=lambda x: (not os.path.isdir(os.path.join(current_dir_abs, x)), x.lower()))
        tree_lines = []
        
        visible_entries = []
        for entry_name in entries:
            entry_abs_path = os.path.join(current_dir_abs, entry_name)
            entry_rel_path = os.path.relpath(entry_abs_path, start_path)
            
            # Skip hidden files/directories unless they're important
            if entry_name.startswith('.') and entry_name not in {'.gitignore', '.env.example', '.github', '.gitlab'}:
                continue
                
            if exclusion_spec and exclusion_spec.match_file(entry_rel_path):
                continue
                
            visible_entries.append(entry_name)
        
        for i, entry_name in enumerate(visible_entries):
            entry_abs_path = os.path.join(current_dir_abs, entry_name)
            
            is_last = i == len(visible_entries) - 1
            connector = '└── ' if is_last else '├── '
            new_prefix = prefix + ('    ' if is_last else '│   ')
            
            if os.path.isdir(entry_abs_path):
                tree_lines.append(f"{prefix}{connector}{entry_name}/")
                tree_lines.extend(_generate_tree(entry_abs_path, new_prefix, depth + 1))
            else:
                info = get_file_info(entry_abs_path)
                size_str = f" ({info['size_str']})" if info['size'] > 0 else ""
                binary_str = " [binary]" if info['binary'] else ""
                tree_lines.append(f"{prefix}{connector}{entry_name}{size_str}{binary_str}")
        
        return tree_lines
    
    tree = [os.path.basename(start_path) + '/'] + _generate_tree(start_path)
    return '\n'.join(tree)

def scan_folder(start_path: str, file_types_filter: Optional[List[str]], 
                output_file_path: str, exclusion_spec: pathspec.PathSpec) -> None:
    """Main scanning function with token budget management."""
    current_tokens = 0
    output_buffer = []
    
    # Statistics
    stats = {
        'total_files_scanned': 0,
        'included_files': 0,
        'binary_files_skipped': 0,
        'autogen_files_skipped': 0,
        'trivial_files_skipped': 0,
        'gitignored_files_skipped': 0,
        'files_skipped_due_to_token_limit': 0,
        'files_content_truncated': 0,
        'files_content_fully_included': 0,
        'total_original_size': 0,
        'final_output_size': 0,
        'estimated_total_tokens': 0
    }
    
    # Analyze codebase first
    print("Analyzing codebase structure...")
    codebase_analysis = analyze_codebase(start_path, exclusion_spec)
    
    # Generate header summary
    header_summary = "AI-Optimized Codebase Summary:\n" + "=" * 30 + "\n"
    header_summary += f"Token Budget: {TOKEN_BUDGET:,} tokens\n"
    header_summary += f"Estimation: ~{CHARS_PER_TOKEN} characters per token\n\n"
    header_summary += f"Project Root: {os.path.abspath(start_path)}\n"
    header_summary += f"Project Type: {codebase_analysis['project_type']}\n"
    header_summary += f"Primary Language: {codebase_analysis['primary_language'] or 'Not determined'}\n"
    
    if codebase_analysis['frameworks']:
        header_summary += f"Frameworks/Tools: {', '.join(codebase_analysis['frameworks'][:10])}\n"
    
    header_summary += f"Total Files (pre-filter): {codebase_analysis['total_files']}\n"
    
    if codebase_analysis['test_directories']:
        header_summary += f"Test Directories: {', '.join(codebase_analysis['test_directories'])}\n"
    if codebase_analysis['build_files']:
        header_summary += f"Build Files: {', '.join(codebase_analysis['build_files'])}\n"
    
    header_summary += "\nKey Processing Notes:\n"
    header_summary += f"- Target token budget: {TOKEN_BUDGET:,}\n"
    header_summary += "- Files are intelligently truncated if large\n"
    header_summary += "- Binary, auto-generated, and trivial files are excluded\n"
    header_summary += "- Lock files are summarized\n"
    header_summary += "- Important config files are prioritized\n\n"
    
    header_tokens = estimate_tokens(header_summary)
    if current_tokens + header_tokens <= TOKEN_BUDGET:
        output_buffer.append(header_summary)
        current_tokens += header_tokens
    else:
        print("Warning: Token budget too small for header summary.")
    
    # Directory structure
    if current_tokens < TOKEN_BUDGET:
        dir_header = "Directory Structure:\n" + "-" * 20 + "\n"
        print("Generating directory structure...")
        dir_structure = print_directory_structure(start_path, exclusion_spec, max_depth=3)
        
        dir_tokens = estimate_tokens(dir_header + dir_structure + "\n\n")
        if current_tokens + dir_tokens <= TOKEN_BUDGET:
            output_buffer.append(dir_header)
            output_buffer.append(dir_structure)
            output_buffer.append("\n\n")
            current_tokens += dir_tokens
        else:
            skip_msg = "[Directory structure omitted due to token budget]\n\n"
            if current_tokens + estimate_tokens(skip_msg) <= TOKEN_BUDGET:
                output_buffer.append(skip_msg)
                current_tokens += estimate_tokens(skip_msg)
    
    # File contents header
    file_header = "File Contents:\n" + "-" * 15 + "\n"
    file_header_tokens = estimate_tokens(file_header)
    if current_tokens + file_header_tokens <= TOKEN_BUDGET:
        output_buffer.append(file_header)
        current_tokens += file_header_tokens
    
    # Collect and prioritize file candidates
    print("Collecting files...")
    file_candidates = []
    
    for root, dirs, files in os.walk(start_path, topdown=True):
        # Filter directories based on exclusion spec
        rel_root_path = os.path.relpath(root, start_path)
        if exclusion_spec and rel_root_path != '.':
            dirs[:] = [d for d in dirs if not exclusion_spec.match_file(
                os.path.join(rel_root_path, d).replace(os.sep, '/')
            )]
        
        for file_name in files:
            stats['total_files_scanned'] += 1
            file_abs_path = os.path.join(root, file_name)
            file_rel_path = os.path.relpath(file_abs_path, start_path)
            
            # Use forward slashes for pathspec
            file_rel_path_normalized = file_rel_path.replace(os.sep, '/')
            
            file_info = get_file_info(file_abs_path)
            stats['total_original_size'] += file_info['size']
            
            # Check if file should be skipped
            skip_reason = should_skip_file(file_rel_path_normalized, file_abs_path, file_info, exclusion_spec)
            if skip_reason:
                if "gitignore" in skip_reason:
                    stats['gitignored_files_skipped'] += 1
                elif "Binary" in skip_reason:
                    stats['binary_files_skipped'] += 1
                elif "Auto-generated" in skip_reason:
                    stats['autogen_files_skipped'] += 1
                elif "Trivial" in skip_reason:
                    stats['trivial_files_skipped'] += 1
                continue
            
            # Apply file type filter
            if file_types_filter and not any(file_name.endswith(ext) for ext in file_types_filter):
                continue
            
            # Calculate priority (lower number = higher priority)
            priority = 0
            if file_info['is_important']:
                priority = -100
            elif file_info['should_summarize']:
                priority = -50
            elif file_rel_path.startswith('test') or 'test' in file_rel_path:
                priority = 50
            elif file_rel_path.startswith('doc') or 'doc' in file_rel_path:
                priority = 60
            
            # Adjust priority based on file extension
            _, ext = os.path.splitext(file_name)
            if ext in ['.md', '.rst', '.txt']:
                priority -= 10
            elif ext in ['.json', '.yml', '.yaml', '.toml', '.ini']:
                priority -= 5
                
            file_candidates.append({
                'abs_path': file_abs_path,
                'rel_path': file_rel_path,
                'info': file_info,
                'priority': priority
            })
    
    # Sort candidates by priority
    file_candidates.sort(key=lambda x: (x['priority'], x['rel_path']))
    
    # Process files within token budget
    print(f"Processing {len(file_candidates)} candidate files...")
    for i, candidate in enumerate(file_candidates):
        if current_tokens >= TOKEN_BUDGET * 0.95:  # Leave 5% buffer
            stats['files_skipped_due_to_token_limit'] += 1
            print(f"Skipping remaining files due to token budget ({i}/{len(file_candidates)} processed)")
            break
        
        file_abs_path = candidate['abs_path']
        file_rel_path = candidate['rel_path']
        file_info = candidate['info']
        
        file_entry_header = f"File: {file_rel_path} ({file_info['size_str']})\n"
        file_entry_header += "-" * 50 + "\n"
        
        try:
            with open(file_abs_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Process content
            was_truncated = False
            if file_info['should_summarize']:
                processed_content = summarize_lock_file(content, os.path.basename(file_rel_path))
            else:
                processed_content, was_truncated = truncate_content(
                    content, file_rel_path, file_info['is_important']
                )
            
            if was_truncated:
                stats['files_content_truncated'] += 1
            else:
                stats['files_content_fully_included'] += 1
            
            # Calculate tokens for this entry
            entry_content = f"{file_entry_header}Content of {file_rel_path}:\n{processed_content}\n\n"
            entry_tokens = estimate_tokens(entry_content)
            
            # Check if it fits in budget
            if current_tokens + entry_tokens <= TOKEN_BUDGET * 0.95:
                output_buffer.append(entry_content)
                current_tokens += entry_tokens
                stats['included_files'] += 1
                stats['final_output_size'] += len(processed_content)
                
                if (i + 1) % 50 == 0:  # Progress indicator
                    print(f"Processed {i + 1}/{len(file_candidates)} files ({current_tokens:,} tokens used)")
            else:
                # Try to include just a skip marker
                skip_marker = f"{file_entry_header}[Content skipped due to token budget - {entry_tokens:,} tokens required]\n\n"
                marker_tokens = estimate_tokens(skip_marker)
                
                if current_tokens + marker_tokens <= TOKEN_BUDGET:
                    output_buffer.append(skip_marker)
                    current_tokens += marker_tokens
                    stats['files_skipped_due_to_token_limit'] += 1
                else:
                    stats['files_skipped_due_to_token_limit'] += 1
                    
        except Exception as e:
            print(f"Error reading {file_rel_path}: {e}")
            error_msg = f"{file_entry_header}[Error reading file: {e}]\n\n"
            error_tokens = estimate_tokens(error_msg)
            
            if current_tokens + error_tokens <= TOKEN_BUDGET:
                output_buffer.append(error_msg)
                current_tokens += error_tokens
    
    # Add statistics summary
    stats['estimated_total_tokens'] = current_tokens
    
    summary_lines = [
        "\n" + "=" * 50 + "\n",
        "Processing Statistics:\n",
        "-" * 20 + "\n",
        f"Total files scanned: {stats['total_files_scanned']}\n",
        f"Files included: {stats['included_files']}\n",
        f"Binary files skipped: {stats['binary_files_skipped']}\n",
        f"Auto-generated files skipped: {stats['autogen_files_skipped']}\n",
        f"Trivial files skipped: {stats['trivial_files_skipped']}\n",
        f"Gitignored files skipped: {stats['gitignored_files_skipped']}\n",
        f"Files skipped (token limit): {stats['files_skipped_due_to_token_limit']}\n",
        f"Files truncated: {stats['files_content_truncated']}\n",
        f"Files fully included: {stats['files_content_fully_included']}\n",
        f"Total original size: {format_file_size(stats['total_original_size'])}\n",
        f"Final output size: {format_file_size(stats['final_output_size'])}\n",
        f"Estimated tokens: {stats['estimated_total_tokens']:,} / {TOKEN_BUDGET:,}\n",
        f"Token utilization: {stats['estimated_total_tokens'] / TOKEN_BUDGET * 100:.1f}%\n"
    ]
    
    summary_text = ''.join(summary_lines)
    summary_tokens = estimate_tokens(summary_text)
    
    if current_tokens + summary_tokens <= TOKEN_BUDGET:
        output_buffer.append(summary_text)
    else:
        # Add minimal token count
        final_msg = f"\nFinal tokens: {stats['estimated_total_tokens']:,} / {TOKEN_BUDGET:,}\n"
        if current_tokens + estimate_tokens(final_msg) <= TOKEN_BUDGET:
            output_buffer.append(final_msg)
    
    # Write output
    final_output = ''.join(output_buffer)
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(final_output)
    
    print(f"\nScan complete. Results written to {output_file_path}")
    print(f"Final token count: {stats['estimated_total_tokens']:,} / {TOKEN_BUDGET:,} ({stats['estimated_total_tokens'] / TOKEN_BUDGET * 100:.1f}%)")
    print(f"Files included: {stats['included_files']} / {stats['total_files_scanned']} scanned")

def main(args: List[str]) -> None:
    """Main entry point."""
    if len(args) < 3:
        print("Usage: python script.py <start_path> <output_file> [custom_exclusion_file] [file_extensions...]")
        print("Examples:")
        print("  python dump_token_aware.py ./my_project output.txt")
        print("  python dump_token_aware.py ./my_project output.txt .gitignore")
        print("  python dump_token_aware.py ./my_project output.txt .gitignore .py .js .jsx")
        sys.exit(1)

    start_path = args[1]
    output_file = args[2]
    custom_exclusion_file = None
    file_types = None

    # Parse optional arguments
    arg_index = 3
    if len(args) > arg_index:
        # Check if it's a file path (contains path separator or exists as file)
        potential_file = args[arg_index]
        if (os.path.sep in potential_file or 
            '.' in os.path.basename(potential_file) and 
            (os.path.exists(potential_file) or os.path.exists(os.path.join(start_path, potential_file)))):
            custom_exclusion_file = potential_file
            arg_index += 1
    
    if len(args) > arg_index:
        file_types = args[arg_index:]
        # Ensure file extensions start with dot
        file_types = [ext if ext.startswith('.') else f'.{ext}' for ext in file_types]

    # Resolve paths
    abs_start_path = os.path.abspath(start_path)
    
    if not os.path.exists(abs_start_path):
        print(f"Error: Start path does not exist: {abs_start_path}")
        sys.exit(1)
    
    # Load exclusion patterns
    print("Loading exclusion patterns...")
    exclusion_spec = load_exclusion_patterns(abs_start_path, custom_exclusion_file)
    
    if not exclusion_spec.patterns:
        print("No exclusion patterns loaded.")
    
    if file_types:
        print(f"Filtering for file types: {file_types}")
    else:
        print("No specific file types specified.")
    
    print(f"Starting scan of: {abs_start_path}")
    print(f"Output will be written to: {output_file}")
    print(f"Token budget: {TOKEN_BUDGET:,}")
    print()
    
    scan_folder(abs_start_path, file_types, output_file, exclusion_spec)

if __name__ == "__main__":
    main(sys.argv)