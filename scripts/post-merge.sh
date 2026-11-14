#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

# Reinstall the app's declared dependencies after merged changes.
pip install -r backend/requirements.txt

# Catch syntax errors without requiring app secrets or a database connection.
python -m compileall -q backend
