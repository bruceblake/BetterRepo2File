# BetterRepo2File v2.0 "RobustRepo" (Vibe Coder)

An advanced, scalable web-based workflow for AI-assisted software development using Gemini for planning and Claude for implementation. Version 2.0 introduces distributed processing with Celery, Redis-backed sessions, and MinIO object storage for enhanced scalability and robustness.

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/yourusername/BetterRepo2File.git
cd BetterRepo2File
./run.sh

# Open in browser
# Navigate to http://localhost:5000
# Start building with AI assistance!
```

## Table of Contents

- [Features](#-features)
  - [Core Workflow](#core-workflow)
  - [Advanced Capabilities](#advanced-capabilities)
  - [Technical Features](#technical-features)
- [Installation](#installation)
- [Usage](#usage)
  - [Vibe Coder Workflow](#vibe-coder-workflow-recommended)
  - [Direct Repository Processing](#direct-repository-processing)
- [API Usage](#api-usage)
- [Configuration Profiles](#configuration-profiles)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Testing](#testing)
- [Environment Variables](#environment-variables)
- [Model Context Windows](#model-context-windows)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

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

### v2.0 "RobustRepo" Features
- **Distributed Processing**: Celery task queue for scalable job processing
- **Redis Session Management**: Fast, reliable session storage
- **MinIO Object Storage**: Scalable file storage for distributed workers
- **Enhanced Monitoring**: Celery Flower for task monitoring
- **Improved Reliability**: Automatic retries and error recovery
- **Better Resource Management**: Separate workers from web application
- **OpenTelemetry Ready**: Infrastructure for distributed tracing (Phase 6)
- **Production Ready**: Docker Compose deployment with health checks

## Installation

### Option 1: Docker (Recommended for v2.0)

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/BetterRepo2File.git
   cd BetterRepo2File
   ```

2. Start the services with Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. Access the application at http://localhost:5000

4. View service UIs:
   - MinIO Console: http://localhost:9001 (minioadmin/minioadmin)
   - Flower (Celery monitoring): http://localhost:5555

### Option 2: Local Development

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/BetterRepo2File.git
   cd BetterRepo2File
   ```

2. Install Redis and MinIO locally:
   ```bash
   # For Ubuntu/Debian
   sudo apt-get install redis-server
   
   # Download MinIO
   wget https://dl.min.io/server/minio/release/linux-amd64/minio
   chmod +x minio
   ./minio server /data --console-address ":9001"
   ```

3. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
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

### Vibe Coder Workflow (Recommended)

1. **Setup Your Project** (Stage A - Gemini Planning):
   - Enter your GitHub repository URL
   - Describe what you want to build in natural language
   - Click "Generate Context" to create input for Gemini
   - Copy the generated context and paste into Gemini
   - Get a detailed implementation plan from Gemini

2. **Implementation** (Stage B - Claude Coding):
   - Paste Gemini's plan back into the application
   - Click "Generate Coder Context" to create input for Claude
   - Copy the context and paste into Claude
   - Implement the feature with Claude's assistance
   - Commit your changes to git

3. **Testing & Iteration** (Stages C & D):
   - Run tests to verify your implementation
   - If tests fail or changes are needed, click "Start Iteration"
   - Describe what needs fixing
   - Get an updated plan from Gemini (Stage C)
   - Implement fixes with Claude (Stage D)
   - Repeat until tests pass and feature is complete

### Direct Repository Processing

1. **GitHub Repository**:
   - Enter a GitHub repository URL
   - Select the branch to process
   - Choose processing mode (Ultra recommended)
   - Click "Generate" to process
   - View, download, or copy the output

2. **Local Files**:
   - Drag and drop files/folders onto the upload area
   - Select file types to include
   - Choose processing mode
   - Click "Generate" to process

## API Usage

The application includes a REST API for programmatic access:

```bash
# Process a GitHub repository with Vibe Coder workflow
curl -X POST http://localhost:5000/api/generate_context \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/user/repo",
    "repo_branch": "main",
    "vibe": "Add dark mode toggle to settings page",
    "stage": "A"
  }'

# Process with specific model and settings
curl -X POST http://localhost:5000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "ultra",
    "github_url": "https://github.com/user/repo",
    "options": {
      "model": "gemini-1.5-pro",
      "token_budget": null,  # Auto-detects based on model
      "github_branch": "develop"
    }
  }'

# List available modes
curl http://localhost:5000/api/v1/modes

