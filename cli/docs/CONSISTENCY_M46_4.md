# `ordo consistency` — cross-artifact consistency check

`ordo consistency` generates `CONSISTENCY_CHECK_REPORT.json` for a package after rendered artifacts exist.

It checks the deterministic path:

```text
confirmed contracts → required artifacts → rendered files → cross-artifact consistency → go/no-go hint
```

## What it checks

- required artifacts exist;
- confirmed contract values appear in all required artifacts;
- repeated values such as alias, display names, source fields and test strategy are consistent across artifacts;
- `validate-artifacts` status is included in the same report;
- blocking issues are returned as machine-readable entries.

## What it does not check

- it does not execute live product code;
- it does not infer arbitrary business values that are not declared as contract fields;
- it does not replace human review of wording or business meaning.

## Command

```bash
ordo consistency packages/history_event_guided_intake
```

Optional arguments:

```bash
ordo consistency <package> \
  --artifacts <generated-artifacts-dir> \
  --state <run-state.yaml-or-json> \
  --out <custom-report-path>
```

Default output:

```text
reports/CONSISTENCY_CHECK_REPORT.json
```

## Exit codes

- `0` — `passed` or `passed_with_warnings`;
- `1` — `failed`.

## Example issue

```json
{
  "code": "ORDO-COV-004",
  "message": "Generated artifacts disagree on the same confirmed contract field.",
  "contract": "G_EVENT_IDENTITY_CONTRACT",
  "field": "event_alias"
}
```

## Relation to other commands

Recommended pipeline:

```text
lint → compile → coverage → intake/run → generate-output → validate-output → validate-artifacts → consistency
```
