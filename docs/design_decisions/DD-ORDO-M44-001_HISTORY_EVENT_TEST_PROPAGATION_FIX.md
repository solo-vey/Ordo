# DD-ORDO-M44-001 — History Event Test Propagation Fix

## Status

Accepted.

## Context

A real AI Ordo Developer run for `LU_CHANGE_CAPITAL` confirmed QA/test requirements during guided intake, but the generated Passport and Jira task did not contain explicit test sections. The issue was not only a gate gap: the guided questions, output templates and deterministic validation rules also needed targeted strengthening.

## Decision

Apply a focused fix to `packages/history_event_guided_intake` without redesigning the Ordo language or the whole package structure:

- add `N_TEST_STRATEGY_CONTRACT` after `N_QA_SCOPE`;
- add gates `G_TEST_STRATEGY_CONTRACT_PRESENT` and `G_TEST_PROPAGATION_REQUIRED`;
- use closed numbered options and path-specific recommendations for non-trivial intake questions;
- replace old three-output template set with four concrete review artifacts:
  - `01_HISTORY_EVENT_PASSPORT_<ALIAS>.md`;
  - `02_JIRA_TASK_<ALIAS>.md`;
  - `04_IMPLEMENTATION_PROMPT_<ALIAS>.md`;
  - `05_QA_PACKAGE_<ALIAS>.md`;
- require test sections in Passport/Jira/Implementation Prompt/QA Package;
- make `ordo validate-output` deterministically fail if required test propagation sections are missing.

## Result

The History Event guided intake package now propagates confirmed QA/test requirements into all key review artifacts instead of leaving them only in the QA package.

## Non-goals

- No full rewrite of Ordo language.
- No replacement of the Process Rail model.
- No rebuild of all output templates.
- No change to the A1 business flow semantics.