# List configuration profiles
curl http://localhost:5000/api/profiles/
```

## Configuration Profiles

The application includes intelligent profiles that automatically select the best model for each task:

### Vibe Coder Profiles
- **vibe_coder_gemini**: Planning stages (A, C) with Gemini 1.5 Pro
  - 2M token context window
  - Automatically uses 1M tokens (50% of capacity)
  - Optimized for understanding large codebases
  - Includes git insights and semantic analysis

- **vibe_coder_claude**: Coding stages (B, D) with Claude 3 Sonnet  
  - 200k token context window
  - Automatically uses 100k tokens (50% of capacity)
  - Optimized for code generation and implementation
  - Focused on practical coding tasks

### Standard Profiles
- **Frontend**: React, Vue, Angular projects
- **Backend**: Python, Node.js, Java development
- **Data Science**: Jupyter notebooks and ML projects
- **Documentation**: Markdown and technical writing
- **Mobile**: React Native and Flutter apps
- **Microservices**: Multi-service architectures

## Architecture

This application consists of:

- **Frontend**: Modern web interface with:
  - Real-time progress tracking
  - Model-specific indicators
  - Workflow visualization
  - Interactive test results

- **Backend**: Flask server with:
  - Intelligent model selection
  - Token budget management
  - Git integration
  - Error recovery
  - Session management

- **Processing Engines**:
  - **Standard**: Basic file consolidation
  - **Smart**: AI-optimized filtering
  - **Token-Aware**: Budget-aware processing
  - **Ultra**: Advanced semantic analysis with:
    - Model-specific token counting
    - AST-based code analysis
    - Priority-based file selection
    - Intelligent truncation strategies

- **Model Integration**:
  - Automatic model selection based on task
  - Token budget auto-adjustment
  - Context window optimization
  - Multi-model support (GPT-4, Claude, Gemini, Llama)

## Requirements

- Python 3.8+
- Git (for cloning repositories)  
- Web browser with JavaScript enabled
- (Optional) API keys for:
  - OpenAI (GPT models)
  - Anthropic (Claude models)
  - Google AI (Gemini models)

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
python -m pytest tests/ -v

# JavaScript tests
cd tests && npm install && npm test

# Run specific test suites
python -m pytest test_vibe_features.py -v
python -m pytest test_gemini_features.py -v
```

### Test Detection

The application automatically detects and runs tests for your project:
- Python: pytest, unittest
- JavaScript: Jest, Mocha
- Go: go test
- Java: Maven, Gradle

## Environment Variables

You can configure API keys and settings through environment variables:

```bash
# AI Model API Keys (optional)
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"  
export GEMINI_API_KEY="your-gemini-key"

# Application Settings
export FLASK_PORT=5000
export FLASK_DEBUG=false
export MAX_UPLOAD_SIZE=52428800  # 50MB
```

## Model Context Windows

The application intelligently manages token budgets based on each model's capabilities:

| Model | Max Context | Default Budget | Use Case |
|-------|-------------|----------------|----------|
| Gemini 1.5 Pro | 2,000,000 | 1,000,000 | Planning & Analysis |
| Claude 3 Sonnet | 200,000 | 100,000 | Code Implementation |
| GPT-4 | 128,000 | 64,000 | General Purpose |
| GPT-3.5 Turbo | 16,385 | 8,192 | Quick Tasks |

## Troubleshooting

### Common Issues

1. **"Broken pipe" error during context generation**:
   - This typically occurs with large repositories
   - Solution: The app now uses improved subprocess handling to prevent this

2. **Token budget exceeded**:
   - The application automatically adjusts budgets based on model
   - If still occurring, try using a model with larger context window

3. **Git operations failing**:
   - Ensure git is installed and accessible in PATH
   - Check repository permissions for private repos
   - Verify branch names are correct

4. **Memory errors with large repos**:
   - Use the Ultra processing mode for better memory management
   - Consider increasing system swap space
   - Process specific subdirectories instead of entire repo

### Getting Help

- Check the [Issues](https://github.com/yourusername/BetterRepo2File/issues) page
- Review [detailed documentation](docs/)
- Contact support through GitHub discussions

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

[MIT License](LICENSE)

## Acknowledgments

- Built on the [repo2file](https://github.com/artkulak/repo2file) core by [artkulak](https://github.com/artkulak)
- Uses [tiktoken](https://github.com/openai/tiktoken) for accurate token counting
- Integrates with leading AI models from OpenAI, Anthropic, and Google
- Special thanks to all contributors and users who provided feedback