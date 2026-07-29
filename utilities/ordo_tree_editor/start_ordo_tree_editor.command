#!/bin/sh
set -eu
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$SCRIPT_DIR/../.."

PYTHON_BIN="${ORDO_PYTHON:-python3}"
if ! "$PYTHON_BIN" -c 'import yaml' >/dev/null 2>&1; then
  echo "Ordo Tree Editor needs Python 3.10+ with PyYAML installed."
  echo "Set ORDO_PYTHON to an Ordo environment, then run this file again."
  printf "Press Return to close..."
  read _
  exit 1
fi

exec "$PYTHON_BIN" utilities/ordo_tree_editor/editor_service.py
