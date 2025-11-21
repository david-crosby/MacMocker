#!/bin/bash

set -e

echo "Installing MacMocker..."

# Check for Python 3.10+
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "Error: Python 3.10+ required, found $PYTHON_VERSION"
    exit 1
fi

# Install uv if not present
if ! command -v uv &> /dev/null; then
    echo "Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Install dependencies
echo "Installing dependencies..."
uv pip install --system -e .

# Create default artifacts directory
mkdir -p ~/macmocker_artifacts

# Set execute permissions
chmod +x main.py

echo "Installation complete"
echo "Run tests with: python3 main.py --config config/quick_tests.yaml"
