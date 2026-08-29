# alpha.20.0.49-dev — declared post-commit rematerialization

R3 generic runtime fix.

- Model nodes with a declarative `rematerialization` contract now rematerialize
  the declared artifact from POST-COMMIT state.
- Materialized artifact lineage records the post-commit revision.
- Artifact dependency extraction now reads the canonical package key
  `semantic_plan` (not the nonexistent `runtime_semantic_plan` alias).
- No playbook/domain-specific identifiers are interpreted by the Editor.
- Permanent regressions cover post-commit rematerialization and semantic-plan
  dependency extraction.
