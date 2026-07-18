# DD-ORDO-M59-001 — CLI-enforced runtime package

Status: accepted
Milestone: M59.1

## Decision

Runtime profile packages must include an embedded runtime CLI and must hard-stop if no approved CLI can run.

## Reason

A runtime package that contains only compiled IR and start files can still be executed by an AI through direct IR reading. That may be useful for inspection, but it is not enforced Runtime Mode. The first practical trust improvement is to put the deterministic helper inside the runtime package.

## Consequences

- `ordo package --profile runtime` includes `cli_embedded/`.
- Embedded runtime CLI blocks authoring/package/release commands.
- `START_HERE_RUNTIME_MODE.md` no longer allows silent soft fallback.
- If CLI cannot run, the session must hard-stop or explicitly enter nondeterministic fallback with `DETERMINISM_NOT_ENFORCED` markers.
- This is Trust Level 1, not MCP/sandbox isolation.
