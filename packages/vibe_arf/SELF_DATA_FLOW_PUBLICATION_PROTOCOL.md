# Vibe Self Data Flow Publication Protocol — alpha.30

## Authority

- Canonical Ordo remains the only execution-language semantic authority.
- `authoring/` is Vibe's canonical authoring information model.
- `design/` is an adapter-facing generated publication projection for Source Data Flow visualization.

## Pipeline

`authoring AIM -> AIM validation -> AIM↔Ordo validation -> deterministic publication -> publication equivalence validation -> package -> Editor Source Data Flow`

## Published surface

- `design/MODEL_BUNDLE.yaml`
- `design/information_dependency_graph.yaml`
- `design/variable_catalog.yaml`
- `design/variable_group_catalog.yaml`
- `design/artifact_catalog.yaml`
- `design/playbook_projection.yaml`
- `design/DATA_FLOW_PACKAGE.zip`

## Non-negotiable rule

The published files are never edited directly. Their upstream hashes point to `authoring/`; stale or divergent publication blocks PRE_EDITOR.
