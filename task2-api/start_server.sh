#!/bin/bash
# Start Task 2 API Server (Helper Script)

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"

# Ensure Task 1 is accessible
TASK1_DIR="$PROJECT_ROOT/../task1-recaptcha-stealth"
export PYTHONPATH="$PROJECT_ROOT/src:$TASK1_DIR:$PYTHONPATH"

echo "🚀 Starting Task 2 API Server..."
echo "   Base Path: $PROJECT_ROOT"
echo "   Task 1 Path: $TASK1_DIR"
echo "   Python Path: $PYTHONPATH"

# Activate Venv if exists
if [ -d "$PROJECT_ROOT/.venv" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# Run Uvicorn
# We run 'main:app' because 'src' is in PYTHONPATH, treating src contents as top-level modules
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
