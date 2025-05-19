#!/bin/bash
# Script to wait for the application to be ready before starting tests

set -e

APP_URL="${BASE_URL:-http://app:5000}"
MAX_ATTEMPTS=30
SLEEP_TIME=5

echo "Waiting for application at $APP_URL to be ready..."

attempt=0
while [ $attempt -lt $MAX_ATTEMPTS ]; do
    if curl -f "${APP_URL}/health" >/dev/null 2>&1; then
        echo "Application is ready!"
        exit 0
    fi
    
    attempt=$((attempt + 1))
    echo "Attempt $attempt/$MAX_ATTEMPTS - Application not ready yet. Sleeping for $SLEEP_TIME seconds..."
    sleep $SLEEP_TIME
done

echo "Error: Application failed to become ready after $MAX_ATTEMPTS attempts"
exit 1