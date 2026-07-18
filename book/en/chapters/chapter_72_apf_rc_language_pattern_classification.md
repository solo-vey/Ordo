# Chapter 72. APF rc.1: Language Pattern Classification

M63.3 records an important boundary: APF `v0.1.0-rc.1` is already a standard applied module, but its internal patterns do not automatically become part of the language core.

APF demonstrates many useful ideas: input policy, progressive tree authoring, node/branch/subtree review, terminal output binding, template recipe, mock render, and the validation handoff tail. For release-candidate integration, however, they remain APF-local, documentation/schema patterns, or future tooling candidates.

The strongest candidates for a future IR decision are `FLOW.JOIN` and `SHARED.TAIL.REFERENCE`. They are kept in the backlog because they need separate stable semantics for source YAML and Semantic JSON IR.

This allows APF rc.1 to be accepted without a breaking migration: the module is already useful as an applied process, while core runtime is not changed in haste.
