# Source-to-template mapping

The reusable lifecycle is represented by the following generic nodes and gates.

| Source element | Template element |
|---|---|
| `N_IMPLEMENTATION_EVIDENCE_INTAKE` | `N_{{id_prefix}}_EVIDENCE_INTAKE` |
| `G_IMPLEMENTATION_EVIDENCE_READINESS` | `G_{{id_prefix}}_EVIDENCE_READY` |
| `N_IMPLEMENTATION_CHANGE_SCOPE_ASSESSMENT` | `N_{{id_prefix}}_SCOPE_ASSESSMENT` |
| `G_IMPLEMENTATION_CHANGE_SCOPE` | `G_{{id_prefix}}_SCOPE_READY` |
| `N_IMPLEMENTATION_PROMPT_SYNC` | `N_{{id_prefix}}_PROMPT_SYNC` |
| `N_IMPLEMENTATION_EXECUTION_MODE_DECISION` | `N_{{id_prefix}}_EXECUTION_MODE` |
| `N_MODEL_DIRECT_CHANGE_APPLICATION` | `N_{{id_prefix}}_DIRECT_CHANGE` |
| `N_MODEL_DIRECT_CHANGE_VALIDATION` | `N_{{id_prefix}}_DIRECT_CHANGE_VALIDATE` |
| `G_IMPLEMENTATION_CANDIDATE_READINESS` | `G_{{id_prefix}}_CANDIDATE_READY` |
| `N_IMPLEMENTATION_VERIFICATION` | `N_{{id_prefix}}_VERIFY` |
| `G_IMPLEMENTATION_VERIFICATION` | `G_{{id_prefix}}_VERIFICATION` |
| `N_IMPLEMENTATION_VERIFICATION_REVIEW` | `N_{{id_prefix}}_VERIFICATION_REVIEW` |
| `N_IMPLEMENTATION_EVIDENCE_CLARIFICATION` | `N_{{id_prefix}}_EVIDENCE_CLARIFICATION` |
| `N_DEVELOPER_HANDOFF_FORMATION` | `N_{{id_prefix}}_DEVELOPER_HANDOFF` |

Host-specific package synchronization, URLs, artifact names, and final package
gates are intentionally excluded from the reusable module.
