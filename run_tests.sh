#!/bin/bash

# Run tests locally or in Docker

set -e

echo "=== BetterRepo2File Test Runner ==="
echo

# Check if we should use Docker
if [ "$1" == "--docker" ]; then
    echo "Running tests in Docker..."
    docker-compose --profile test up --build
    exit 0
fi

# Run tests locally
echo "Running tests locally..."

# Ensure we're in the project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
pip install pytest pytest-cov pytest-flask pytest-mock

# Create test results directory
mkdir -p test_results

# Run Python tests
echo
echo "Running Python tests..."
python -m pytest tests/test_app.py -v --cov=app --cov-report=html:test_results/python_coverage
python -m pytest tests/test_repo2file.py -v --cov=repo2file --cov-append --cov-report=html:test_results/python_coverage

# Install JavaScript dependencies if needed
if [ ! -d "tests/node_modules" ]; then
    echo
    echo "Installing JavaScript test dependencies..."
    cd tests
    npm install
    cd ..
fi

# Run JavaScript tests
echo
echo "Running JavaScript tests..."
cd tests
npm test -- --coverage --coverageDirectory=../test_results/js_coverage
cd ..

echo
echo "=== Test Suite Complete ==="
echo "Coverage reports available in test_results/"
echo "  - Python: test_results/python_coverage/index.html"
echo "  - JavaScript: test_results/js_coverage/index.html"