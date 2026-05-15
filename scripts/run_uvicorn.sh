#!/usr/bin/env bash
set -euo pipefail
# Helper to run uvicorn using the repository's venv/python so the command
# works even when IntelliJ's terminal has a different PATH.
#
# Usage:
#   ./scripts/run_uvicorn.sh            # runs on port 8000
#   ./scripts/run_uvicorn.sh --port 9000
#   ./scripts/run_uvicorn.sh --dry-run  # prints resolved python and command

DRY=0
PORT=8000
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run)
      DRY=1
      shift
      ;;
    --port)
      PORT="$2"
      shift 2
      ;;
    --port=*)
      PORT="${1#*=}"
      shift
      ;;
    -h|--help)
      echo "Usage: $0 [--dry-run] [--port PORT]"
      exit 0
      ;;
    *)
      echo "Unknown argument: $1"
      echo "Usage: $0 [--dry-run] [--port PORT]"
      exit 2
      ;;
  esac
done

# Determine script and project directories so the script can be executed from
# any working directory (IntelliJ terminal often opens at the repository root).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Resolve a suitable python executable. Prefer active venv, then common venv dirs
# inside the project, otherwise fallback to `python` on PATH.
PYTHON=python
if [ -n "${VIRTUAL_ENV:-}" ]; then
  PYTHON="$VIRTUAL_ENV/bin/python"
else
  for candidate in "$PROJECT_DIR/.venv/bin/python" "$PROJECT_DIR/venv/bin/python" "$PROJECT_DIR/env/bin/python"; do
    if [ -x "$candidate" ]; then
      PYTHON="$candidate"
      break
    fi
  done
fi

# Ensure module imports work by running from project dir (so `app` package is importable)
cd "$PROJECT_DIR"

CMD=("$PYTHON" -m uvicorn app.main:app --reload --port "$PORT")

echo "Project dir: ${PROJECT_DIR}"
echo "Resolved python: ${PYTHON}"
echo "Command: ${CMD[*]}"

# If the chosen python doesn't have uvicorn installed, prefer a system uvicorn
# or another python that does. This helps when IntelliJ terminal uses a venv
# without uvicorn installed.
if ! "$PYTHON" -c "import importlib,sys; importlib.import_module('uvicorn')" 2>/dev/null; then
  if command -v uvicorn >/dev/null 2>&1; then
    CMD=("uvicorn" app.main:app --reload --port "$PORT")
    echo "Note: using 'uvicorn' from PATH because ${PYTHON} has no uvicorn module."
  elif command -v python3 >/dev/null 2>&1 && python3 -c "import importlib; importlib.import_module('uvicorn')" 2>/dev/null; then
    CMD=("python3" -m uvicorn app.main:app --reload --port "$PORT")
    echo "Note: using 'python3 -m uvicorn' because ${PYTHON} has no uvicorn module."
  elif python -c "import importlib; importlib.import_module('uvicorn')" 2>/dev/null; then
    CMD=("python" -m uvicorn app.main:app --reload --port "$PORT")
    echo "Note: using 'python -m uvicorn' because ${PYTHON} has no uvicorn module."
  else
    echo "Error: uvicorn module not found in ${PYTHON} and no 'uvicorn' executable found on PATH." >&2
    echo "Install uvicorn in your virtualenv, or run: pip install uvicorn[standard]" >&2
    exit 1
  fi
fi

if [ "$DRY" -eq 1 ]; then
  exit 0
fi

exec "${CMD[@]}"

