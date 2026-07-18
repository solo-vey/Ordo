# Prompt Registry Packaging Checks

Status: M67.0 accepted draft packaging-check profile.

This document consolidates package-level checks for prompt registry and startup profile consistency.

## Required checks

Prompt registry checks:

- prompt registry exists and parses;
- prompt IDs are unique;
- prompt paths exist;
- required prompts are present;
- prompt refs resolve;
- target nodes/artifacts/gates resolve where applicable;
- prompt language/audience/visibility/lifecycle/state-change fields are declared;
- prompt text does not claim gate, validation, runtime, or state authority.

Manifest checks:

- prompt manifest exists;
- manifest paths exist;
- checksums match when declared;
- packaged prompt files are covered.

Startup checks:

- startup profile exists;
- default startup mode is declared and defined;
- entry files exist;
- startup prompt IDs resolve to prompt registry;
- startup prompt files are manifest-covered.

Derived artifact checks:

- source-of-truth is explicit;
- derived artifacts are declared when relied upon;
- stale artifacts are regenerated or covered by delta backlog.

## Decision model

```text
if any error:
  decision = blocked
elif any warning:
  decision = approved_with_warnings
else:
  decision = approved
```

## Non-goals

M67.0 defines review semantics only. CLI/linter implementation remains future work.
