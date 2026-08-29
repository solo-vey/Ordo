# Ordo Tree Editor alpha.20.0.163-dev R3

## Generated-playbook profile execution adapter

This release makes the supported Vibe/generated-playbook `package_tool` profile consistent across compiler and runtime without extending canonical Ordo language semantics.

### Changes

- Added `generated_playbook_profile_adapter.py` as an explicit compiler adapter boundary.
- `execution_contract.runtime_executor: package_tool` + `tool_ref`/`args` compiles to Runtime Semantic Plan `runtime_executor=package_tool` and an explicit `execution_adapter`.
- `template`/`bindings`/`output` no longer cause a supported profile package-tool materializer to compile as `document_generate`.
- Runtime package-tool execution consumes tool path/args from the compiled semantic plan adapter, not directly from profile source metadata.
- Adapter-backed tools receive the current canonical runtime state at `runtime/state.yaml` in their isolated package workspace.
- Tool-returned `state_updates` are accepted only for semantic-plan declared write paths.
- Declared generated outputs are surfaced into the runtime workspace.
- Unsupported/conflicting profile declarations fail with structured compiler diagnostics.

### Language boundary

Canonical Ordo schema/language was not changed. The profile remains an adapter-layer contract, and runtime continues to treat the compiled Runtime Semantic Plan as execution authority.
