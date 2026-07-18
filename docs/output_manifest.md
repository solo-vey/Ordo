# Generated Output Manifest

M13 introduces a formal manifest for generated output artifacts.

Every successful `ordo generate-output <package>` writes:

```text
generated_outputs/output_manifest.json
```

The manifest makes generated markdown files traceable derived artifacts. It records:

- package name, version and Ordo version;
- generation mode;
- source state location and state hash;
- one entry per generated artifact;
- template set id/version/source;
- template hash;
- required output/gate evidence;
- generated file hash and byte size;
- handoff status.

`ordo validate-output <package>` validates the manifest as well as the rendered files.

## Typical workflow

```bash
ordo intake packages/history_event_guided_intake --answers packages/history_event_guided_intake/run_inputs/intake_success.yaml --non-interactive
ordo generate-output packages/history_event_guided_intake
ordo validate-output packages/history_event_guided_intake
```

## Why it matters

Without an output manifest, generated files are just loose markdown files. With the manifest, each output can be traced back to:

```text
state → template → gates → generated artifact → hash → handoff status
```

This supports release validation, reproducibility and later audit.
