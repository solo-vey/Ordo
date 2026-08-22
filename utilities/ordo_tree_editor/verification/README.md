# Editor Verification Framework

This directory is the dynamic verification extension point for Ordo Playbook Explorer.

## Runtime model

The Editor scans `verification/checks/*.json` every time the verification catalog is requested. The UI does not contain a hard-coded check list.

`Verify Playbook -> Run all verifications`:

1. creates an isolated temporary copy of the currently loaded playbook package;
2. loads descriptors from `checks/` in `order` sequence;
3. executes each applicable check one at a time;
4. streams/polls status as `PENDING -> RUNNING -> PASS|FAIL|ERROR|SKIPPED`;
5. never modifies the user's original uploaded ZIP;
6. retains command output in the verification result for inspection.

Checks that require context unavailable to a one-click suite remain visible and become `SKIPPED` with a reason.

## Directory contract

- `checks/*.json` — discoverable verification descriptors.
- `check_descriptor.schema.json` — descriptor schema.
- `toolkit/` — optional executable verification dependencies. It is intentionally not
  duplicated in the curated Editor source tree; checks that need it are reported as
  `SKIPPED` unless a compatible toolkit is supplied for that installation.
- `LANGUAGE_PACKAGE_INTEGRATION_CONTRACT.md` — build/update instructions.

## Placeholders available to command descriptors

- `{package_root}` — extracted playbook root.
- `{source_path}` — canonical source YAML if resolved.
- `{output_root}` — temporary verification output directory.
- `{toolkit_root}` — optional verification toolkit root.

Example:

```json
{
  "schema_version": "ordo.editor.verification_check.v1",
  "id": "lint",
  "title": "Language lint",
  "group": "language",
  "description": "Validate source against the Ordo language model",
  "order": 10,
  "enabled": true,
  "requires": [],
  "timeout_seconds": 180,
  "runner": {
    "type": "command",
    "command": ["python", "-m", "ordo.cli", "lint", "{package_root}"]
  }
}
```

## Portable executable contract

Verification descriptors MUST remain platform-neutral. For Python checks, the first command token SHOULD be `python` or `{python}`; the Editor verification runner resolves it to `sys.executable` at runtime. Do not hard-code an absolute interpreter path, virtualenv path, or assume `python`/`python3` exists on PATH. Future descriptor generators must preserve this rule.
