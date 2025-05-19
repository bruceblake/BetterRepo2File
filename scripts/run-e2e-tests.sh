#!/bin/bash

# Wait for the application to be ready
./scripts/wait-for-app.sh

# Set environment variables
export BASE_URL="http://app:5000"
export HEADLESS="true"
export TIMEOUT="30000"

# Run tests
echo "Running E2E tests..."
python -m pytest \
    tests_e2e/ \
    --base-url="$BASE_URL" \
    --html=playwright-report/report.html \
    --self-contained-html \
    -v \
    --timeout=120 \
    -s

# Exit with the test result code
exit $?