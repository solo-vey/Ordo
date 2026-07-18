# Implementation Prompt — {{ state.event_alias }}

> Generated from Ordo template `IMPLEMENTATION_PROMPT`.

You are implementing a HistoryEvent analytical package for `{{ state.event_alias }}`.

## Business event

- UA: {{ state.display_name_uk }}
- EN: {{ state.display_name_en }}
- Path: `{{ state.selected_path }}`
- Source field(s): `{{ state.source_field }}`

## Required behavior

{{ state.value_semantics | bullets }}

## Required tests

Confirmed test strategy:

{{ state.test_strategy_contract | bullets }}

Test coverage level: `{{ state.test_coverage_level }}`

Manual QA coverage:

{{ state.manual_qa_coverage | bullets }}

Functional test coverage:

{{ state.functional_test_coverage | bullets }}

Unit test coverage:

{{ state.unit_test_coverage | bullets }}

## Test documentation requirement

- {{ state.test_documentation_requirement }}

## Deterministic implementation rules

- Do not implement only the happy path.
- Do not leave confirmed test requirements only in the QA document.
- Propagate confirmed test requirements into code-level tests, Jira acceptance criteria, and implementation handoff.
- Rollback instructions are only for technical restoration of current state.
