# 18. Program-level Approval Gate Model

Status: `M64.3 docs/lint-profile design`

## 1. Purpose

The program-level approval gate defines how a package author, reviewer, or future linter should evaluate top-level process contracts before package handoff.

It applies to the M64 convention blocks:

```text
program_contract
interaction_model
process_rail
conversation_semantics
program_level_approval_gate
```

The gate answers:

```text
Is the program-level contract complete enough for the selected package profile?
If not, are the findings errors, warnings, or informational notes?
Can the package be approved, approved with warnings, blocked, or marked not applicable?
```

## 2. Scope

In scope:

- approval gate documentation;
- lint/profile check taxonomy;
- severity levels;
- `light`, `standard`, and `strict` profile behavior;
- example source shape;
- schema convention for future tooling.

Out of scope:

- runtime-core behavior;
- compiler enforcement;
- CLI command implementation;
- new opcodes;
- deterministic classification of natural language;
- `FLOW.JOIN` or `SHARED.TAIL.REFERENCE` implementation.

## 3. Conceptual model

```text
source package
  → program_contract
  → interaction_model
  → process_rail
  → conversation_semantics
  → program_level_approval_gate
  → findings
  → approval decision
```

The approval gate is a reviewer/linter layer above the top-level source conventions. It does not change how nodes, gates, transitions, assertions, or output templates execute.

## 4. Profiles

| Profile | Use case | Default stance |
|---|---|---|
| `light` | drafts, examples, exploratory packages | advisory warnings |
| `standard` | reusable process packages, standard applied modules | required identity/authority checks, warnings for incomplete policy |
| `strict` | release-candidate/stable high-control packages | missing or unsafe policy is blocking |

## 5. Severity model

| Severity | Review behavior |
|---|---|
| `error` | blocks approval under the selected profile |
| `warning` | visible review issue; may allow `approved_with_warnings` |
| `info` | contextual note; does not affect readiness |

## 6. Required check families

### Identity and compatibility

Checks package identity, module identity, lifecycle, Ordo compatibility, and schema profile.

### Runtime profile and authority

Checks that human, AI, and CLI responsibilities are declared and do not contradict each other.

### Review and validation readiness

Checks that review points and validation commands are declared when the package claims reviewer or CLI support.

### Process rail safety

Checks deviation, resume, backtracking, invalidation, skip-ahead, and stale-answer policies.

### Conversation routing safety

Checks that declared input classes have routing actions and that unmatched input cannot silently mutate state.

## 7. Approval decision rules

Recommended default decision logic:

```text
if any error:
  decision = blocked
elif any warning:
  decision = approved_with_warnings
elif gate not applicable:
  decision = not_applicable
else:
  decision = approved
```

A package owner may define stricter behavior, but should not silently downgrade errors to warnings in release-candidate or strict profiles.

## 8. Relationship to go/no-go

This model does not replace `go-no-go`.

Program-level approval checks top-level package contract readiness. `go-no-go` checks broader package readiness, including generated artifacts, validation evidence, and release/handoff state.

Recommended order:

```text
program-level contract approval
  → artifact/package validation
  → consistency review
  → go-no-go
  → human final approval
```

## 9. Human ownership rule

If `interaction_model.decision_authority.final_release_decision` is `human`, no lint/profile result may claim final content approval.

The gate may say:

```text
program-level contract structurally approved
```

It must not say:

```text
package content approved by AI
```

unless that authority is explicitly declared and accepted by the package owner.

## 10. M64.3 non-change statement

M64.3 is design-only:

```text
no runtime-core changes
no compiler behavior changes
no CLI command changes
no new opcodes
no deterministic natural-language classifier
```
