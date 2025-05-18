# Base image with Python
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies for common test frameworks
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js and npm (for JavaScript tests)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a directory for test results
RUN mkdir -p /app/test_results

# Default command
CMD ["python", "app/app.py"]

# Test runner specific image (multistage)
FROM python:3.9-slim as test-runner

# Install common test tools and frameworks
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    curl \
    golang-go \
    cargo \
    default-jdk \
    maven \
    gradle \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js and npm
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install .NET SDK for dotnet tests
RUN wget https://packages.microsoft.com/config/debian/11/packages-microsoft-prod.deb -O packages-microsoft-prod.deb \
    && dpkg -i packages-microsoft-prod.deb \
    && rm packages-microsoft-prod.deb \
    && apt-get update \
    && apt-get install -y dotnet-sdk-7.0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python test frameworks
RUN pip install pytest pytest-cov unittest-xml-reporting

# Install JavaScript test frameworks globally
RUN npm install -g jest mocha chai nyc

# Create test directory
WORKDIR /test

# Script to run tests
COPY scripts/docker_test_runner.sh /usr/local/bin/docker_test_runner.sh
RUN chmod +x /usr/local/bin/docker_test_runner.sh

# Set entrypoint
ENTRYPOINT ["/usr/local/bin/docker_test_runner.sh"]