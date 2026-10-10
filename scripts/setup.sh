#!/usr/bin/env bash

set -e

# Find project root
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"

echo "Setting up System Monitor..."

# Check prerequisites
for command in python3 npm; do
    if ! command -v "$command" >/dev/null 2>&1; then
        echo "Error: $command is not installed."
        exit 1
    fi
done

# Create Python environment
echo "Setting up Python environment..."

if [ ! -f "$BACKEND/.venv/bin/python" ]; then
    python3 -m venv "$BACKEND/.venv"
fi

# Install backend dependencies
echo "Installing Python dependencies..."

"$BACKEND/.venv/bin/python" -m pip install -e "$BACKEND"

# Install frontend dependencies
echo "Installing frontend dependencies..."

cd "$FRONTEND"

if [ -f "package-lock.json" ]; then
    npm ci
else
    npm install
fi

# Build React
echo "Building frontend..."

npm run build

echo ""
echo "System Monitor setup complete!"
echo "Run ./scripts/run.sh to start the application."