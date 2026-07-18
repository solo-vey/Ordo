# APF Execution Trace authoring-flow integration policy

Every concrete-playbook authoring run must make and record an explicit Execution Trace design decision. APF does not generate the runtime trace itself; it generates the contracts, mappings, policies and validation evidence required for the target runtime to do so.

## Defaults

- APF internal tracing remains disabled by default.
- Generated applied playbooks support tracing by default.
- The recommended generated-playbook default is `enabled_by_default: true`, `capture_level: standard`, `replay.mode: deterministic` and a runtime enable/disable toggle.

## Conditional assembly

When trace support is enabled, APF must generate the config, schema, event mapping, redaction policy, replay policy and validation report. A runtime adapter contract and conformance report are additionally required for `runtime_enforced` mode.

When support is disabled, APF records the decision and rationale but must not generate misleading runtime trace artifacts.

## Human confirmation

Before package assembly, the process owner confirms the support decision, default capture state, capture level, replay mode, storage/retention choice, redaction policy and runtime toggle authority.

## Boundary

Trace configuration cannot grant navigation, gate, approval or state-mutation authority. Hidden model chain of thought, secrets and full confidential payloads must not be persisted.
