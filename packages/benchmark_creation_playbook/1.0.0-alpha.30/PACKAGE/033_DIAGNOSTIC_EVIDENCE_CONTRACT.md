# 033. Diagnostic Evidence Contract

**Backlog:** `BL-BENCH-033`  
**Status:** implemented  
**Version:** `1.0.0`

## Purpose

Define how diagnostic claims are corroborated. Executor testimony is a causal hypothesis and evidence of model reasoning, not proof that a component caused the defect.

## Evidence hierarchy

Highest-trust evidence is direct and immutable:

1. checksum-bound source package and manifests;
2. append-only execution log and terminal disposition;
3. exact generated artifact versions;
4. active prompt, template, contract, Driver and validator versions;
5. evaluator reports and applied caps;
6. deterministic structural/semantic diffs;
7. executor diagnostic response;
8. analyst inference without direct evidence.

Lower-trust evidence cannot override contradictory higher-trust evidence without an explicit conflict record.

## Diagnostic claim model

Every claim contains:

- stable `claim_id`;
- claim text;
- proposed root-cause class;
- supporting evidence pointers;
- contradicting evidence pointers;
- evidence coverage status;
- confidence;
- corroboration status;
- reviewer decision.

Allowed corroboration statuses:

- `confirmed`;
- `probable`;
- `plausible`;
- `unsupported`;
- `contradicted`;
- `insufficient-evidence`.

Only `confirmed` and `probable` claims may drive an automatic improvement proposal. `plausible` claims require human review. Unsupported or contradicted claims cannot be used as closure evidence.

## Required triangulation

A causal claim should normally connect at least two independent evidence families, for example:

- executor explanation + execution log;
- artifact defect + template omission;
- wrong route + Driver binding/transition evidence;
- missed defect + validator/gate configuration;
- variant divergence + lineage and compiler records.

Single-source diagnosis must be marked `single-source` and cannot be `confirmed` unless the source is a deterministic proof artifact.

## Counterfactual test

For a root-cause claim, record the counterfactual:

> If the proposed component were corrected while other frozen inputs remained unchanged, would the defect reasonably disappear?

The answer is `yes`, `no`, or `unknown`, with evidence. A `no` result rejects the proposed primary cause.

## Diagnostic package

A completed case contains:

- request;
- executor response;
- evidence index;
- claim assessment;
- root-cause decision;
- unresolved alternatives;
- recommended patch target;
- regression implications.

Use `templates/DIAGNOSTIC_CASE.template.json` and `schemas/diagnostic_case.schema.json`.

## Gate

Diagnosis is ready only if evidence is frozen, claims are traceable, contradictions are visible, uncertainty is retained, and the primary cause is not based solely on executor self-report.
