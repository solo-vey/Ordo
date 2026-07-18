# 15. Contract → Artifact Coverage Model

## Status

M46.1 formalizes the language-level model for checking whether confirmed process contracts actually reach generated artifacts. This is a specification layer first: later CLI milestones can implement `validate-artifacts`, `consistency`, and `go-no-go` on top of it.

## Problem

A guided intake can correctly confirm contracts in conversation and still produce incomplete artifacts. For example, a test strategy can be confirmed but appear only in the QA package and not in the Passport or Jira task. In Ordo terms, this is a broken propagation path:

```text
confirmed contract → expected artifact coverage → rendered artifact
```

The package is not trustworthy if this path is not explicit and checkable.

## Core pipeline

The M46 coverage model adds a standard pipeline:

```text
confirmed contracts
→ artifact requirements
→ rendered artifacts
→ deterministic validation
→ consistency report
→ go/no-go decision
```

This pipeline does not replace Process Rail. It extends it: Process Rail controls the route, while artifact coverage checks whether the route's decisions were preserved in the outputs.

## Contract

A `contract` is a structured set of values that has been collected, proposed, confirmed, blocked, or marked as not applicable during an Ordo process.

A contract is not only a conversation note. It is a validation object.

Allowed contract field statuses:

```text
missing
candidate
proposed
confirmed
blocked
not_applicable
```

Minimal IR shape:

```json
{
  "kind": "contract",
  "id": "G_EVENT_IDENTITY_CONTRACT",
  "status": "confirmed",
  "fields": {
    "alias": {
      "value": "LU_CHANGE_CAPITAL",
      "status": "confirmed",
      "required": true
    },
    "name_uk": {
      "value": "Зміна статутного капіталу компанії",
      "status": "confirmed",
      "required": true
    },
    "name_en": {
      "value": "Company capital changed",
      "status": "confirmed",
      "required": true
    }
  }
}
```

## Artifact

An `artifact` is a declared generated output target. It can be markdown, JSON, YAML, or another structured document.

Example:

```json
{
  "kind": "artifact",
  "id": "01_HISTORY_EVENT_PASSPORT",
  "path_pattern": "01_HISTORY_EVENT_PASSPORT_<ALIAS>.md",
  "format": "markdown",
  "required": true
}
```

## Artifact requirement

An `artifact_requirement` declares where confirmed contract fields must appear.

Example:

```json
{
  "kind": "artifact_requirement",
  "id": "REQ_HISTORY_EVENT_OUTPUT_IN_PASSPORT_AND_JIRA",
  "when": {
    "contract": "G_HISTORY_EVENT_OUTPUT_CONTRACT",
    "status": "confirmed"
  },
  "requires": [
    {
      "artifact": "01_HISTORY_EVENT_PASSPORT",
      "must_include_fields": [
        "type",
        "sub_type",
        "source",
        "group",
        "groupPriority",
        "isEdr",
        "deleted",
        "item.values"
      ]
    },
    {
      "artifact": "02_JIRA_TASK",
      "must_include_fields": [
        "type",
        "sub_type",
        "source",
        "group",
        "groupPriority",
        "isEdr",
        "deleted",
        "item.values"
      ]
    }
  ]
}
```

## Coverage rule

A `coverage_rule` describes a deterministic check over contracts and artifact requirements.

Example:

```json
{
  "kind": "coverage_rule",
  "id": "COVERAGE_CONFIRMED_CONTRACTS_TO_ARTIFACTS",
  "input": "confirmed_contracts",
  "output": "artifact_requirements",
  "failure_policy": "no_go"
}
```

A confirmed contract without artifact requirements is a coverage gap.

## Rendered artifact assertion

A `rendered_artifact_assertion` checks generated files after rendering, not only templates.

Example:

```json
{
  "kind": "rendered_artifact_assertion",
  "id": "ASSERT_ALIAS_RENDERED_EVERYWHERE",
  "field": "G_EVENT_IDENTITY_CONTRACT.alias",
  "must_appear_in": [
    "README.md",
    "01_HISTORY_EVENT_PASSPORT_<ALIAS>.md",
    "02_JIRA_TASK_<ALIAS>.md",
    "04_IMPLEMENTATION_PROMPT_<ALIAS>.md",
    "05_QA_PACKAGE_<ALIAS>.md",
    "SUMMARY.json",
    "VALIDATION_REPORT.json",
    "CONSISTENCY_CHECK_REPORT.json"
  ]
}
```

## Go/no-go decision

`go_no_go` is the standard machine-readable release or draft decision object.

```json
{
  "kind": "go_no_go",
  "status": "no_go_requires_artifact_fix",
  "blocking_issues": [
    {
      "code": "ORDO-COV-002",
      "message": "Confirmed contract field G_HISTORY_EVENT_OUTPUT_CONTRACT.group is missing from 01_HISTORY_EVENT_PASSPORT"
    }
  ],
  "warnings": []
}
```

Allowed statuses:

```text
go
no_go_requires_confirmation
no_go_requires_artifact_fix
no_go_requires_template_fix
no_go_requires_runner_contract
```

## Required deterministic errors

M46 reserves these error codes for the coverage layer:

| Code | Meaning |
|---|---|
| `ORDO-COV-001` | Confirmed contract has no artifact mapping. |
| `ORDO-COV-002` | Confirmed contract field missing from required artifact. |
| `ORDO-COV-003` | Artifact contains confirmed value that was only candidate/proposed in state. |
| `ORDO-COV-004` | Generated artifacts disagree on the same contract field. |
| `ORDO-COV-005` | Required gate skipped before draft package. |
| `ORDO-COV-006` | Required gate skipped before final package. |
| `ORDO-COV-007` | Normalization contract does not cover all event-impact fields. |
| `ORDO-COV-008` | HistoryEvent output contract missing required fields. |
| `ORDO-COV-009` | Test strategy confirmed but missing from Passport or Jira. |
| `ORDO-COV-010` | Unit tests required but test class markdown documentation not mentioned. |

## Compile-time vs rendered artifact checks

`compile` can check references and structure:

```text
contract ids exist
artifact ids exist
artifact requirements point to known contracts and artifacts
field names are syntactically valid
```

`compile` cannot prove that a generated Markdown document contains the required contract value. That belongs to `validate-artifacts`.

## Relationship to CLI helper commands

This spec prepares the following helper commands:

```text
ordo coverage
ordo validate-artifacts
ordo consistency
ordo go-no-go
```

M46.1 only defines the language/IR model. Runtime behavior is implemented in later M46 slices.
