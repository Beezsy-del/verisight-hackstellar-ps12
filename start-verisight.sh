#!/bin/sh
set -eu
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  echo 'Create .venv and install backend/requirements.txt first.' >&2
  exit 1
fi
.venv/bin/python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8001 &
backend_pid=$!
trap 'kill "$backend_pid" 2>/dev/null || true' EXIT INT TERM
npm run dev --prefix frontend -- --host 127.0.0.1 --port 5175 --strictPort
