# M74.6 — APF modularization

Status: implemented

The APF source is now maintained as eight responsibility modules under `source/modules/`.
`source/module_manifest.yaml` defines ownership and assembly order.
`tools/assemble_ordo_modules.py` deterministically assembles the compatibility target `source/program.ordo.yaml` and blocks duplicate or undeclared top-level keys.

The previous monolith is retained under `source/legacy/` only as the M74.5 equivalence reference.

Validation results:

- legacy and modular lint: passed;
- legacy and modular compile: passed;
- normalized Semantic JSON IR: equivalent;
- 407 operations on both sides;
- no added, removed, or changed operations;
- static tests: passed on both sides;
- pathwalk graph and terminal-path artifacts: equivalent.

The existing APF graph remains blocked for clean testcase generation because both versions report the same 4141 cycle edges and 2 dead-end paths. This is a pre-existing APF graph condition, not a modularization regression.
