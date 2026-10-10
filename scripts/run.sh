#!/usr/bin/env bash

set -e

# Find project root
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
PYTHON="$BACKEND/.venv/bin/python"

# Verify Python environment
if [ ! -f "$PYTHON" ]; then
    echo "Error: Python virtual environment not found."
    echo "Create it in backend/.venv and install the project."
    exit 1
fi

# Verify frontend build
if [ ! -f "$FRONTEND/dist/index.html" ]; then
    echo "Error: Frontend has not been built."
    echo "Run: cd frontend && npm install && npm run build"
    exit 1
fi

# Start application
cd "$BACKEND"

echo "Starting System Monitor..."
echo "Open http://localhost:8000"

exec "$PYTHON" -m uvicorn app.main:app \
    --host "${MONITOR_HOST:-127.0.0.1}" \
    --port 8000