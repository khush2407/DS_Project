#!/bin/bash

# Run all tests with coverage
pytest tests/ \
    --cov=. \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-fail-under=80 \
    -v \
    --asyncio-mode=auto

# Check if tests passed
if [ $? -eq 0 ]; then
    echo "All tests passed successfully!"
    exit 0
else
    echo "Some tests failed!"
    exit 1
fi 