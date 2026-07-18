# Program-level Approval Gate Model

Status: `M64.3 accepted-docs-lint-profile-design`

M64.3 defines the **program-level approval gate** as a documentation and lint/profile design layer for packages that declare `program_contract`, `interaction_model`, `process_rail`, and `conversation_semantics`.

It is not a new opcode, not a runtime-core feature, not a compiler behavior change, and not a CLI command. It describes how future linters, validators, reviewers, and package authors should decide whether a program-level package contract is ready for handoff.

```text
program-level approval gate
  → checks that top-level process contracts are present enough for the package profile
  → classifies findings as error / warning / info
  → applies light / standard / strict profile behavior
  → produces an approval decision for human review
```

## Why this layer exists

M64.1 made the package-level execution contract explicit through `program_contract`. M64.2 added the supporting conversational policy conventions: `interaction_model`, `process_rail`, and `conversation_semantics`.

M64.3 connects those conventions into a reviewable approval layer. The goal is to prevent a package from claiming to be a standard applied module, strict runtime process, or deterministic validator-backed package while leaving the key decision, routing, resume, validation, and human-approval rules ambiguous.

## Canonical source shape

A package may declare an approval policy at the top level of `source/program.ordo.yaml`:

```yaml
program_level_approval_gate:
  gate_id: program_level_contract_approval
  applies_to:
    - program_contract
    - interaction_model
    - process_rail
    - conversation_semantics
  profile: standard
  severity_policy:
    missing_required_contract: error
    missing_recommended_contract: warning
    incomplete_routing_rule: warning
    unsafe_authority_claim: error
    undocumented_profile_value: warning
  required_checks:
    - program_contract_identity_present
    - runtime_profile_declared
    - human_final_approval_declared
    - validation_commands_declared
    - interaction_roles_consistent
    - process_rail_resume_policy_consistent
    - conversation_input_classes_routed
  approval_decision:
    allowed_values:
      - approved
      - approved_with_warnings
      - blocked
    default_on_error: blocked
    default_on_warning: approved_with_warnings
```

This block is optional as source syntax during M64.3. Its semantics are documented so future lint/profile implementations can converge on a common model.

## Approval gate does not replace human ownership

The approval gate can decide whether the top-level contract is structurally ready for review. It must not silently approve content decisions that the package assigns to a human.

Recommended rule:

```text
The gate may approve contract completeness. It may not approve business/content decisions unless the program contract explicitly delegates that authority.
```

## Relationship to M64.1 and M64.2

| Source block | What M64.3 checks |
|---|---|
| `program_contract` | identity, lifecycle, control level, execution mode, runtime profile, review points, validation expectations |
| `interaction_model` | human/AI/CLI roles, decision authority, raw tool output policy, review point consistency |
| `process_rail` | state tracking, deviation policy, resume policy, backtracking invalidation and stale-answer rules |
| `conversation_semantics` | declared input classes, routing rules, unmatched-input policy, clarification behavior, resume consistency |

## Finding severity levels

### `error`

A finding that blocks approval for the selected profile.

Examples:

- `program_contract` is missing for a strict or standard applied module profile.
- `final_release_decision` is assigned only to `ai` without explicit package policy.
- `allow_deviation: true` but no resume policy exists under strict profile.
- an input class is declared but no routing rule exists under strict profile.

### `warning`

A finding that should be reviewed before handoff but does not necessarily block the package.

Examples:

- lifecycle is missing from a draft/basic process package.
- validation commands are incomplete for a light profile.
- a package-local routing action is used without enough explanation.
- a recommended review point is absent.

### `info`

A non-blocking observation that helps the reviewer understand the package state.

Examples:

- optional `process_rail` field omitted because deviations are disabled.
- legacy package has no M64 contract blocks but is explicitly outside migration scope.
- package declares docs-only compatibility with no runtime enforcement.

## Approval decisions

| Decision | Meaning |
|---|---|
| `approved` | Required checks for the selected profile passed with no blocking findings. |
| `approved_with_warnings` | No errors, but warnings remain visible for owner review. |
| `blocked` | At least one profile-blocking error exists. |
| `not_applicable` | Package is out of scope for this gate, usually because it is a legacy/static artifact or a non-process companion utility. |

## Required review output shape

Future tools or manual review reports should produce a compact report:

```json
{
  "gate": "program_level_contract_approval",
  "profile": "standard",
  "decision": "approved_with_warnings",
  "findings": [
    {
      "severity": "warning",
      "check": "validation_commands_declared",
      "message": "Package declares CLI validator role but lists only lint and compile."
    }
  ],
  "non_changes": [
    "no runtime-core behavior changed",
    "no CLI command added",
    "no opcode added"
  ]
}
```

## Typical mistakes

- Treating an approval gate as a runtime opcode.
- Treating a lint warning as content approval.
- Claiming strict profile while leaving input routing ambiguous.
- Letting AI approve final release when `interaction_model` assigns final release decision to human.
- Hiding warnings in the final package instead of surfacing them in validation reports.
