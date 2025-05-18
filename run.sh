#!/bin/bash

# Make script executable with: chmod +x run.sh

# Check for compatible Python version
if command -v python3.12 &> /dev/null; then
    PYTHON_CMD=python3.12
elif command -v python3.11 &> /dev/null; then
    PYTHON_CMD=python3.11
elif command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    echo "Warning: Using Python 3.13 may have compatibility issues with tiktoken"
else
    echo "Python 3 is not installed. Please install Python 3.11 or 3.12 for best compatibility."
    exit 1
fi

# Check if virtual environment exists, create it if it doesn't
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    echo "Virtual environment created."
fi

# Activate virtual environment
source venv/bin/activate

# Install or update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run the application
echo "Starting Repo2File UI application..."
python app/app.py