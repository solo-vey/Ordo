# Production Repository Root Classification Matrix

Status: `M70.0 design baseline`

| Root ID | Path | Role | Exists | Has root `ordo.yml` | Current clean-check treatment | Future enforcement path |
|---|---|---|---:|---:|---|---|
| `language_core` | `language/` | `language_core` | yes | no | `not_applicable` | language-root repo checks |
| `cli_core` | `cli/` | `cli_utility` | yes | no | `not_applicable` | CLI-root repo checks |
| `canonical_cli_example` | `cli/examples/history_event_guided_intake/` | `example_package` | yes | yes | `optional` | existing clean-check |
| `applied_packages` | `packages/` | `applied_packages` | yes | mixed children | `delegated` | package-local opt-in |
| `companion_utilities` | `utilities/` | `companion_utility` | yes | no | `not_applicable` | utility-specific checks |
| `pathwalk_utility` | `utilities/ordo_pathwalk/` | `companion_utility` | yes | no | `not_applicable` | Python utility checks |
| `book_area` | `book/` | `book_or_docs` | yes | no | `not_applicable` | publication checks |
| `docs_area` | `docs/` | `book_or_docs` | yes | no | `not_applicable` | docs/link/schema checks |
| `workflow_area` | `.github/` | `workflow_area` | yes | no | `ignored` | existing workflow path checks |
| `reports_area` | `reports/` | `generated_artifact_area` | yes | no | `ignored` | generated metadata checks |

## Acceptance rule

A root may become `required` only when its declared checker is compatible with the root and has real fixtures proving pass, warning and blocked behavior.
