#!/usr/bin/env bash
set -e

# Change to script directory
cd "$(dirname "$0")"

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

export PYTHONPATH=.
echo "🏃 Starting RunTrack Streamlit Frontend on http://127.0.0.1:8501..."
exec streamlit run app.py --server.port 8501 --server.headless true
