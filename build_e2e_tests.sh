#!/bin/bash
# Build script for E2E tests

set -e

echo "Building E2E test Docker image..."

# Build without cache to avoid any cache issues
docker-compose build --no-cache e2e-tests

echo "Build complete!"