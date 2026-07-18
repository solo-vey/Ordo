# `ordo runtime-entry`

`ordo runtime-entry <package>` validates the startup requirements for AI Ordo Runtime Mode.

It checks:

- `START_HERE_RUNTIME_MODE.md` exists and is readable;
- `ordo.yml` can be resolved;
- `source/program.ordo.yaml` exists;
- `compiled/program.ir.json` exists and is not stale;
- the next guided node can be derived from the compiled IR plus optional run state.

Example:

```bash
ordo compile packages/history_event_guided_intake
ordo runtime-entry packages/history_event_guided_intake
```

Optional state:

```bash
ordo runtime-entry packages/history_event_guided_intake --state run_state.json
```

The command writes `reports/runtime_entry_report.json`.

## New errors

```text
ORDO-RUNTIME-007 START_HERE_RUNTIME_MODE.md missing or empty
ORDO-RUNTIME-008 compiled IR cannot be loaded
ORDO-RUNTIME-009 no next NODE.DEF found in compiled IR
```

`ORDO-RUNTIME-009` is a warning because some runtime packages may be output-only packages.
