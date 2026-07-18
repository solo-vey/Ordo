# M59.2 Incremental Intake Evidence Report

Status: passed

## Scope

M59.2 adds one-node runtime progression and evidence reporting:

- `ordo intake <package> --submit <NODE_ID> --answer "..."`
- `reports/intake_submit_report.json`
- `runtime/evidence/*_evidence.json`
- SHA-256 digests for runtime helper/evidence reports
- embedded runtime CLI support for submit mode from source-free runtime packages

## Commands executed

- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=cli python -m pytest -q cli/tests/test_cli_workflow.py` → `58/58 OK`
- `PYTHONPATH=cli python -m ordo.cli lint packages/history_event_guided_intake` → passed
- `ordo package packages/history_event_guided_intake --profile runtime` → passed
- extracted/source-free runtime profile submit covered by regression test
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=cli python -m ordo.cli repo-check .` → passed after generated source artifacts were cleaned

## Evidence behavior

A submit call returns the next node and prints evidence in this form:

```text
intake-submit: passed node=<NODE_ID> next_node=<NEXT_NODE> (.../reports/intake_submit_report.json)
evidence: runtime/evidence/<RUN_ID>_001_<NODE_ID>_evidence.json sha256=<digest>
```

The AI/runtime operator must show the evidence report path and SHA-256 digest before asking the next runtime question.

## Known limitations

- This is still Trust Level 1 evidence enforcement.
- Hash-chain snapshots are not part of M59.2.
- `ordo verify-session` is not part of M59.2.
- Canary checks in compiled IR are not part of M59.2.
