# 034. Root Cause Classification

**Backlog:** `BL-BENCH-034`  
**Status:** implemented  
**Version:** `1.0.0`

## Purpose

Provide a stable taxonomy for causal findings and select the narrowest responsible component for a future patch.

## Canonical root-cause classes

| Code | Class | Typical evidence |
|---|---|---|
| `RC-PLAYBOOK-NODE` | Playbook node or transition | wrong/missing node, branch, obligation or terminal transition |
| `RC-PROMPT` | Prompt/instruction defect | prompt omits, distorts or contradicts an active contract |
| `RC-TEMPLATE` | Template defect | required field/section/source mapping absent or ambiguous |
| `RC-DRIVER` | Driver behavior or binding | wrong Driver, disclosure timing, transition or correction handling |
| `RC-RUNTIME-CONTRACT` | Runtime/launcher/logging contract | preflight, logging, version binding or terminal disposition defect |
| `RC-SOURCE-EVIDENCE` | Source or fixture defect | missing, stale, contradictory or contaminated source evidence |
| `RC-COMPILER-LINEAGE` | Package compiler or lineage defect | semantic loss, contamination or wrong source lineage |
| `RC-RENDERING` | Rendering/materialization defect | canonical state correct but final rendered artifact wrong |
| `RC-VALIDATOR-GATE` | Validator or gate defect | defect should have been blocked but rule/check was absent or misbound |
| `RC-EVALUATOR-CONTRACT` | Evaluation contract defect | wrong artifact contract, cap, criterion or scoring interpretation |
| `RC-PACKAGING` | Package assembly defect | missing/wrong file, stale all-in-one, checksum or manifest issue |
| `RC-RESULT-REGISTRY` | Registry/comparison defect | wrong identity, supersession, cohort or matrix construction |
| `RC-HUMAN-DECISION` | Explicit human decision/override | accepted exception or incorrect manual decision with evidence |
| `RC-MULTI-FACTOR` | Multiple necessary causes | no single cause explains the failure; contributing causes are explicit |
| `RC-UNKNOWN` | Insufficient evidence | investigation cannot support a responsible component |

## Primary and contributing causes

Each diagnostic case has at most one `primary_root_cause`. Additional necessary or amplifying factors are `contributing_causes`. `RC-MULTI-FACTOR` is used only when removing one factor alone would not prevent the defect.

## Classification rules

1. Classify the earliest verified point where the defect became inevitable.
2. Do not classify the visible artifact alone when an upstream contract caused it.
3. Do not blame the executor when the active prompt/template mandated the faulty behavior.
4. Use `RC-VALIDATOR-GATE` as primary only when generation may be imperfect by design but the missing gate is the contractual prevention mechanism.
5. Use `RC-EVALUATOR-CONTRACT` when the artifact is acceptable under its real role but was scored with unsuitable criteria.
6. Use `RC-UNKNOWN` rather than inventing causality.

## Severity and recurrence dimensions

Root-cause records also classify:

- impact: `critical | major | moderate | minor`;
- recurrence: `systemic | variant-specific | run-specific | one-off | unknown`;
- affected layer: `authoring | compilation | execution | evaluation | registry | handoff`;
- patch locality: exact component/file/node IDs where known.

## Machine-readable registry

`ROOT_CAUSE_CLASSIFICATION.yaml` is the canonical taxonomy registry. Changes require versioning and a design decision if they alter historical interpretation.

## Gate

A classification is complete only when the chosen class is evidence-backed, alternatives are recorded, primary/contributing roles are explicit, and the patch target is no broader than the evidence supports.
