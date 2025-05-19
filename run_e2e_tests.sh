#!/bin/bash
# Script to run E2E tests for RobustRepo

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
HEADLESS=${HEADLESS:-true}
SPECIFIC_TEST=${1:-""}
PROFILE="e2e"

echo -e "${GREEN}RobustRepo E2E Test Runner${NC}"
echo "================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check if services are running
echo -e "${YELLOW}Checking if services are running...${NC}"
if ! docker-compose ps | grep -q "Up"; then
    echo -e "${YELLOW}Starting services...${NC}"
    docker-compose up -d
    echo -e "${GREEN}Waiting for services to be ready...${NC}"
    sleep 10
fi

# Build the E2E test image if needed
echo -e "${YELLOW}Building E2E test image...${NC}"
docker-compose --profile $PROFILE build e2e-tests

# Run the tests
if [ -z "$SPECIFIC_TEST" ]; then
    echo -e "${GREEN}Running all E2E tests...${NC}"
    docker-compose --profile $PROFILE run --rm \
        -e PLAYWRIGHT_HEADLESS=$HEADLESS \
        e2e-tests
else
    echo -e "${GREEN}Running specific test: $SPECIFIC_TEST${NC}"
    docker-compose --profile $PROFILE run --rm \
        -e PLAYWRIGHT_HEADLESS=$HEADLESS \
        e2e-tests pytest "$SPECIFIC_TEST" -v
fi

# Capture exit code
TEST_EXIT_CODE=$?

# Generate report
if [ -f "playwright-report/report.html" ]; then
    echo -e "${GREEN}Test report available at: playwright-report/report.html${NC}"
fi

# Check for traces
if [ -d "traces" ] && [ "$(ls -A traces)" ]; then
    echo -e "${YELLOW}Traces available in: traces/${NC}"
    echo "View traces with: playwright show-trace traces/<trace-file>.zip"
fi

# Clean up (optional)
if [ "$CLEANUP" = "true" ]; then
    echo -e "${YELLOW}Cleaning up test artifacts...${NC}"
    rm -rf test-results/* traces/* playwright-report/*
fi

# Exit with test status
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
else
    echo -e "${RED}Some tests failed. Check the report for details.${NC}"
fi

exit $TEST_EXIT_CODE