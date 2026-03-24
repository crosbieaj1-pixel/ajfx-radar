#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

if [ -d "venv" ]; then
  # shellcheck disable=SC1091
  source "venv/bin/activate"
elif [ -d ".venv" ]; then
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
fi

REQ_FILE="backend/requirements.txt"
if [ ! -f "$REQ_FILE" ]; then
  REQ_FILE="requirements.txt"
fi

if ! python -c "import fastapi, uvicorn" >/dev/null 2>&1; then
  echo "Installing dependencies from $REQ_FILE..."
  python -m pip install -r "$REQ_FILE"
fi

echo "Starting AJFX Trading Radar on port 8011..."
exec python -m uvicorn backend.main:app --host 0.0.0.0 --port 8011 --reload
