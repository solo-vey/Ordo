# M7: Package-to-output generation

`ordo generate-output` creates controlled Markdown output artifacts from the latest `run` or `intake` state.

It is intentionally conservative:

- it does not call an AI model;
- it does not invent missing domain content;
- it maps confirmed Ordo state into derived handoff documents;
- it writes `reports/output_generation_report.json`;
- generated files are derived artifacts, not source of truth.

## Example

```bash
ordo intake packages/history_event_guided_intake --answers packages/history_event_guided_intake/run_inputs/intake_success.yaml --non-interactive
ordo generate-output packages/history_event_guided_intake
```

Generated files are written to:

```text
generated_outputs/
```

For `history_event.guided_intake`, the generator creates:

```text
01_HISTORY_EVENT_CONTRACT_<ALIAS>.md
02_QA_SCOPE_<ALIAS>.md
03_HANDOFF_<ALIAS>.md
```
