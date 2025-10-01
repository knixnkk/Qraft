#!/usr/bin/env bash
set -euo pipefail
if [ -z "${VIRTUAL_ENV-}" ]; then
  echo "Warning: no virtualenv detected. It's recommended to run inside one."
fi
export FLASK_APP=app.py
flask run
