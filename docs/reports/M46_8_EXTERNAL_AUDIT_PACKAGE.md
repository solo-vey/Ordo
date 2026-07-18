# M46.8 External Audit Package

M46.8 adds a reviewer-facing audit prompt and checklist for independent pre-release validation. It does not add new language semantics, CLI runtime behavior, or business package logic.

## Purpose

The goal is to make external review repeatable and evidence-based:

```text
archive contents → commands actually run → generated artifacts checked → consistency/go-no-go verified → audit verdict
```

The audit package is intentionally skeptical of self-reported validation files. Reviewers are instructed to verify the package by inspecting files and running commands where tools are available.

## Added materials

- `docs/external_audit/EXTERNAL_AUDIT_PROMPT_M46_8.md`
- `docs/external_audit/PRE_RELEASE_AUDIT_CHECKLIST_M46_8.md`
- `docs/reports/M46_8_EXTERNAL_AUDIT_PACKAGE.md`
- `docs/design_decisions/DD-ORDO-M46-008_EXTERNAL_AUDIT_PACKAGE.md`
- `book/source/chapters/chapter_42_external_audit_pre_release.md`

## Scope boundary

M46.8 does not claim live AI execution, REST integration, Mongo validation, or production business runtime validation. It validates the pre-release package as a source-available Ordo workspace with deterministic helper checks.

## Expected external-audit outcome

A fresh reviewer should be able to answer:

- Does the archive structure match the lean pre-release scope?
- Does CLI install and pass baseline checks?
- Do active packages pass lint/compile/test/coverage?
- Does History Event regression validate generated artifacts, consistency, and go/no-go?
- Are M46 language/CLI/book docs aligned with implemented behavior?
- Are release limitations honest?

