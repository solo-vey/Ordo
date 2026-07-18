# EXECUTION_TRACE Tooling, Testing and Review Guide

## Purpose

This guide defines the release-facing checks for the `EXECUTION_TRACE` language element after core and runtime/compiler integration.

## Required test layers

1. **Schema examples** — canonical minimal and replayable examples parse as YAML and use only registered values.
2. **Compiler tests** — `execution_trace:` normalizes into one `EXECUTION_TRACE.DEF` instruction.
3. **Runtime lifecycle tests** — initialization, append-only event capture, terminal locking, checksum creation and redaction.
4. **Replay tests** — deterministic, `re_evaluate`, simulation and audit-only plans preserve their side-effect rules.
5. **Tamper/integrity tests** — sequence gaps, event-count drift and checksum drift are detected.
6. **Compatibility tests** — legacy `trace:` remains accepted only through the compatibility adapter and does not become the canonical IR representation.

## Review checklist

- [ ] One primary trace is created per run.
- [ ] Event sequence is strictly increasing and starts at 1.
- [ ] Terminal traces contain exactly one terminal lifecycle event.
- [ ] Sensitive keys are redacted before persistence.
- [ ] `replayable: true` is rejected when required inputs are not preserved.
- [ ] Simulation replay never authorizes external side effects.
- [ ] Generated artifacts have correlated `artifact_generated` events.
- [ ] Trace files do not contain private model chain-of-thought.
- [ ] Book, schema, registry, examples and runtime implementation use the same closed values.

## Operational artifacts

The default runtime artifact is:

```text
runtime/execution_trace.json
```

Generated run reports are runtime outputs and are not added to the source language package unless explicitly requested.
