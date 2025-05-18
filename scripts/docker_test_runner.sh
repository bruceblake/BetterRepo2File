#!/bin/bash
# Docker Test Runner Script

set -e

# Default values
FRAMEWORK="${TEST_FRAMEWORK:-auto}"
REPO_PATH="${REPO_PATH:-/test}"
OUTPUT_FORMAT="${OUTPUT_FORMAT:-json}"

# Function to detect project type and run appropriate tests
run_tests() {
    cd "$REPO_PATH"
    
    case "$FRAMEWORK" in
        auto)
            # Auto-detect test framework
            if [ -f "pytest.ini" ] || [ -f "setup.cfg" ] || [ -f "tox.ini" ]; then
                echo "Detected Python project with pytest"
                pytest --tb=short --json-report --json-report-file=/test_results/pytest_report.json || true
            elif [ -f "package.json" ] && grep -q "test" package.json; then
                echo "Detected Node.js project"
                npm install
                npm test -- --json > /test_results/npm_report.json || true
            elif [ -f "go.mod" ]; then
                echo "Detected Go project"
                go test -json ./... > /test_results/go_report.json || true
            elif [ -f "Cargo.toml" ]; then
                echo "Detected Rust project"
                cargo test --message-format=json > /test_results/cargo_report.json || true
            elif [ -f "pom.xml" ]; then
                echo "Detected Maven project"
                mvn test -Dmaven.test.failure.ignore=true
                cp target/surefire-reports/*.xml /test_results/ || true
            elif [ -f "build.gradle" ] || [ -f "build.gradle.kts" ]; then
                echo "Detected Gradle project"
                gradle test --continue || true
                cp build/test-results/test/*.xml /test_results/ || true
            elif [ -f "*.csproj" ] || [ -f "*.fsproj" ] || [ -f "*.vbproj" ]; then
                echo "Detected .NET project"
                dotnet test --logger "trx;LogFileName=/test_results/dotnet_report.trx" || true
            else
                echo "No recognized test framework found"
                exit 1
            fi
            ;;
        pytest)
            pytest --tb=short --json-report --json-report-file=/test_results/pytest_report.json || true
            ;;
        npm)
            npm install
            npm test -- --json > /test_results/npm_report.json || true
            ;;
        jest)
            npm install
            npx jest --json --outputFile=/test_results/jest_report.json || true
            ;;
        mocha)
            npm install
            npx mocha --reporter json > /test_results/mocha_report.json || true
            ;;
        go)
            go test -json ./... > /test_results/go_report.json || true
            ;;
        cargo)
            cargo test --message-format=json > /test_results/cargo_report.json || true
            ;;
        maven)
            mvn test -Dmaven.test.failure.ignore=true
            cp target/surefire-reports/*.xml /test_results/ || true
            ;;
        gradle)
            gradle test --continue || true
            cp build/test-results/test/*.xml /test_results/ || true
            ;;
        dotnet)
            dotnet test --logger "trx;LogFileName=/test_results/dotnet_report.trx" || true
            ;;
        *)
            echo "Unknown test framework: $FRAMEWORK"
            exit 1
            ;;
    esac
    
    # Generate summary
    echo "Test execution completed. Results saved to /test_results/"
    ls -la /test_results/
}

# Main execution
run_tests