#!/bin/bash
trap "kill 0" EXIT

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment and installing dependencies..."
    uv venv
    source .venv/bin/activate
    uv pip install -r xatra_gui/requirements.txt
    uv pip install -e .
else
    source .venv/bin/activate
fi

echo "Starting Backend..."
# Run from root so imports work
python -m uvicorn xatra_gui.main:app --reload --host 0.0.0.0 --port 8088 &

echo "Starting Frontend..."
cd xatra_gui/frontend
npm run dev &

wait