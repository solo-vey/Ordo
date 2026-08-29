#!/bin/sh
set -eu
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

# Optional per-install defaults. These are application parameters, not Editor code.
DEFAULTS_FILE="${ORDO_EDITOR_DEFAULTS_FILE:-$SCRIPT_DIR/ordo_editor_defaults.env}"
if [ -f "$DEFAULTS_FILE" ]; then
  set -a
  # shellcheck disable=SC1090
  . "$DEFAULTS_FILE"
  set +a
fi

python_version_ok() {
  candidate="$1"
  command -v "$candidate" >/dev/null 2>&1 || [ -x "$candidate" ] || return 1
  "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)' >/dev/null 2>&1
}

python_runtime_ok() {
  candidate="$1"
  python_version_ok "$candidate" || return 1
  "$candidate" -c 'import sys, yaml; raise SystemExit(0 if sys.version_info >= (3,10) else 1)' >/dev/null 2>&1
}

find_base_python() {
  # Prefer explicit user choice, then common command names, then common macOS/Homebrew locations.
  if [ -n "${ORDO_PYTHON:-}" ]; then
    if python_version_ok "$ORDO_PYTHON"; then
      printf '%s\n' "$ORDO_PYTHON"
      return 0
    fi
    echo "Configured ORDO_PYTHON is not usable or is older than Python 3.10: $ORDO_PYTHON" >&2
    return 1
  fi

  for candidate in python3.13 python3.12 python3.11 python3.10; do
    if python_version_ok "$candidate"; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  # Keep the generic pair explicit for portable launcher compatibility.
  for candidate in python3 python; do
    if python_version_ok "$candidate"; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done

  for candidate in \
    /opt/homebrew/bin/python3 \
    /usr/local/bin/python3 \
    /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 \
    /Library/Frameworks/Python.framework/Versions/3.12/bin/python3 \
    /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
    /Library/Frameworks/Python.framework/Versions/3.10/bin/python3
  do
    if python_version_ok "$candidate"; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  return 1
}

BASE_PYTHON="$(find_base_python || true)"
if [ -z "$BASE_PYTHON" ]; then
  echo "Ordo Tree Editor needs Python 3.10+."
  echo "No suitable Python 3.10+ interpreter was found automatically."
  echo "Install Python 3.10+ (for example via python.org or Homebrew) or set ORDO_PYTHON."
  exit 1
fi

# Use an explicitly configured interpreter directly when it already has runtime dependencies.
if python_runtime_ok "$BASE_PYTHON"; then
  PYTHON_BIN="$BASE_PYTHON"
else
  # Bootstrap a private runtime environment so users do not need global pip packages.
  VENV_DIR="${ORDO_VENV_DIR:-$SCRIPT_DIR/.venv}"
  VENV_PYTHON="$VENV_DIR/bin/python"
  REQUIREMENTS_FILE="$SCRIPT_DIR/requirements-runtime.txt"

  if ! python_runtime_ok "$VENV_PYTHON"; then
    echo "Preparing local Ordo Tree Editor Python environment..."
    rm -rf "$VENV_DIR"
    if ! "$BASE_PYTHON" -m venv "$VENV_DIR"; then
      echo "Failed to create local virtual environment with: $BASE_PYTHON"
      exit 1
    fi
    if ! "$VENV_PYTHON" -m pip install --disable-pip-version-check -r "$REQUIREMENTS_FILE"; then
      echo "Failed to install Ordo Tree Editor runtime dependencies into: $VENV_DIR"
      echo "Check internet/package-index access, or preinstall PyYAML and set ORDO_PYTHON."
      exit 1
    fi
  fi
  PYTHON_BIN="$VENV_PYTHON"
fi

cd "$SCRIPT_DIR/../.."
exec "$PYTHON_BIN" utilities/ordo_tree_editor/editor_service.py "$@"
