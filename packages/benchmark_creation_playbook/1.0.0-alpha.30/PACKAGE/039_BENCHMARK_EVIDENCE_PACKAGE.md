# 039 — Benchmark Evidence Package

## Purpose

Define the canonical, reproducible evidence bundle for a benchmark release, campaign, attempt, evaluation, diagnostic case, or improvement cycle.

## Core rule

A status claim is valid only when its evidence is materialized, checksum-bound, version-identified, and linked through a manifest. Chat history alone is not authoritative evidence.

## Required package layers

1. **Identity** — package ID, playbook version, creation timestamp, authority profile, scope and compatibility cohort.
2. **Source** — test case, RUN contract, package variant, Driver binding, prompts, templates, schemas and source checksums.
3. **Execution** — launch manifest, preflight report, append-only execution log, produced artifacts and terminal disposition.
4. **Evaluation** — process evaluation, artifact evaluations, failure caps, contract versions and focused-review evidence.
5. **Results** — immutable registry record, comparison eligibility, matrix high-water mark and supersession state.
6. **Diagnostics and improvement** — diagnostic cases, root-cause decision, patch records, diffs, regression selection and campaign outcome when applicable.
7. **Release integrity** — inventory, SHA-256 manifest, validation report, known limitations and unresolved backlog.

## Evidence states

- `PRESENT_VERIFIED`
- `PRESENT_UNVERIFIED`
- `NOT_APPLICABLE`
- `EXPECTED_MISSING`
- `QUARANTINED`
- `SUPERSEDED`

`EXPECTED_MISSING` blocks a complete evidence-package claim.

## Mandatory controls

- Every file has a stable relative path and SHA-256.
- Every derived artifact identifies its source versions.
- Hidden/evaluator-only material remains access-controlled in the package layout.
- No evidence file may be silently replaced; replacements create a new package version.
- Manifest and inventory must agree exactly.
- Known limitations and open backlog items are explicit.

## Canonical outputs

- `EVIDENCE_PACKAGE_POLICY.yaml`
- `templates/EVIDENCE_PACKAGE_MANIFEST.template.yaml`
- `schemas/evidence_package_manifest.schema.json`
- `EVIDENCE_PACKAGE_INDEX.md`

## Completion criteria

`BL-BENCH-039` is complete when the package contract, machine-readable policy, manifest template, schema, inventory rules and integrity checks exist and pass self-validation.
