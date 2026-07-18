# CLEAN_CHECK_FIXTURE_MATRIX — M68.1 real fixture suite

Status: accepted-fixture-test-suite

M68.1 turns the M68.0 fixture plan into a real test fixture suite under:

```text
cli/tests/fixtures/clean_check/
```

The fixtures are repository-local test packages and are not applied packages. Tests
copy each fixture into a temporary directory before running `ordo clean-check`, so
clean-check reports do not dirty the committed fixture directory.

## Fixture matrix

| Fixture | Purpose | Default expected status |
|---|---|---|
| `clean_minimal` | Minimal valid package | `passed` |
| `missing_manifest` | Missing `ordo.yml` | `blocked` |
| `broken_manifest_yaml` | Invalid manifest YAML | `blocked` |
| `missing_source_yaml` | Manifest source missing | `blocked` |
| `broken_source_yaml` | Invalid source YAML | `blocked` |
| `prompt_manifest_valid` | Prompt registry and manifest pass | `passed` |
| `prompt_manifest_checksum_mismatch` | Light warning / standard error checksum mismatch | profile-dependent |
| `prompt_ref_missing` | Unresolved prompt_ref | `blocked` |
| `startup_entry_present` | Startup entry present | `passed` |
| `startup_entry_missing` | Startup entry missing | `blocked` |
| `derived_artifact_present` | Declared derived artifact exists | `passed` |
| `derived_artifact_missing` | Missing derived artifact without backlog | `blocked` |
| `derived_artifact_backlogged` | Missing derived artifact covered by delta backlog | `passed` |
| `expired_delta_blocker` | Expired blocker warning/error by profile | profile-dependent |
| `warning_fail_on_warning` | Warning fixture for `--fail-on-warning` | profile-dependent |

## Test coverage

The test suite covers direct API behavior through `run_clean_check` and CLI behavior
through `python -m ordo.cli clean-check` for JSON stdout, `--out`, and
`--fail-on-warning`.
