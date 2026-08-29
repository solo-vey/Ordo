# Program-level Contract Value Registry

Status: `M64.1 registry convention`

This registry explains common values used by `program_contract`. It is documentation-first in M64.1.

## lifecycle

| Value | Meaning |
|---|---|
| `draft` | Working draft. Behavior may change frequently. |
| `alpha` | Early implementation. Useful for internal testing, not release-ready. |
| `beta` | Broad review candidate. Major workflow exists, but blockers may remain. |
| `release-candidate` | Candidate release. Known limitations must be explicit and non-blocking. |
| `stable` | Accepted stable release. Breaking changes require migration notes. |
| `deprecated` | Retained for history/compatibility, not recommended for new use. |

## control_level

| Value | Meaning |
|---|---|
| `light` | Minimal formal control; suitable for exploratory packages. |
| `standard` | Normal Ordo control: state, gates, review points, and validation are expected. |
| `strict` | High-control package. Missing gates/review/validation may become blockers. |

## execution_mode

| Value | Meaning |
|---|---|
| `full_runtime` | Intended to run as a guided runtime package. |
| `chat_internal` | Intended for disciplined chat execution, but not full runtime packaging. |
| `freeform_only` | Documentation/freeform process; no deterministic runtime claim. |
| `dry_run` | Non-mutating rehearsal or validation. |
| `test` | Fixture/test-oriented execution profile. |

## contract_profile

| Value | Meaning |
|---|---|
| `basic_process` | Small Ordo process with minimal program-level metadata. |
| `standard_applied_module` | Reusable applied module included in a language package. |
| `runtime_package` | Package intended for runtime handoff/execution. |
| `companion_utility_workflow` | Utility-oriented route for artifacts, graphs, tests, or review outputs. |

Unknown values are not automatically invalid in M64.1, but package-local values must be documented.
