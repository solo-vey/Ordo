# ET-6 — Validation gates

Status: completed

Implemented:
- blocking validation contract for generated-playbook execution-trace capability;
- schema/config, artifact, coverage, integrity, redaction, replay, and runtime-consistency gates;
- conditional adapter-conformance gate for `runtime_enforced` mode;
- validation report template with explicit release decision;
- `not_applicable` path when trace support is intentionally disabled.

Release is blocked when any applicable blocking check fails.

Boundary preserved:
- APF validates trace capability contracts and package evidence;
- target runtime emits actual traces;
- APF internal tracing remains disabled by default.

Next: ET-7 — runtime adapter contract.
