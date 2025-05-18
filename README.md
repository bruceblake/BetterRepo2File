# BetterRepo2File (Vibe Coder)

An advanced web-based workflow for AI-assisted software development using Gemini for planning and Claude for implementation. This tool consolidates repository contents into optimized contexts for Large Language Models (LLMs), providing a structured workflow from idea to implementation.

## 🚀 Features

### Core Workflow
- **Vibe Coder Workflow**: A structured approach to AI development:
  - **Stage A**: Initial planning with Gemini 1.5 Pro (2M context window)
  - **Stage B**: Implementation with Claude 3 Sonnet (200k context window)
  - **Stage C**: Iteration planning with Gemini based on test results and feedback
  - **Stage D**: Iteration implementation with Claude for fixes and improvements

### Advanced Capabilities
- **Smart Model Selection**: Automatically uses the right LLM for each task
  - Gemini 1.5 Pro for planning (utilizing massive 2M token context)
  - Claude 3 Sonnet for coding (optimized for implementation tasks)
- **Token Management**: 
  - Automatic budget adjustment based on model capabilities
  - Uses 50% of model's context window for safety
  - Model-specific token counting with tiktoken
- **Git Integration**:
  - Colored diff output for better visibility
  - Automatic test detection and execution
  - Commit history tracking
  - Function-level change analysis
- **Multiple Processing Modes**:
  - **Standard Mode**: Basic file consolidation
  - **Smart Mode**: AI-optimized with intelligent filtering
  - **Token-Aware Mode**: Budget-aware token management
  - **Ultra Mode**: Advanced with exact token counting and semantic analysis

### Technical Features
- Drag and drop files or folders
- Process GitHub repositories via URL with branch selection
- Customizable file type filtering with profile-based defaults
- Real-time progress tracking and logging
- Binary file detection and exclusion
- Lock file summarization
- Priority-based file inclusion
- Configuration profiles for different project types
- REST API for programmatic access
- Semantic code analysis with AST parsing
- Parallel file processing with worker threads
- Comprehensive error handling and recovery

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/BetterRepo2File.git
   cd BetterRepo2File
   ```

2. Create a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app/app.py
   # OR use the run script:
   ./run.sh
   ```

5. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

### File Upload
1. Drag and drop files/folders onto the designated area or click "Choose Files"
2. Optionally specify file types to include (e.g., `.py .js .tsx`)
3. Click "Generate" to process
4. View, download, or copy the consolidated output

### GitHub Repository
1. Switch to the "GitHub URL" tab
2. Enter a GitHub repository URL (e.g., `https://github.com/username/repo`)
3. Optionally specify a branch (leave empty for default branch)
4. Optionally specify file types to include
5. Click "Generate" to process
6. View, download, or copy the consolidated output

## API Usage

The application includes a REST API for programmatic access:

```bash
# Process a GitHub repository
curl -X POST http://localhost:5000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "ultra",
    "github_url": "https://github.com/user/repo",
    "options": {
      "model": "gpt-4",
      "token_budget": 500000,
      "github_branch": "develop"
    }
  }'

# List available modes
curl http://localhost:5000/api/v1/modes

# List configuration profiles
curl http://localhost:5000/api/profiles/
```

## Configuration Profiles

The application includes pre-configured profiles for common use cases:

- **Frontend**: Optimized for React, Vue, Angular projects
- **Backend**: Python, Node.js, Java backend development
- **Data Science**: Jupyter notebooks and ML projects
- **Documentation**: Markdown and technical writing
- **Mobile**: React Native and Flutter apps
- **Microservices**: Multi-service architectures
- **Gemini**: Optimized for Gemini 1.5 Pro with:
  - 1M token budget for large context windows
  - Hierarchical manifest generation for easy navigation
  - Advanced truncation strategies (middle summarization)
  - Business logic prioritization
  - Automatic ultra mode configuration

## Architecture

This application consists of:

- **Frontend**: HTML, CSS, and JavaScript for the user interface
- **Backend**: Flask web server that:
  - Handles file uploads and GitHub repository cloning
  - Processes inputs using multiple repo2file variants
  - Provides REST API endpoints
  - Manages configuration profiles
- **repo2file Processors**:
  - Standard: Basic file consolidation
  - Smart: AI-optimized filtering
  - Token-Aware: 500K token budget management
  - Ultra: Advanced with exact tokens and semantic analysis

## Requirements

- Python 3.7+
- Git (for cloning repositories)
- Web browser with JavaScript enabled

## Testing

### Running Tests with Docker

The project includes a comprehensive test suite that can be run using Docker:

```bash
# Run all tests
docker-compose --profile test up --build

# Run tests with coverage reports
docker-compose run --rm test

# View coverage reports
open test_results/python_coverage/index.html
open test_results/js_coverage/index.html
```

For detailed testing instructions, see [DOCKER_TESTING.md](DOCKER_TESTING.md).

### Local Testing

You can also run tests locally:

```bash
# Python tests
python -m pytest tests/test_app.py -v
python -m pytest tests/test_repo2file.py -v

# JavaScript tests
cd tests && npm install && npm test
```

## License

[MIT License](LICENSE)

## Acknowledgments

This project uses the [repo2file](https://github.com/artkulak/repo2file) tool by [artkulak](https://github.com/artkulak) for file consolidation processing.