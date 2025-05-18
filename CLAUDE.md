# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Setup and Run
```bash
# Install dependencies in a virtual environment
./run.sh

# OR manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app/app.py
```

### Run Application
```bash
# If venv is already set up
source venv/bin/activate
python app/app.py
```

### Use repo2file directly
```bash
# Standard version
python repo2file/dump.py <start_path> <output_file> [exclusion_file] [file_extensions...]

# Smart AI-optimized version
python repo2file/dump_smart.py <start_path> <output_file> [exclusion_file] [file_extensions...]

# Token-aware version (500K token budget)
python repo2file/dump_token_aware.py <start_path> <output_file> [exclusion_file] [file_extensions...]

# Ultra version (most advanced)
python repo2file/dump_ultra.py <repo_path> <output_file> [options]
```

Examples:
```bash
# Standard processing
python repo2file/dump.py ./my_repo output.txt repo2file/exclude.txt .py .js .html

# Smart processing (with AI optimizations)
python repo2file/dump_smart.py ./my_repo output_smart.txt .gitignore .py .js .tsx

# Token-aware processing (500K token budget)
python repo2file/dump_token_aware.py ./my_repo output_token.txt .gitignore .py .js .tsx

# Ultra processing (exact token counting, semantic analysis)
python repo2file/dump_ultra.py ./my_repo output_ultra.txt --model gpt-4 --budget 500000
```

### REST API Usage
```bash
# Health check
curl http://localhost:5000/api/v1/health

# List available modes
curl http://localhost:5000/api/v1/modes

# Process a GitHub repo
curl -X POST http://localhost:5000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "ultra",
    "github_url": "https://github.com/user/repo",
    "options": {
      "model": "gpt-4",
      "token_budget": 500000
    }
  }'

# List profiles
curl http://localhost:5000/api/profiles/

# Get specific profile
curl http://localhost:5000/api/profiles/frontend
```

## Project Architecture

BetterRepo2File is a web-based UI for the repo2file tool that consolidates repository contents into a single text file for easier use with Large Language Models.

### Core Components

1. **Flask Web Application** (`app/app.py`)
   - Provides web UI and REST API endpoints
   - Handles file uploads and GitHub repository cloning
   - Uses repo2file as a subprocess to process files
   - Manages temporary files and cleanup operations
   - Supports both standard and smart processing modes

2. **repo2file Tool** 
   - **Standard version** (`repo2file/dump.py`): Basic file consolidation
   - **Smart version** (`repo2file/dump_smart.py`): AI-optimized with:
     - Automatic binary file detection and exclusion
     - Intelligent file truncation (preserves code structure)
     - Auto-generated file filtering
     - Lock file summarization
     - Codebase analysis and summary
     - File size management for optimal LLM processing
   - **Token-aware version** (`repo2file/dump_token_aware.py`): Ultra-optimized with:
     - 500K token budget management
     - Robust pathspec-based .gitignore pattern matching
     - Priority-based file inclusion
     - Detailed token usage statistics
     - Automatic content truncation to fit budget
     - Enhanced file type detection and categorization
   - **Ultra version** (`repo2file/dump_ultra.py`): Most advanced features:
     - Exact token counting using tiktoken
     - Semantic code analysis with AST parsing
     - Multi-model support (GPT-4, GPT-3.5, Claude, Llama)
     - Caching system for performance
     - Parallel file processing
     - Advanced truncation strategies
     - Comprehensive codebase analysis

3. **Frontend** (`app/templates/index.html`, `app/static/js/script.js`, `app/static/css/styles.css`)
   - Provides drag-and-drop file upload interface
   - Supports GitHub repository URL input
   - Offers file type filtering
   - Displays and allows downloading/copying of processed output
   - Options for .gitignore usage and multiple processing modes
   - Profile-based configuration system
   - Real-time preview capability
   - Ultra mode with model and token budget selection

4. **REST API** (`app/api.py`)
   - RESTful endpoints for programmatic access
   - Support for all processing modes
   - Health check and mode information endpoints
   - Process files or GitHub repos via API

5. **Configuration Profiles** (`app/profiles.py`)
   - Pre-configured profiles for common use cases
   - Custom profile creation and management
   - Profile-based processing optimization
   - Default profiles for frontend, backend, data science, etc.

6. **Supporting Modules**
   - `token_manager.py`: Advanced token counting and allocation
   - `code_analyzer.py`: Semantic code analysis using AST
   - Built-in caching system for performance

### Data Flow

1. User inputs files/folders or GitHub URL via web interface
2. Flask backend processes the input:
   - For file uploads: saves files to temporary directory
   - For GitHub URLs: clones repository to temporary directory
3. Flask calls repo2file script on the input directory
4. repo2file generates a single text file containing:
   - Directory structure visualization
   - Contents of all files (respecting exclusions and type filters)
5. Backend returns the processed content to the frontend
6. User can view, download, or copy the output
7. Temporary files are cleaned up periodically or on page close

### Security Considerations

- Temporary directories are created with unique UUIDs
- Operation IDs are validated to prevent directory traversal
- File uploads are limited to 50MB
- Temporary files are cleaned up after 1 hour
- Filenames are sanitized using werkzeug's secure_filename

### Key Features for AI/LLM Optimization

1. **Smart Mode Features**:
   - Automatic detection and exclusion of binary files
   - Intelligent truncation of large files (preserves first/last 50 lines for code)
   - Auto-generated and minified file filtering
   - Lock file summarization instead of full content
   - Preservation of important config files
   - AI-focused codebase summary at the beginning of output

2. **Customization Options**:
   - Toggle between .gitignore and default exclusion patterns
   - Choose between standard and smart processing modes
   - Specify file types to include
   - All options default to AI-optimized settings

The smart mode is specifically designed to reduce output size while maintaining the key information that AI/LLM agents need to understand and work with codebases effectively.