#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 /path/to/ordo-playbook" >&2
  exit 2
fi
ROOT="$(cd "$(dirname "$0")" && pwd)"
PKG="$(cd "$1" && pwd)"
export PYTHONPATH="$ROOT/ordo_pkg"

run() {
  echo
  echo "==> $*"
  "$@"
}

run python -m ordo.cli lint "$PKG"
run python -m ordo.cli compile "$PKG"
run python -m ordo.cli test "$PKG"
run python -m ordo.cli coverage "$PKG"
run python -m ordo.cli runtime-status "$PKG"
run python -m ordo.cli verify-targets "$PKG"
run python -m ordo.cli clean-check "$PKG" --profile strict

echo
echo "CORE VERIFICATION: PASS"
