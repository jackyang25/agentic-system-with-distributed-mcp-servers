#!/bin/bash

# Civic Assistant Team 5 - Test Runner
echo "Civic Assistant Team 5 - Running Tests"
echo "======================================"

# Check if pytest is installed
if ! python3 -m pytest --version > /dev/null 2>&1; then
    echo "Installing pytest..."
    python3 -m pip install pytest
fi

# Run tests
echo "Running MCP and Database tests..."
python3 -m pytest tests/ -v

echo ""
echo "Test run completed!"
