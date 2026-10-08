#!/usr/bin/env bash
set -e

# Change to script directory
cd "$(dirname "$0")"

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

export PYTHONPATH=.
echo "🚀 Starting RunTrack FastAPI Backend on http://127.0.0.1:8000..."
exec uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
