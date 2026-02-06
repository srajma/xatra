#!/bin/bash
trap "kill 0" EXIT

BACKEND_PORT=8088

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment and installing dependencies..."
    uv venv
    source .venv/bin/activate
    uv pip install -r xatra_gui/requirements.txt
    uv pip install -e .
else
    source .venv/bin/activate
fi

# Free the backend port if something is still running from a previous session
free_port() {
    if command -v fuser >/dev/null 2>&1; then
        fuser -k "$BACKEND_PORT"/tcp 2>/dev/null || true
    fi
    if command -v lsof >/dev/null 2>&1; then
        for pid in $(lsof -ti:"$BACKEND_PORT" 2>/dev/null); do
            kill -9 "$pid" 2>/dev/null || true
        done
    fi
}
port_in_use() {
    if command -v lsof >/dev/null 2>&1; then
        lsof -ti:"$BACKEND_PORT" >/dev/null 2>&1
    else
        fuser "$BACKEND_PORT"/tcp >/dev/null 2>&1
    fi
}

if port_in_use; then
    echo "Freeing port $BACKEND_PORT (killing existing process(es))..."
    free_port
    for i in 1 2 3 4 5; do
        sleep 1
        if ! port_in_use; then break; fi
        [ "$i" -eq 5 ] && { echo "ERROR: Port $BACKEND_PORT still in use. Try: kill -9 \$(lsof -ti:$BACKEND_PORT)"; exit 1; }
        free_port
    done
fi

echo "Starting Backend (port $BACKEND_PORT)..."
# Run from root so imports work
python -m uvicorn xatra_gui.main:app --reload --host 0.0.0.0 --port "$BACKEND_PORT" &

echo "Starting Frontend..."
cd xatra_gui/frontend
npm run dev &

wait