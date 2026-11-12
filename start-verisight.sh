#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
if [ -f "$ROOT/.env" ]; then set -a; . "$ROOT/.env"; set +a; fi
if [ ! -x .venv/bin/python ]; then echo 'Create .venv and install backend/requirements.txt first.' >&2; exit 1; fi
if [ ! -d frontend/node_modules ]; then echo 'Run npm ci in frontend first.' >&2; exit 1; fi
.venv/bin/python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8101 --no-access-log & API_PID=$!
(cd frontend && npm run dev -- --host 127.0.0.1 --port 5174) & WEB_PID=$!
trap 'kill "$API_PID" "$WEB_PID" 2>/dev/null || true' EXIT INT TERM
open http://localhost:5174 2>/dev/null || true
wait "$API_PID" "$WEB_PID"
