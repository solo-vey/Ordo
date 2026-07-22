#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLAN="${SCRIPT_DIR}/../DRY_RUN_PLAN.json"
ROOT="${ORDO_PATHWALK_ROOT:-}"
if [[ -z "${ROOT}" ]]; then
  CANDIDATE="$(cd "/../../../../.." && pwd)"
  if [[ -d "${CANDIDATE}/utilities/ordo_pathwalk" ]]; then ROOT="${CANDIDATE}"; fi
fi
if [[ -z "${ROOT}" || ! -d "${ROOT}/utilities/ordo_pathwalk" ]]; then
  echo "ERROR: ORDO_PATHWALK_ROOT must point to an Ordo workspace or PathWalk RC root containing utilities/ordo_pathwalk/." >&2
  echo "For standalone RC + developer bundle, set ORDO_PATHWALK_ROOT=<pathwalk_rc_root> and ORDO_CLI_ROOT=<developer_bundle>/cli." >&2
  exit 64
fi
CLI_ROOT="${ORDO_CLI_ROOT:-${ROOT}/cli}"
if [[ ! -d "${CLI_ROOT}/ordo" ]]; then
  echo "ERROR: Ordo CLI package not found. Set ORDO_CLI_ROOT to a cli directory containing ordo/." >&2
  exit 65
fi
PY_PATH="${CLI_ROOT}:${ROOT}${PYTHONPATH:+:${PYTHONPATH}}"
cd "${ROOT}"
exec env PYTHONPATH="${PY_PATH}" python3 -m utilities.ordo_pathwalk.cli dry-run-job --plan "${PLAN}" --job-id scenario_010_json_ordo-code < /dev/null
