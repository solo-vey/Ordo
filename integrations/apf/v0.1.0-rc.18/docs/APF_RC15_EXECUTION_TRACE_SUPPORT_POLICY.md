# APF rc.15 — Execution Trace Support

## Status

`release-candidate-ready-for-human-confirmation`

## Added capability

APF can design, package and validate Execution Trace capability for generated playbooks in alignment with Ordo v0.12 M72.

Canonical flow:

```text
trace design decision
→ human confirmation
→ configuration and conditional artifacts
→ event coverage mapping
→ runtime adapter conformance when required
→ validation gates
→ package assembly
```

## Defaults and boundary

- APF internal trace is disabled by default.
- Generated playbooks support a runtime capture toggle.
- Recommended generated-playbook default is enabled with `capture_level: standard`, unless explicitly changed and justified.
- APF does not generate the actual runtime trace; the runtime adapter does.

## Exclusions

This release does not enable APF internal tracing, implement a concrete runtime engine, activate deferred replay backlog, or modify Ordo core.
