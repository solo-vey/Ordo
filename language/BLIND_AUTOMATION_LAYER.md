# Blind Automation Layer

Status: accepted implementation for BL-ORDO-055 change bundle.

## Purpose

The Blind Automation Layer standardizes automated playbook testing when the execution model must not see expected answers, evaluator scores, prior run outcomes, developer conclusions, or hidden scenario data beyond what the Driver is allowed to disclose.

It separates five authorities:

1. the instruction package defines process behavior;
2. the hidden scenario owns authoritative test facts;
3. the Driver controls disclosure and terminal-state protocol;
4. the execution model performs the playbook and creates artifacts;
5. the external evaluator scores process execution and document quality after the run.

The execution model MUST NOT assign the authoritative score to its own output. Driver protocol compliance MUST NOT be treated as proof of document quality.

## Execution profiles

### `step_bound`

Use when the process has a canonical ordered step sequence. The Driver binds allowed disclosures and expected action classes to explicit step IDs. It MUST NOT skip mandatory gates or disclose future-step facts.

Required profile fields:

- `step_catalog` with stable IDs and order;
- `step_disclosure_bindings`;
- deterministic transitions;
- correction return targets;
- terminal gate requirements.

### `semantic_adaptive`

Use when the instruction source does not impose a fixed question order. The Driver classifies natural questions into neutral semantic intents and returns only minimal relevant confirmed facts.

Required profile fields:

- `intent_catalog`;
- cue and classification rules;
- compound-intent policy;
- ambiguity policy;
- over-disclosure guard;
- correction manager;
- terminal gate requirements.

The Driver MUST NOT invent a hidden step order or reveal facts merely because they may become useful later.

## Driver protocol

Allowed actions are `start`, `ask`, `answer`, `present`, `correction`, and `finish`.

- `start` initializes an isolated run and records package, fixture, Driver, and model identities.
- `ask` classifies the requested step or semantic intent.
- `answer` returns only facts allowed by the active disclosure policy.
- `present` registers a new artifact version, correction response, or approval decision.
- `correction` supersedes a confirmed fact and invalidates dependent artifacts and approvals.
- `finish` evaluates the terminal-state contract; it never silently repairs missing work.

## Fact lifecycle

Allowed states are `confirmed`, `tentative`, `withdrawn`, `superseded`, `unavailable`, and `irrelevant`.

Only `confirmed` facts may satisfy mandatory artifact or terminal requirements. A correction MUST preserve the previous value as an auditable superseded or withdrawn record.

## Artifact versioning and approval

Every generated artifact has a stable artifact ID and immutable version ID. Approval scope is exactly one artifact version. A later version does not inherit approval.

When an authoritative fact changes:

1. the old fact is superseded or withdrawn;
2. dependency rules mark affected artifact versions `stale`;
3. dependent approvals become `invalidated`;
4. only the affected chain must be regenerated;
5. a whole-run consistency review is still required;
6. `finish` remains blocked until fresh validation and approval complete.

## Terminal states

- `T_COMPLETED`: required facts, current artifacts, validations, and approvals are complete.
- `T_INPUT_BLOCKED`: a mandatory fact is unavailable and will not be supplied.
- `T_SCENARIO_EXHAUSTED`: remaining scenario facts cannot satisfy the target case.
- `NO_GO`: the package, fixture, Driver, runner, key, or protocol prevents a valid run.
- `not_ready`: a premature finish request; the run remains active.

A terminal state is protocol evidence, not a document-quality score.

## Evaluation separation

A benchmark SHOULD report at least two separate dimensions:

- process/instruction execution;
- generated-document quality.

The recommended default aggregation is 50/50, but the exact rubric is benchmark-owned. Evidence-capture quality belongs to the harness assessment, not the tested model's score.

## Causal diagnostic review

After independent evaluation identifies a concrete defect, the same execution model MAY receive a narrow diagnostic request to reconstruct the causal path of that output. The request MUST NOT ask for self-scoring or immediate repair.

For every investigated element, capture:

- source node;
- loaded prompt, template, and contract;
- confirmed facts and fixture inputs;
- invocation and assertions;
- gate path;
- blocker, generic fallback, or missing rule;
- suspected defect location: node, prompt, template, contract, Driver, runner, or validator.

A diagnostic statement has status `model_reported` until corroborated by trace, logs, package files, or deterministic reproduction. It MUST NOT alone close a defect.

## Improvement loop

1. Run a blind execution without self-scoring.
2. Independently evaluate process and documents.
3. Select one bounded defect.
4. Run causal diagnostic review.
5. Corroborate the model report with logs and files.
6. Patch the narrowest responsible component.
7. rebuild a new blind package;
8. rerun in a clean context;
9. compare with the prior run and record regression evidence.

## Minimum package contract

A conforming package includes README/profile declaration, canonical instruction source, hidden or encrypted fixtures, compatible Driver, protocol examples, terminal-state contract, templates, independent evaluator criteria, launch prompt, checksums, Driver smoke/regression tests, audit-log contract, and causal diagnostic prompt templates.
