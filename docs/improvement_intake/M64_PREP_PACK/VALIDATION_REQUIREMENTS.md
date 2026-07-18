# Validation Requirements for Language Improvement Pack

Status: `planning validation / package self-check`

## This package validates that

```text
- all improvement candidates are classified;
- P0/P1/P2 priority is assigned;
- APF discoveries are not directly promoted to opcodes;
- program-level contract layer is identified as P0;
- FLOW.JOIN / SHARED.TAIL.REFERENCE remain design-spike candidates;
- next APF step remains separate and clear;
- source references are preserved;
- checksums are generated.
```

## Future deterministic validation to add to Ordo/APF

For program-level contract:

```text
program metadata completeness
allowed enum values
execution mode/profile consistency
control level/gate consistency
interaction role completeness
process rail completeness
conversation semantics completeness
hybrid execution deterministic commands present
human review points present
startup prompt/readme policies present
```

For package profile:

```text
source-authoring package contains source YAML and compile path
compiled-runtime package contains compiled IR and runtime entry/status
hybrid package contains both or explains split
handoff package contains start prompt and startup README
```

For derived artifacts:

```text
model hash matches derived output provenance
manifest includes expected outputs
stale outputs are blocked or explicitly marked omitted/not-applicable
```
