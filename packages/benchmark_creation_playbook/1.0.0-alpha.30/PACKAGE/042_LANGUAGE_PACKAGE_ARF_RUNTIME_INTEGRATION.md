# BL-BENCH-042 — Mandatory Language Package and ARF Runtime Integration

**Status:** DONE  
**Target:** post-alpha improvement

## Problem

Recent iterations used principles derived from the Ordo language package and ARF, but did not execute the current language package and the applicable ARF playbook as the mandatory meta-runtime for creating, patching and validating this benchmark playbook. Manual Python/YAML patching could therefore pass local checks without proving conformance to the same end-to-end process expected externally.

## Required behavior

Every create, modify, validate and release operation must:

1. Load and checksum the explicitly selected current Ordo language package.
2. Record language, ARF and AEF baseline versions.
3. Select the applicable ARF meta-playbook for playbook creation or modification.
4. Execute its mandatory stages and preserve machine-readable ARF state.
5. Use package-provided validators, evidence capture, regression and release gates where applicable.
6. Bind every patch and release to the language-package and ARF versions used.
7. Fail closed with rollback/no-change when the package is missing, incompatible, corrupt or the required ARF route cannot be completed.
8. Distinguish package-derived validation from local supplemental checks.

## Required evidence

- `LANGUAGE_PACKAGE_BINDING.json`
- `ARF_PROCESS_SELECTION.json`
- `ARF_EXECUTION_STATE.json`
- `ARF_VALIDATION_EVIDENCE/`
- `ARF_RELEASE_GATE_REPORT.json`
- checksums and exact source lineage
- mapping from local validators to package/ARF validators

## Acceptance criteria

- A clean reference change completes through the selected ARF route.
- A missing or corrupted language package produces no mutation.
- An incompatible ARF version produces fail-closed disposition.
- A local-only patch cannot pass the release gate without ARF evidence.
- Scoped YAML verification remains mandatory and is invoked inside or after the ARF patch flow.
- The final evidence package proves which package functions, validators and gates were actually executed.

## Non-claim

Implemented in alpha.3. The release is bound to the selected language package and cannot pass without ARF evidence.


## Implemented runtime

- `tools/run_arf_meta_runtime.py`
- fail-closed package binding and version compatibility
- deterministic ARF route selection
- machine-readable execution state and validation evidence
- ARF release gate required in addition to local validation
- positive and negative acceptance tests
