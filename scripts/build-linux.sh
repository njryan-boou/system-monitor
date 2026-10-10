#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
PYTHON="$BACKEND/.venv/bin/python"

echo "Building System Monitor for Linux..."

# Verify build environment
if [ ! -x "$PYTHON" ]; then
    echo "Error: Python virtual environment not found."
    exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
    echo "Error: npm is not installed."
    exit 1
fi

# Build frontend
echo "Building React frontend..."

cd "$FRONTEND"
npm ci
npm run build

# Build executable
echo "Packaging Python backend..."

cd "$BACKEND"

"$PYTHON" -m PyInstaller \
    --noconfirm \
    --clean \
    --onefile \
    --name system-monitor-linux \
    --specpath "$BACKEND/build" \
    --distpath "$BACKEND/dist" \
    --collect-submodules uvicorn \
    --add-data "$FRONTEND/dist:frontend/dist" \
    launcher.py

echo ""
echo "Build successful!"
echo "Executable: $BACKEND/dist/system-monitor-linux"