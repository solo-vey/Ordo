# APF Session Package Load and Cache

Milestone: M80.0 runtime contract.

`SESSION_PACKAGE_LOAD_AND_CACHE` prevents repeated unpacking and full rereading of the same validated package during one APF session.

## Runtime sequence

`MESSAGE_RECEIVED → PACKAGE_CACHE_CHECK → CACHE_HIT | RELOAD_REQUIRED → ACTIVE_NODE_EXECUTION`

`PACKAGE_RELOAD_NECESSITY_GATE` is fail-closed. It returns `cache_hit` only when the recorded version and SHA-256 fingerprint match, the cache is valid, the manifest and source of truth were loaded, the unpacked location exists, and all required files are present.

A reload decision must not advance the process or alter the active node, active question, accepted answers, path history, approvals, or generated artifacts.

## Reload conditions

Reload is required when the package version or fingerprint changes, cache state is missing/invalid, the unpacked location is unavailable, a required file is missing, manifest/source validation is incomplete, or the user explicitly requests a full reload.

## Trace events

- `PACKAGE_CACHE_HIT`
- `PACKAGE_CACHE_MISS`
- `PACKAGE_RELOAD_REQUIRED`
- `PACKAGE_RELOAD_COMPLETED`
- `PACKAGE_CACHE_INVALIDATED`

Generated playbooks inherit this APF runtime capability. Their own instructions should contain only a short rule against rereading an unchanged validated package.

## M80.3 trace, metrics and diagnostics

Runtime cache operations emit JSONL trace records using `ordo.apf.package_cache_trace.v1`.
Metrics use `ordo.apf.package_cache_metrics.v1` and report event counts, decision volume, malformed records and cache-hit ratio.
Diagnostics use `ordo.apf.package_cache_diagnostics.v1` and fail on unreadable state, missing payload or missing required files; malformed trace records are warnings.
