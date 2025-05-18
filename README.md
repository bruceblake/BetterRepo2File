# Repo2File UI

A web-based user interface for the [repo2file](https://github.com/artkulak/repo2file) tool, which consolidates repository contents or local files into a single text file for use with Large Language Models (LLMs).

## Features

- Drag and drop files or folders
- Process GitHub repositories via URL
- Customizable file type filtering
- Preview consolidated output in the browser
- Download the output as a text file
- Copy the output to clipboard
- Multiple processing modes:
  - **Standard Mode**: Basic file consolidation
  - **Smart Mode**: AI-optimized with intelligent filtering and truncation
  - **Token-Aware Mode**: Ultra-optimized with 500K token budget management
  - **Ultra Mode**: Most advanced with exact token counting and semantic analysis
- Automatic .gitignore pattern matching using pathspec
- Binary file detection and exclusion
- Lock file summarization
- Priority-based file inclusion within token limits
- Configuration profiles for common use cases
- REST API for programmatic access
- Real-time preview capability
- Multi-model support (GPT-4, GPT-3.5, Claude, Llama, Gemini 1.5 Pro)
- Caching system for improved performance
- Semantic code analysis with AST parsing
- Parallel file processing
- **Gemini 1.5 Pro Support**: Optimized profile with 1M token budget for large context windows ([detailed documentation](docs/GEMINI_FEATURES.md))

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/BetterRepo2File.git
   cd BetterRepo2File
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python app/app.py
   ```

4. Open your browser and navigate to:
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