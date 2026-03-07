#!/bin/bash
# Validate Examples Script
# Runs all examples and tests to ensure they work correctly

set -e

echo "======================================"
echo "Module 1 Examples and Tests Validation"
echo "======================================"
echo ""

TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to run a test
run_test() {
    local test_file=$1
    local test_name=$(basename "$test_file")

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    echo "🧪 Running $test_name..."
    if python3 -m pytest "$test_file" -v --tb=short; then
        echo "✅ $test_name passed"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo "❌ $test_name failed"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    echo ""
}

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "📦 Installing pytest..."
    pip3 install pytest
fi

# Check if flake8 is installed
if ! command -v flake8 &> /dev/null; then
    echo "📦 Installing flake8..."
    pip3 install flake8
fi

# Run Python linting
echo "🔍 Running flake8 linting..."
if [ -d "examples" ] && [ -n "$(find examples -name '*.py')" ]; then
    flake8 examples/ --config .flake8 || true
fi
echo ""

# Run tests
if [ -d "tests" ]; then
    echo "🧪 Running test suite..."
    for test_file in tests/test_*.py; do
        if [ -f "$test_file" ]; then
            run_test "$test_file"
        fi
    done
fi

# Run exercise validation tests
if [ -d "exercises" ]; then
    echo "🧪 Running exercise tests..."
    for test_file in exercises/*/test_*.py; do
        if [ -f "$test_file" ]; then
            run_test "$test_file"
        fi
    done
fi

# Summary
echo "======================================"
echo "Validation Summary"
echo "======================================"
echo "Total tests: $TOTAL_TESTS"
echo "Passed: $PASSED_TESTS"
echo "Failed: $FAILED_TESTS"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo "✅ All validations passed!"
    exit 0
else
    echo "❌ Some tests failed. See output above for details."
    exit 1
fi
