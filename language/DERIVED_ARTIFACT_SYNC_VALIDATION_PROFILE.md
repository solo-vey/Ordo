# Derived Artifact Sync Validation Profile

Status: `M67.4 aligned to implemented CLI`

`derived_artifact_sync_validation_profile` defines how declared derived artifacts, manifest evidence, and delta backlog entries are checked as part of clean package review.

This profile aligns the M67.0 `artifact_sync` / `delta_backlog` conventions with the implemented M67.3 `ordo clean-check` command.

## Purpose

Derived artifacts are outputs that are expected to reflect a source package state, for example compiled runtime files, lockfiles, rendered graphs, generated reports, or embedded runtime bundles.

The validation profile answers four questions:

1. Which derived artifacts are expected?
2. Which artifacts are required for the selected review profile?
3. Are missing or stale artifacts covered by `delta_backlog`?
4. Does the clean package gate pass, warn, or block?

## Relationship to CLI

The current minimal CLI implementation checks derived artifacts through this v1 group:

```text
derived_artifacts_current_or_backlogged_when_declared
```

It also checks backlog hygiene through:

```text
delta_backlog_blockers_not_expired_when_declared
```

The current implementation is intentionally conservative:

- if `artifact_sync` is absent, the derived artifact check is `not_applicable`;
- if `artifact_sync` declares derived paths, missing paths must either exist or be covered by `delta_backlog`;
- profile `light` may downgrade some drift to warning;
- profile `standard` and `strict` should block unbacklogged missing derived artifacts;
- expired blockers are warning-level in standard and error-level in strict;
- ownerless blockers are error-level in strict.

## Profile fields

Recommended top-level key:

```yaml
derived_artifact_sync_validation_profile:
  profile_id: clean_package_default_sync_profile
  version: "0.1"
  default_cli_command: ordo clean-check
  default_profile: standard
  required_report: reports/clean_check_report.json
  artifact_policy:
    missing_declared_artifact: block_unless_backlogged
    checksum_mismatch: block_in_standard_and_strict
    stale_artifact: block_unless_backlogged
  delta_backlog_policy:
    expired_blocker_standard: warning
    expired_blocker_strict: error
    ownerless_blocker_strict: error
```

## Severity mapping

| Condition | Light | Standard | Strict |
|---|---|---|---|
| Missing optional derived artifact | warning | warning | error if required by profile |
| Missing declared required artifact | warning if backlogged | error unless backlogged | error unless backlogged |
| Checksum mismatch | warning | error | error |
| Missing artifact covered by backlog | pass/warn | pass/warn | warning unless release-blocking |
| Expired blocker | warning | warning | error |
| Ownerless blocker | warning | warning | error |

## Delta backlog expectations

A `delta_backlog` entry used to justify drift should include:

- stable `id`;
- target path or artifact id;
- reason;
- status;
- owner when strict release profile is used;
- due or expiry date for blocker items;
- resolution expectation.

Backlog entries are not a replacement for synchronization. They are an explicit trace of known drift.

## Non-goals

This profile does not define automatic artifact regeneration. Regeneration is a separate explicit operation and must not be performed silently by `clean-check`.
