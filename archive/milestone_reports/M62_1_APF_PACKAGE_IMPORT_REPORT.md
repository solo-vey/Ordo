# M62.1 — APF Package Import into Current Language Package

Status: `passed-package-import`  
Date: 2026-07-08

## Summary

APF `v0.1.0-alpha.14` has been imported into the current Ordo language package as a standard applied module under:

```text
packages/ordo_applied_project_factory/
```

This is a controlled package import. It does not change Ordo runtime-core semantics, scoring, calibration, benchmark orchestration, or formal IR/opcodes.

## Imported APF contents

The import preserves the standalone APF package structure:

```text
packages/ordo_applied_project_factory/
  source/program.ordo.yaml
  compiled/program.ir.json
  compiled/program.ordo.view
  output_templates/
  docs/
  tests/
  run_inputs/
  runtime/
  reports/
  generated_outputs/
  README.md
  VERSION.md
  MODULE_CHANGELOG.md
  ORDO_PARENT_PACKAGE_IMPORT.md
```

The language improvement handoff document was also copied into APF docs as:

```text
packages/ordo_applied_project_factory/docs/LANGUAGE_MODEL_IMPROVEMENTS_PACKAGE.md
```

## APF graph snapshot after import

```text
nodes: 54
edges: 78
gates: 38
assertions: 28
outputs: 1
source_sha256: dbeb51f58b19a1048146f9714a523213b0b61c99cbbc1ba1aed75c85b366e14a
```

## Current CLI compatibility

```text
lint: passed
compile: passed
static test: passed
```

APF alpha.14 still treats full validation as deferred by design. M62.1 does not claim full validation or APF human-review closure.

## Documentation sync

A current-package import note was added. The high-level README mode list was synced to reflect the APF alpha.14 fourth startup mode:

```text
4. Коригування існуючого процесу
```

The source YAML branch logic was not rewritten.

## Smoke checks

- workspace `py_compile`: passed;
- selected PathWalk + Visual Graph pytest: `33 passed`;
- APF current CLI lint / compile / static test: passed;
- Visual Graph APF `.mmd` smoke: passed;
- Visual Graph APF focused `.svg` smoke: passed;
- PathWalk APF `real-module-graph` smoke: passed;
- developer bundle APF lint / compile / static test: passed;
- PathWalk RC selected pytest: `27 passed`;
- book manifest sanity: passed.

## Explicit non-goals

- no APF branch 1/2 rewrite;
- no terminal output binding patch;
- no APF review closure claim;
- no formal language opcode/IR additions;
- no runtime execution/scoring/calibration;
- no PathWalk/Visual Graph/APF merge.

## Next recommended milestone

`M62.2 — APF Documentation and Book Section`.
