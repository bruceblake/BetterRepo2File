# Use Python 3.11 as base image
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js and npm for JavaScript tests
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install test dependencies
RUN pip install --no-cache-dir pytest pytest-cov pytest-flask pytest-mock

# Copy application code
COPY . .

# Install JavaScript test dependencies
RUN cd tests && npm init -y && npm install --save-dev jest @testing-library/dom @testing-library/jest-dom jsdom

# Create test results directory
RUN mkdir -p /app/test_results

# Default command for base image
CMD ["python", "app/app.py"]

# Test runner image
FROM base as test-runner

# Create test runner script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "=== Running BetterRepo2File Test Suite ==="\n\
echo\n\
\n\
# Run Python tests\n\
echo "Running Python tests..."\n\
python -m pytest tests/test_app.py -v --cov=app --cov-report=html:/app/test_results/python_coverage\n\
python -m pytest tests/test_repo2file.py -v --cov=repo2file --cov-append --cov-report=html:/app/test_results/python_coverage\n\
\n\
# Run JavaScript tests\n\
echo -e "\nRunning JavaScript tests..."\n\
cd tests && npm test -- --coverage --coverageDirectory=/app/test_results/js_coverage\n\
\n\
echo -e "\n=== Test Suite Complete ==="\n\
echo "Coverage reports available in /app/test_results/"\n\
' > /usr/local/bin/run_tests.sh && chmod +x /usr/local/bin/run_tests.sh

# Set entrypoint for test runner
ENTRYPOINT ["/usr/local/bin/run_tests.sh"]