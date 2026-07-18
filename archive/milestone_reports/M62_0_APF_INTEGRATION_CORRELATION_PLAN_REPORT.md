# M62.0 — APF Integration Correlation Plan Report

Status: `passed-design-docs-only`

## Summary

M62.0 starts the APF integration line after M61 Companion Utilities Line Closure. It correlates APF alpha.14 with the current M61 package and establishes the safe import strategy.

## Result

APF should be integrated as a **standard applied module**, not as runtime core and not as a companion utility.

Planned import path:

```text
packages/ordo_applied_project_factory/
```

## Added documents

- `APF_INTEGRATION_CORRELATION_PLAN.md`
- `STANDARD_APPLIED_MODULES.md`
- `APF_LANGUAGE_PATTERN_CANDIDATES.md`
- `docs/apf_integration_correlation_plan.md`
- `docs/standard_applied_modules.md`
- book chapter 66: APF integration correlation plan

## APF facts checked

| Check | Result |
|---|---|
| APF source YAML parse | passed |
| APF module id | `ordo.applied_project_factory` |
| APF version | `0.1.0-alpha.14` |
| APF nodes | `54` |
| APF gates | `38` |
| APF alpha.14 validation status | `passed_minimal_validation` |
| APF present in older full workspace branch | `True` |

## Validation

- Workspace `py_compile`: passed.
- Selected non-runtime PathWalk + Visual Graph tests: passed.
- APF alpha.14 `source/program.ordo.yaml` YAML parse: passed.
- APF alpha.14 validation report inspected: `passed_minimal_validation`.
- Book manifest sanity: passed.
- Zip extraction check: passed.

## Explicit non-goals

- APF code/package was not imported into the current workspace in M62.0.
- Runtime core was not changed.
- PathWalk and Visual Graph behavior was not changed.
- No APF source YAML rewrite.
- No formal IR/opcode addition.
- No runtime execution/scoring/calibration.

## Next step

Proceed to **M62.1 — APF Package Import into Current Language Package**.

## Final validation summary

- workspace `py_compile`: passed;
- selected non-runtime PathWalk + Visual Graph tests: `27 passed`;
- APF alpha.14 YAML parse: passed;
- APF alpha.14 minimal validation report inspected: `passed_minimal_validation`;
- Visual Graph `.mmd` and `.svg` smoke: passed;
- PathWalk graph → paths → clean-cases → noise-cases → review-cards smoke: passed, `15` cards;
- PathWalk RC + developer bundle smoke: passed;
- book manifest sanity: passed.
