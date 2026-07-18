# Run State

`run_state.json` is the current state of an Ordo execution.

Minimal shape:

```json
{
  "package_id": "",
  "package_version": "",
  "current_node": "",
  "answered_questions": [],
  "contracts": {},
  "gates": {},
  "decisions": [],
  "open_questions": [],
  "blocked": false,
  "go_no_go": "unknown"
}
```

Current CLI helpers also accept reports that embed a `state` object, for example `reports/intake_report.json`.

`next-step` is defined by:

```text
compiled/program.ir.json + run_state.json
```

not by free-form memory or by scanning Markdown documents.

## M57 Runtime Checkpoint Discipline

Runtime Mode now enforces a checkpoint layer: one node, one contract, and one decision at a time. Helper reports expose `checkpoint_table`, `earliest_incomplete_node`, `open_required_fields`, and `forward_allowed`. `next-step` prioritizes the earliest incomplete node, and `generate-output` is blocked while checkpoint gaps remain. Detailed rules live in `language/RUNTIME_CHECKPOINTS.md` and package `START_HERE_RUNTIME_MODE.md`; minimal runtime prompts stay minimal.

