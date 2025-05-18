# Gemini 1.5 Pro Support Documentation

## Overview

BetterRepo2File now includes comprehensive support for Gemini 1.5 Pro, Google's large context window model. The Gemini profile is specifically optimized to take advantage of Gemini 1.5 Pro's 1 million token context window, providing enhanced features for processing large codebases.

## Features

### 1. Large Token Budget (1M Tokens)

The Gemini profile is configured with a 1 million token budget by default, allowing you to process significantly larger repositories without truncation.

### 2. Hierarchical Manifest Generation

When using the Gemini profile, a detailed hierarchical manifest is automatically generated, including:

- Project overview with type, language, and frameworks detected
- Navigation guide for easy browsing
- Directory-based organization with estimated token locations
- File importance scoring
- Module/directory purpose detection

### 3. Advanced Truncation Strategies

The profile uses the `middle_summarize` truncation strategy, which:

- Preserves the beginning and end of files (most important parts)
- Intelligently summarizes middle sections when needed
- Prioritizes business logic and critical code sections

### 4. Business Logic Prioritization

The semantic analyzer identifies and prioritizes:

- Revenue-related code
- Financial calculations
- Core business logic
- Critical algorithms
- Main entry points

### 5. Automatic Configuration

When selecting the Gemini profile:

- Ultra mode is automatically enabled
- Token budget is set to 1,000,000
- Model is set to `gemini-1.5-pro`
- Manifest generation is enabled
- Advanced truncation is configured

## Usage

### Web Interface

1. Select "Gemini 1.5 Pro (Large Context)" from the profile dropdown
2. The interface will automatically configure:
   - Ultra mode: ON
   - Model: gemini-1.5-pro
   - Token budget: 1,000,000
3. Process your repository as usual

### Command Line

```bash
# Using the Gemini profile
python repo2file/dump_ultra.py /path/to/repo output.txt --profile gemini

# Equivalent manual configuration
python repo2file/dump_ultra.py /path/to/repo output.txt \
  --ultra \
  --model gemini-1.5-pro \
  --token-budget 1000000 \
  --truncation-strategy middle_summarize \
  --include-manifest

# Process a specific branch
python repo2file/dump_ultra.py /path/to/repo output.txt --profile gemini --git-insights
```

### API

```python
# Using the REST API
curl -X POST http://localhost:5000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{
    "profile": "gemini",
    "github_url": "https://github.com/user/repo",
    "options": {
      "github_branch": "develop"
    }
  }'

# Or with explicit options
curl -X POST http://localhost:5000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "ultra",
    "model": "gemini-1.5-pro",
    "token_budget": 1000000,
    "truncation_strategy": "middle_summarize",
    "include_manifest": true,
    "github_url": "https://github.com/user/repo"
  }'
```

## Example Output Structure

When using the Gemini profile, the output follows this structure:

```markdown
# Repository Analysis Report
==================================================

Repository: YourProject
Generated: 2025-05-18 08:55:55
Processing Model: gemini-1.5-pro
Token Budget: 1,000,000

## Project Overview
Type: Python Web Application
Primary Language: python
Total Files: 150
Total Size: 2.5 MB

# Project Manifest

## Table of Contents

### Project Overview
- **Type**: python Project
- **Primary Language**: python
- **Key Frameworks**: Django, React
- **Total Files**: 150

### Navigation Guide

Each section below contains:
- Module/directory purpose (when detectable)
- Key files with their main exports/classes
- Estimated token location in the output

---

### Root
*Project root directory*

- **README.md** - Project documentation [Token offset: 1,000]
- **setup.py** - Package configuration [Token offset: 2,500]
...

### src/api
*REST API endpoints*

- **src/api/views.py** - API view controllers [Token offset: 10,000]
  - Classes: UserView, ProductView, OrderView
  - Functions: authenticate, validate_request
...

[File contents follow the manifest]
```

## Configuration Details

The Gemini profile (`app/profiles.py`) includes:

```python
'gemini': ProcessingProfile(
    name='gemini',
    description='Optimized for Gemini 1.5 Pro with large context window',
    mode='ultra',
    model='gemini-1.5-pro',
    token_budget=1000000,
    truncation_strategy='middle_summarize',
    generate_manifest=True,
    semantic_analysis=True,
    prioritize_business_logic=True,
    include_dependencies=True,
    smart_chunking=True,
    preserve_structure=True
)
```

## Advanced Features

### Semantic Analysis

The Gemini profile uses advanced semantic analysis to:

- Extract classes, functions, and their relationships
- Calculate file importance scores
- Detect business logic patterns
- Identify critical code paths

### Smart Chunking

Files are chunked intelligently to:

- Preserve function and class boundaries
- Keep related code together
- Maintain context for better understanding

### Cache Optimization

The caching system is profile-aware, meaning:

- Different profiles maintain separate caches
- Cache invalidation considers profile settings
- Improved performance for repeated processing

## Best Practices

1. **Use for Large Codebases**: The Gemini profile excels with large repositories that would exceed normal token limits

2. **Review the Manifest**: The hierarchical manifest provides an excellent overview - use it to navigate the output efficiently

3. **Business Logic Focus**: If your codebase has critical business logic, the Gemini profile will prioritize it automatically

4. **Token Monitoring**: Even with 1M tokens, monitor usage for extremely large repositories

5. **API Integration**: Use the profile parameter in API calls for consistent configuration

## Troubleshooting

### Token Limit Exceeded

Even with 1M tokens, very large repositories might exceed limits. Consider:

- Using more specific file filters
- Excluding test directories
- Focusing on specific modules

### Performance Issues

For optimal performance:

- Enable caching (default)
- Use parallel processing (default in ultra mode)
- Consider excluding large generated files

### Manifest Not Generated

Ensure:

- Ultra mode is enabled (automatic with Gemini profile)
- Sufficient files are processed
- No errors during semantic analysis

## Future Enhancements

Planned improvements for Gemini support:

1. Dynamic token budget adjustment based on repository size
2. Multi-stage processing for extremely large codebases
3. Enhanced business logic detection patterns
4. Integration with Gemini's code understanding capabilities
5. Custom manifest templates

## API Reference

### Profile Endpoints

```bash
# Get Gemini profile details
curl http://localhost:5000/api/profiles/gemini

# List all profiles
curl http://localhost:5000/api/profiles
```

### Processing Options

All standard processing options are supported, with these defaults for Gemini:

- `mode`: "ultra"
- `model`: "gemini-1.5-pro"
- `token_budget`: 1000000
- `truncation_strategy`: "middle_summarize"
- `generate_manifest`: true

## Conclusion

The Gemini 1.5 Pro support in BetterRepo2File provides a powerful way to process large codebases while maintaining context and structure. The combination of large token budget, intelligent truncation, and semantic analysis makes it ideal for comprehensive code analysis tasks.