# Ordo Tree Editor 0.2.0-alpha.20.0.180-dev

## Show Data Flow — Canonical Data Layer adapter

- `Show Data Flow` now prefers `ordo.design.editor_projection.v1` and follows its `data_layer` reference to `ordo.authoring.canonical_data_layer.v1`.
- The Editor deterministically projects canonical state variables, node read/write dependencies, gates, and declared outputs/artifacts into the Data Flow UI.
- The adapter is read-only UI projection logic and does not extend Ordo syntax or alter compiler/runtime semantics.
- Legacy `canonical_sources.graph` authoring bundles remain supported as a backward-compatible fallback.
- Empty-state/help text now describes both canonical Data Layer projections and legacy authoring bundles.
- Added regression coverage for canonical Data Layer discovery, preference, graph projection, and execution-semantics isolation.
- Verified against `PASSPORT_CHANGE_PLAYBOOK_0.3.5_CANDIDATE_31_PASSPORT_ONLY_MODEL_RUN.zip`: 152 objects, 296 relations, 1 gate.
