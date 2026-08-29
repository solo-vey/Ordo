# alpha.20.0.73-dev — model explanation layer

Generic Explorer capability.

- Added `Explanation` tab for every inspectable node/output.
- Explanation is empty by default and generated only by explicit `Explain with model`.
- Explanation calls are read-only: no execution state, revision, pointer, or run history mutation.
- Python package references expose `Explain with model` in addition to source preview.
- Explanations use the playbook interaction language.
- Global Model Settings are available before a playbook run, including on the initial screen.
- Compiler fallback language inference samples analyst-facing prose across nodes/gates; explicit interaction_model remains authoritative.

No domain-specific semantics are embedded in Editor/Compiler.
