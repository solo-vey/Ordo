# M68.3 — Repo-Level Package Hygiene Design Report

Status: `accepted-design / passed-scope-validation`

## Summary

M68.3 defines repo-level package hygiene as a policy and aggregation layer above package-level `ordo clean-check`.

Preferred future integration:

```bash
ordo repo-check <repo> --clean
```

No implementation code was changed in this milestone.

## Added

- `cli/docs/REPO_LEVEL_PACKAGE_HYGIENE_DESIGN.md`
- `language/spec/27_REPO_LEVEL_PACKAGE_HYGIENE_MODEL.md`
- `docs/design_decisions/DD-ORDO-M68-002_REPO_LEVEL_PACKAGE_HYGIENE_DESIGN.md`
- `M68_3_REPO_LEVEL_PACKAGE_HYGIENE_DESIGN_REPORT.md`
- `M68_3_REPO_LEVEL_PACKAGE_HYGIENE_DESIGN_REPORT.json`
- `M68_3_VALIDATION_REPORT.json`
- `language/improvement_intake/m68_3/*`

## Updated

- `cli/docs/REPO_LEVEL_PACKAGE_HYGIENE_PLAN.md`
- `cli/docs/CLEAN_CHECK_HARDENING_PLAN.md`
- `README.md`
- `CHANGELOG.md`
- `STABLE_PACKAGE_INDEX.md`
- `language/README.md`
- `language/CHANGELOG.md`
- `language/VALIDATION_REPORT.json`

## Scope guard

M68.3 does not modify:

- `packages/*`
- `cli/ordo/*.py`
- `cli/tests/*`
- runtime core
- compiler
- opcodes
- compiled IR
- lockfiles
- embedded CLI bundles

## Validation summary

- JSON reports parse: passed
- packages diff guard: passed
- CLI implementation diff guard: passed
- CLI tests diff guard: passed
- zip integrity: passed
